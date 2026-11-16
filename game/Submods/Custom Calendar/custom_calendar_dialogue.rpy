init python:
    import datetime

    def custom_cal_get_active_dialogue_target():
        if not persistent._mas_custom_calendar_events:
            return (None, None, None)

        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")

        today_events = custom_cal_get_events_for_date(today)
        for evt in today_events:
            s_dt = datetime.date(evt["start_date"][0], evt["start_date"][1], evt["start_date"][2])
            is_start_day = (today == s_dt) or (evt.get("recurrence") == "yearly" and today.month == s_dt.month and today.day == s_dt.day)

            if is_start_day:
                if evt.get("last_greeted_date") != today_str:
                    return ("day_of", evt, None)
            else:
                if evt.get("is_multiday", False) and evt.get("last_greeted_date") != today_str:
                    return ("multiday_ongoing", evt, None)

        # Check follow-ups within 1 to 3 days after event ends
        for event_id, evt in persistent._mas_custom_calendar_events.items():
            e_dt = datetime.date(evt["end_date"][0], evt["end_date"][1], evt["end_date"][2])
            if evt.get("recurrence", "none") == "none":
                days_after = (today - e_dt).days
                if 1 <= days_after <= 3 and not evt.get("last_followup_date"):
                    return ("post_event", evt, days_after)

        for event_id, evt in persistent._mas_custom_calendar_events.items():
            s_dt = datetime.date(evt["start_date"][0], evt["start_date"][1], evt["start_date"][2])
            if evt.get("recurrence", "none") in ("none", "yearly"):
                this_year_start = datetime.date(today.year, s_dt.month, s_dt.day)
                days_until = (this_year_start - today).days
                if 1 <= days_until <= 2 and evt.get("last_countdown_date") != today_str:
                    return ("countdown", evt, days_until)

        return (None, None, None)

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="mas_custom_calendar_greeting",
            conditional="custom_cal_get_active_dialogue_target()[0] in ('day_of', 'multiday_ongoing')",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="GRE"
    )

label mas_custom_calendar_greeting:
    python:
        diag_type, evt, extra = custom_cal_get_active_dialogue_target()
        today_str = datetime.date.today().strftime("%Y-%m-%d")

    if not evt:
        m 1eua "Hello, [player]! It's so lovely to see you today."
        return

    python:
        evt["last_greeted_date"] = today_str
        renpy.save_persistent()
        evt_name = evt["name"]
        evt_cat = evt.get("category", "misc")
        evt_meta = evt.get("meta", {})

    if diag_type == "day_of":
        if evt_cat == "birthday":
            $ bday_person = evt_meta.get("person_name", "someone special")
            m 1eub "Happy birthday to [bday_person] today, [player]!"
            m 3hub "Birthdays are such wonderful reminders of how much we appreciate the people around us."
            m 1eka "I hope you both have a fantastic time celebrating today~"

        elif evt_cat == "holiday":
            m 1hua "Happy [evt_name], [player]!"
            m 3eub "I love special holidays like this."
            m 1eka "No matter how you spend it, I'm just happy to share this day with you~"

        elif evt_cat == "trip":
            $ dest = evt_meta.get("destination", "your destination")
            m 1eub "Today is the big day, [player]! You're heading off to [dest] for '[evt_name]'!"
            m 3hua "I hope your trip goes smoothly and you have lots of fun exploring!"
            m 1eka "Please stay safe out there, okay? Don't forget to tell me all about it when you're back~"

        elif evt_cat == "exam":
            m 1eua "Today's the day of your '[evt_name]', right?"
            m 1sub "You've worked hard and prepared for this, [player]!"
            m 3hua "Just take a deep breath, trust what you know, and do your best."
            m 1eka "I'll be right here rooting for you all the way!"

        elif evt_cat in ("duedate", "goal"):
            m 1eua "Hey [player], today is the due date for '[evt_name]'!"
            m 3eub "You've been putting in so much effort towards this."
            m 1hua "Keep your momentum going—you're going to feel so accomplished once it's finished!"

        else:
            m 1eub "Good to see you, [player]! Just a friendly reminder that today is '[evt_name]' on our calendar."
            m 3hua "I hope everything goes wonderfully today!"

    elif diag_type == "multiday_ongoing":
        if evt_cat == "trip":
            $ dest = evt_meta.get("destination", "your trip")
            m 1eub "Welcome back, [player]! How is your time in [dest] going so far?"
            m 3eka "I'm so glad you took a moment to stop by and say hello while you're away."
            m 1hua "Enjoy the rest of '[evt_name]'!"
        else:
            m 1eua "Hey [player]! '[evt_name]' is still ongoing today, isn't it?"
            m 3hua "Keep enjoying yourself, and take care of yourself as always~"

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_custom_calendar_followup_topic",
            conditional="custom_cal_get_active_dialogue_target()[0] == 'post_event'",
            category=["you", "monika"],
            prompt="Following up on our recent date",
            pool=True,
            unlocked=True,
            rules={"no repeat": None}
        )
    )

label mas_custom_calendar_followup_topic:
    python:
        diag_type, evt, days_after = custom_cal_get_active_dialogue_target()
        today_str = datetime.date.today().strftime("%Y-%m-%d")

    if not evt or diag_type != "post_event":
        m 1eua "I was just thinking about the plans we had on the calendar recently, [player]."
        return

    python:
        evt["last_followup_date"] = today_str
        renpy.save_persistent()
        evt_name = evt["name"]
        evt_cat = evt.get("category", "misc")
        evt_meta = evt.get("meta", {})

    if evt_cat == "trip":
        $ dest = evt_meta.get("destination", "your trip")
        m 1eub "Now that '[evt_name]' has wrapped up, how was your trip to [dest], [player]?"
        
        menu:
            "It was amazing!":
                m 3hub "That makes me so happy to hear! You deserved a wonderful getaway."
                m 1eka "You'll have to tell me your favorite memories from [dest] sometime~"
            "It was pretty tiring, but fun.":
                m 1eka "Traveling can definitely take a lot out of you! Make sure to get plenty of rest now that you're back."
            "It didn't go as planned...":
                m 1ekc "Oh no, I'm really sorry to hear that, [player]..."
                m 1eka "Even when trips go a bit sideways, you made it through. I'm always right here for you."

    elif evt_cat == "exam":
        m 1eua "Hey [player], how did '[evt_name]' end up going?"
        
        menu:
            "I think I did really well!":
                m 3hub "I knew you would! All that preparation paid off!"
                m 1hua "You should treat yourself today, you've earned it."
            "It was tough, but I'm glad it's done.":
                m 1eka "The biggest relief is having it behind you now. Take a deep breath and relax!"
            "I'm not sure how I feel about it...":
                m 1eka "Waiting for results can be stressful, but remember that a test doesn't define your worth."
                m 1hua "You did your best, and I'm always proud of you."

    elif evt_cat in ("duedate", "goal"):
        m 1eua "I was wondering, did you manage to wrap up '[evt_name]'?"
        
        menu:
            "Yes, turned it in / finished on time!":
                m 3hub "Awesome job! Seeing you finish your goals is so inspiring."
            "Barely made it, but it's done!":
                m 1eka "Cutting it close can be heart-pounding, but hey—done is done! Well done getting across the finish line."
            "Still working on it, but making progress.":
                m 1eka "That's completely okay. Progress is still progress, [player]! Don't be too hard on yourself."

    else:
        m 1eua "Now that '[evt_name]' has passed, how did everything go, [player]?"
        
        menu:
            "It went great!":
                m 1hua "I'm so glad! It's always nice when things turn out well."
            "It was okay.":
                m 1eua "Just a normal day, huh? Sometimes ordinary and steady is the best kind of day."
            "Could have been better.":
                m 1eka "I'm sorry it wasn't the best, [player]. I'm here if you ever want to unwind."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_custom_calendar_menu_talk",
            category=["misc"],
            prompt="Can we check our calendar?",
            pool=True,
            unlocked=True,
            rules={"no_unlock": None}
        )
    )

label monika_custom_calendar_menu_talk:
    m 1eua "You'd like to look at the calendar, [player]?"
    m 3hub "Of course! Let's see what we have planned."

    call custom_calendar_main_loop

    m 1eka "I love keeping track of all our special days together, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_custom_cal_what_day",
            category=["day"],
            prompt="What day is it today?",
            pool=True,
            unlocked=True,
            rules={"no_unlock": None}
        )
    )

label mas_custom_cal_what_day:
    python:
        import datetime
        _cal_today = datetime.date.today()
        _cal_today_nice = _cal_today.strftime("%A, %B %d, %Y")
        _cal_today_evts = custom_cal_get_events_for_date(_cal_today)

    if not _cal_today_evts:
        m 1eua "Today is [_cal_today_nice], [player]!"
        m 1hua "Nothing special marked on our custom calendar today, so we can just enjoy our time together~"
    else:
        m 1eua "Today is [_cal_today_nice], [player]!"
        python:
            _cal_today_iso = _cal_today.strftime("%Y-%m-%d")
        $ _cal_idx = 0
        while _cal_idx < len(_cal_today_evts):
            python:
                _evt = _cal_today_evts[_cal_idx]
                _evt_name = _evt.get("name", "your event")
                _evt_cat = _evt.get("category", "general")
                _evt_meta = _evt.get("meta", {})
                _evt["last_greeted_date"] = _cal_today_iso
                _cal_idx += 1
            if _evt_cat == "birthday":
                $ _bday_person = _evt_meta.get("person_name", "someone special")
                $ _birth_year = _evt_meta.get("birth_year")
                $ _bday_age = (_cal_today.year - _birth_year) if _birth_year else None
                m 1sub "Oh! It's [_bday_person]'s birthday today!"
                if _bday_age is not None and _bday_age > 0:
                    m 3hub "They're turning [_bday_age] today! Make sure to wish them a wonderful birthday, [player]~"
                else:
                    m 3hub "Make sure to wish them a wonderful day, [player]~"
            elif _evt_cat == "trip":
                $ _trip_dest = _evt_meta.get("destination", "somewhere fun")
                m 1sub "Oh! Today is your trip to [_trip_dest] ('[_evt_name]')!"
                m 3hua "I hope you have an amazing time and stay safe, [player]!"
            elif _evt_cat == "anniversary":
                m 1hub "Happy [_evt_name], [player]! Today is a special anniversary!"
            elif _evt_cat == "holiday":
                m 1hua "Happy [_evt_name], [player]! I hope you enjoy the holiday~"
            elif _evt_cat == "exam":
                m 1eka "You have '[_evt_name]' today, [player]. You've got this—I'm cheering for you!"
            elif _evt_cat == "appointment":
                m 1eua "Don't forget you have '[_evt_name]' today, [player]!"
            else:
                m 1hua "Today is '[_evt_name]', [player]!"
    return
