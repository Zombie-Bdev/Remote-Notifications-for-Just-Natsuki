# HUGE Thanks to Zhaumbie for all the help getting this working,
# and to Wowm for helping with dialogue!

# This submods internal name is jn_zpn

#
# How to safely use jn_zpn notifications in your submod:
#
# This will confirm that jn_zpn has created it's namespace before attempting to call it's functions
# If players don't have jn_zpn installed, Ren'Py will simply skip over this code instead of crashing
#
#
# if "jn_zpn" in globals() and hasattr(jn_zpn, "send_ntfy_notification"):
#     $ jn_zpn.send_ntfy_notification("Your message here! [tease_emote]")
#
#
# Natsuki constantly uses emoticons while texting, use these in your message to grab a random emoticon
# They are already defined and randomized within jn_zpn
#
# [happy_emote]
# [angry_emote]
# [sad_emote]
# [tease_emote]
# [confused_emote]
#

default persistent._zombie_phone_notifications = {
    "player_ntfy_password": "none",
    "player_text_preference": False,
}

init -10 python in jn_zpn:
    """
    NOTE: Prefix functions with "jn_zpn."
    """

    import urllib2
    import threading
    import random
    import store
    import re

    # Function to push a notification to ntfy.sh given a password
    # This function is unthreaded and will freeze JN until a server response is received.
    # It also requires a password to send the message to
    # PLEASE PLEASE DO NOT USE TY
    def send_ntfy_notification_unthreaded(message, password):
        """
        NOTE: DO NOT USE THIS

        """

        try:
            urllib2.urlopen(
                urllib2.Request(
                    "https://ntfy.sh/" + password,
                    message.encode("utf-8")
                ),
                timeout=10
            ).close()

        except Exception as e:
            store.jn_utils.log("Error posting to ntfy servers. ", + str(e))

    # This is our async function that will prevent JN from freezing waiting for a server response
    # Creates a thread and calls the original function to push a notification to the players saved password
    # Please use this one
    def send_ntfy_notification(message):
        """
        Sends a push notification to the player through ntfy

        IN:
            message - string: The message you want to send the player
        """
        player_ntfy_password = store.persistent._zombie_phone_notifications.get("player_ntfy_password")
        player_text_preference = store.persistent._zombie_phone_notifications.get("player_text_preference")

        # Natsuki loves her emoticons while texting, especially at higher affinities.
        # She uses them like, every other text. So we define and randomize them here
        store.happy_emote = store.jn_utils.getRandomHappyEmoticon()
        store.angry_emote = store.jn_utils.getRandomAngryEmoticon()
        store.sad_emote = store.jn_utils.getRandomSadEmoticon()
        store.tease_emote = store.jn_utils.getRandomTeaseEmoticon()
        store.confused_emote = store.jn_utils.getRandomConfusedEmoticon()

        # As long as the players password isn't "none" and they want to be texted, we create a thread and send a message!
        # Turns out there was a built in threading class in JN already, oops...
        if not player_ntfy_password == "none" and player_text_preference == True:
            thread = threading.Thread(
                    target = send_ntfy_notification_unthreaded,
                    args = (renpy.substitute(message), player_ntfy_password,)
                )
            # This will prevent the thread from holding JN hostage. Basically it tells JN that the thread isn't important,
            # and not to wait for it to finish if we want to quit
            thread.setDaemon(True)
            thread.start()

    # Thanks to Zhaumbie for the two functions below

    def should_send_topic_notification(topic_label):
        """
        Returns True when the queued label is a normal topic,
        a queued special event, or an actual holiday.
        """
        topic = store.get_topic(topic_label)

        # Normal topics Natsuki is allowed to bring up herself
        if (
            topic is not None
            and topic_label in store.topics.TOPIC_MAP
            and topic.nat_says
            and "Setup" not in topic.category
        ):
            return True

        # Actual special events
        if topic_label in store.jn_events.EVENT_MAP:
            return True

        # Actual holiday scenes
        if store.jn_events.getHoliday(topic_label) is not None:
            return True

        return False

    # Sanitizes Natsuki's nickname for safe use as a topic prefix
    def get_safe_topic_prefix(name):
        safe_name = re.sub("[^A-Za-z0-9_-]", "", name or "")
        return safe_name if safe_name else "Natsuki"

# Here we wrap the global queue function to send the player a message whenever it is called,
# As long as jn_zpn.should_send_topic_notification() returns true
init 10 python:

    _original_queue = queue

    def queue_zpn(topic_label):

        if jn_zpn.should_send_topic_notification(topic_label):

            ENAMORED_NOTIFY_MESSAGES = [
                "[player]! [player]! Wanna talk? [happy_emote]",
                "Hey! You got a sec? [happy_emote]",
                "Wanna talk? [happy_emote]",
                "[player]! I got something! [happy_emote]",
                "Heeey! Wanna talk? [happy_emote]",
                "Talk to meeee! [angry_emote]",
                "I'm talking to you, dummy! [tease_emote]",
                "Come over here dummy! [tease_emote]"
            ]
            AFFECTIONATE_NOTIFY_MESSAGES = [
                "Come talk to me! [happy_emote]",
                "[player]! You wanna talk?",
                "Hey! Hey! Talk to me! [angry_emote]",
                "Hey dummy! I'm talking to you!",
                "[player]! I just thought of something! [confused_emote]",
                "[player]! I wanna talk to you! [happy_emote]",
                "I just thought of something, [player]!"
            ]
            HAPPY_NOTIFY_MESSAGES = [
                "[player]! Did you have a sec? [happy_emote]",
                "[player]? Can I borrow you?",
                "Are you at your PC right now? [confused_emote]",
                "Hey! Come here a sec?",
                "Hey! I wanna talk!",
                "You there, [player]?"
            ]
            NORMAL_NOTIFY_MESSAGES = [
                "You wanna talk?",
                "Hey... are you busy? [confused_emote]",
                "[player]? Did you have a sec?",
                "Can I borrow you for a sec?",
                "You there, [player]?",
                "Hey... you still there?",
                "[player]? Are you there?"
            ]

            if Natsuki.isNormal(higher=True):
                if Natsuki.isEnamored(higher=True):
                    ntfy_message = random.choice(ENAMORED_NOTIFY_MESSAGES)

                elif Natsuki.isAffectionate(higher=True):
                    ntfy_message = random.choice(AFFECTIONATE_NOTIFY_MESSAGES)

                elif Natsuki.isHappy(higher=True):
                    ntfy_message = random.choice(HAPPY_NOTIFY_MESSAGES)

                else:
                    ntfy_message = random.choice(NORMAL_NOTIFY_MESSAGES)

                jn_zpn.send_ntfy_notification(ntfy_message)

        # Continue normal game behavior
        return _original_queue(topic_label)

    queue = queue_zpn

# Topic to set up and give Natsuki the ability to text!
init 5 python:
    registerTopic(
        Topic(
            persistent._topic_database,
            label="talk_zombie_texting_setup",
            unlocked=True,
            prompt="Can we set up texting?",
            category=["Natsuki", "Media"],
            player_says=True,
            affinity_range=(jn_affinity.NORMAL, None),
            location="classroom"
        ),
        topic_group=TOPIC_TYPE_NORMAL
    )

label talk_zombie_texting_setup:
    $ player_text_preference = persistent._zombie_phone_notifications.get("player_text_preference")
    $ player_ntfy_password = persistent._zombie_phone_notifications.get("player_ntfy_password")

    if get_topic("talk_zombie_texting_setup").shown_count > 0:
        n 2tnmss "Oh,{w=0.2} did you wanna set up texting again?"

        show natsuki 7tnmsm at jn_center
        menu:
            n "What do you want to do?"

            "Can we set up a new topic name / password?":
                n 6uwlbg "Yeah,{w=0.2} we can do that!"

            "Can you stop sending me texts for now?" if player_text_preference == True:
                $ persistent._zombie_phone_notifications["player_text_preference"] = False

                n 7udtss "Need a break?"
                n 2ntlsm "Fine by me!"
                n 6nchss "Just let me know if you want me to start sending you messages again."

                return

            "Can you start sending me texts again?" if player_text_preference == False:
                $ persistent._zombie_phone_notifications["player_text_preference"] = True

                n 4fchsm "Ehehe,{w=0.5}{nw}"
                extend 7fsgsm " just couldn't resist my charm,{w=0.2} huh?"
                n 3uchsm "Sure thing!"

                return

            "Can you send me a text?" if player_text_preference == True:
                $ jn_zpn.send_ntfy_notification("Hi [player]! [happy_emote]")

                n 3uchsm "Sure thing!"

                return

            "Can you tell me our topic name / password again?":

                n 4fchsm "Ehehe,{w=0.5}{nw}"
                extend 4fsgss " why, [player]?{w=0.3} Forgot about it already?"
                n 1fsqsm "..."
                n 2fchlg "Ahaha!{w=0.3} You should've seen that look on your face."
                n 3uchgn "Don't worry,{w=0.2} I'm just teasing you!"
                n 6unmbg "It was \"[player_ntfy_password]\". "
                n 6uchbg "Hope that helps!"

                return

        n 7nnmss "For the first half of the topic,{w=0.2} we're gonna use my name,{w=0.5}{nw}"
        extend 7nchsm " like usual."

    else:
        n 1tnmfr "H-{w=0.2}huh?{w=0.3} What are you going on about, [player]?"
        n 2fllaj "You know I don't have a phone in here,{w=0.75}{nw}"
        extend 2ktraj " and even if I did-"
        n 1twdbo "..."
        n 1tsqbo "Wait,{w=0.5}{nw}"
        extend 4tslca " what is this{cps=30}...?{/cps}"
        n 7nsqbo "Did you...{w=0.3}{nw}"
        n 7tnmaj "[player]... Did you change something?"
        n 7tdwaj "There's something new in here..."
        n 2tdlbo "...{w=1.5}{nw}"
        extend 1uwdgseex "!!"
        n 4uspbs "[player]!{w=0.3} [player]!{w=0.3} How did you {i}do{/i} this?"
        n 7udlbs "If I'm seeing this correctly,{w=0.5}{nw}"
        extend 6uwdbs " this is gonna let me send you messages!"
        extend 3uchgn " like,{w=0.2} on your {i}phone{/i}!"
        n 4fsgct "Oh,{w=0.2} we {i}have{/i} to set this up right now...!"
        n 2fchsm "No worries though,{w=0.2} I don't think it'll take that long."
        n 2tdrsm "Okay...{w=0.3} what do we have here..."
        n 2tsrsmsbl "So,{w=0.2} it's not exactly {i}texting{/i},{w=0.5}{nw}"
        extend 1unmaj " but it looks like I can directly send you messages using this \"ntfy\" app."
        n 6fnmbg "And you don't even need the app open for me to message you!"
        n 1uchgn "Plus, it's free,{w=0.2} and you don't even need to sign in!"
        n 6fsgbg "Sounds epic, doesn't it?"
        n 7fsgsm "Now,{w=0.2} go on your phone,{w=0.2} head to your app store and search for {i}ntfy{/i}."
        n 7ntlaj "The icon should be green with a speech bubble in the middle."
        n 2uchsm "Let me know when you finish downloading it!"

        show natsuki option_wait_curious
        menu:
            n "Got it yet?"

            "Yes.":
                n 4uchbg "Good!"
                n 7utrbg "It looks like you can receive my messages by subscribing to a topic in the app."
                n 7nsqbg "And don't worry,{w=0.2} it's not the kind of subscription that needs money."
                n 6nchgn "Anyway,{w=0.2} let's name that topic right now!"
                n 6uwlsm "For the first half,{w=0.2} we're gonna use my name."

    # Save previous configuration, in case the player backs out of setup.
    $ previous_ntfy_password = persistent._zombie_phone_notifications.get("player_ntfy_password", "none")
    $ previous_text_preference = persistent._zombie_phone_notifications.get("player_text_preference", False)

    # If the player has given Natsuki a nickname, they can choose to use it for their "password"
    if (
        persistent._jn_nicknames_natsuki_allowed
        and persistent._jn_nicknames_natsuki_current_nickname
        and persistent._jn_nicknames_natsuki_current_nickname != "Natsuki"
        ):
        show natsuki 7tsqsm at jn_center
        menu:
            n "Do you want me to use my nickname?{w=0.3} Or just \"Natsuki\"?"

            "Let's use your nickname.":
                $ ntfy_natsuki_name = jn_zpn.get_safe_topic_prefix(
                    persistent._jn_nicknames_natsuki_current_nickname
                )
                n 2uchgn "Okaaay!{w=0.5}{nw}"
                extend 2uwrbg " Sounds good to me!"

            "Natsuki is fine.":
                $ ntfy_natsuki_name = "Natsuki"
                n 2tnmbg "Oh,{w=0.2} okay!"
                n 2nwlsm "Fine by me."

    else:
        $ ntfy_natsuki_name = "Natsuki"

    n 7uupbg "Now for the second half,{w=0.2} we need to make a password."
    n 7ksrsm "Because of how the app works,{w=0.2} the topic name {i}is{/i} the password."
    n 3uchsm "So let's make one!"
    n 3ullaj "It doesn't need to be super serious,{w=0.5}{nw}"
    extend 5nsrsmsbl " we can always change it later if someone figures it out."
    n 4unmaj "I would aim for it to be between eight and twelve characters."
    n 4uchcs "Oh, and just letters and numbers will be fine,{w=0.5}{nw}"
    extend 4fsgsm " no fancy symbols or anything like that."

    # We need the player to choose a "password", otherwise players will receive notifications from others

    $ player_input_valid = False

    while not player_input_valid:
        show natsuki 4tnmsm at jn_center

        $ ntfy_password = renpy.input(prompt="Enter a password: (Or type nevermind to exit setup)", allow="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", length=16)

        if ntfy_password.lower() == "nevermind":
            n 3tnmss "Oh,{w=0.2} do you want to set this up another time then?"
            n 3nslss "That's fine,{w=0.5}{nw}"
            extend 6uchsm " just let me know when!"

            return

        elif len(ntfy_password) <= 6:
            n 6usqsm "Sorry, [player],{w=0.2} it's gonna have to be longer than that."

        else:
            python:
                player_input_valid = True

                player_ntfy_password = ntfy_natsuki_name + "_" + ntfy_password
                persistent._zombie_phone_notifications["player_ntfy_password"] = player_ntfy_password
                persistent._zombie_phone_notifications["player_text_preference"] = True

            n 6uchbg "Great! '[ntfy_password]' it is."

    n 3unmbg "Almost done!{w=0.75}{nw}"
    n 3uchbg "Just one more thing and we should be good to go."
    n 3unmaj "Now, go ahead and open the app on your phone if you haven't already."
    n 3utrss "Tap the plus...{w=1}{nw}"
    extend 6unmbg " And enter \"[player_ntfy_password]\" into the text box."
    #n 7uchbg "Again,{w=0.2} that's \"[player_ntfy_password]\"."
    n 7nnmbg "Now just tap \"Subscribe\",{w=0.2} and I think it's about time we test it,{w=0.5}{nw}"
    extend 4uchbg " don't you think?"
    n 7cdwfo "By the way,{w=0.2} it {i}might{/i} take some time to send that notification,{w=0.8}{nw}"
    extend 6uchss " so give it some time!"

    $ retry_ntfy_attempt = True

    while retry_ntfy_attempt:

        $ jn_zpn.send_ntfy_notification("Well? Did it work, [player]? [happy_emote]")

        show natsuki 4uspbs at jn_center
        menu:
            n "Does it work? Did you see my message?"

            "Yes, I see it.":
                $ retry_ntfy_attempt = False
                n 2fchgn "Yes!{w=0.3} This is gonna be {i}so{/i} awesome."

            "No, I can't see it.":
                n 1kcswr "Man... I was really hoping it would work."
                n 1ttlpo "Hmm...{w=0.3}"
                n 1tnmaj "Is it possible that you misspelled the topic?"
                n 4cwdgslesssbl "Not that I'm blaming you or anything!"
                n 4ullajlsbl "But,{w=0.2} just to double-check,{w=0.5}{nw}"
                extend 6unmsm " it was \"[player_ntfy_password]\", right?"
                n 7unmgseex "Oh!{w=0.25}{nw}"
                extend 7nnmbg " Make sure you have notifications turned on for the app, too"
                n 7nsrbgsbr "You might have to go into your phone's settings to find that..."

                show natsuki 3tnmsm at jn_center
                menu:
                    n "Well,{w=0.2} do you want to try again?"

                    "Yes.":
                        n 3uchsm "Great! Let's give it another shot then."

                    "No.":
                        #Restore original setup
                        $ persistent._zombie_phone_notifications["player_ntfy_password"] = previous_ntfy_password
                        $ persistent._zombie_phone_notifications["player_text_preference"] = previous_text_preference

                        n 3knmpo "Oh,{w=0.5}{nw}"
                        extend 3unmaj " well, I guess we can always try again later."
                        n 6uchsm "Just let me know when!"

                        return

    if Natsuki.isAffectionate(higher=True):
        n 5ullssf "I know how much you love hearing me talk by now..."
        n 4uchssfsbl "But I'll do my best not to blow up your phone with messages."

    else:
        n 4ullss "I know you probably don't want me messaging you {i}constantly{/i}..."

    n 2uchsm "So I'll mostly stick to messaging you when I wanna talk about something."
    n 6unmbg "That way,{w=0.2} even if you step away from your computer for a moment,{w=0.5}{nw}"
    extend 7uchgn " I can still get ahold of you!"
    n 4fsgct "Oh,{w=0.2} and one more thing, [player]."

    if Natsuki.isLove(higher=True):
        $ jn_zpn.send_ntfy_notification("I love youuuu~! [tease_emote]")

    elif Natsuki.isEnamored(higher=True):
        $ jn_zpn.send_ntfy_notification("Thanks dummy! [tease_emote]")

    elif Natsuki.isAffectionate(higher=True):
        $ jn_zpn.send_ntfy_notification("Thanks dummy! [happy_emote]")

    elif Natsuki.isHappy(higher=True):
        $ jn_zpn.send_ntfy_notification("Thank you! [happy_emote]")

    else:
        $ jn_zpn.send_ntfy_notification("Thank you!")

    n 4fsgsm "..."
    n 4uchbl "Ehehe."

    return
