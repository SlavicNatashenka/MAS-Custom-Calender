init python:
    import datetime
    import os

    CUSTOM_CAL_ICONS_DIR = "Submods/Custom Calendar Dates/icons"

    def custom_cal_get_available_icons():
        icons = []
        full_dir = os.path.join(renpy.config.gamedir, CUSTOM_CAL_ICONS_DIR.replace("/", os.sep))
        if os.path.exists(full_dir):
            for fname in os.listdir(full_dir):
                if fname.lower().endswith((".png", ".jpg", ".webp")):
                    icons.append(fname)
        icons.sort()
        return icons

    def custom_cal_get_icon_path(icon_name):
        if not icon_name:
            return None
        return CUSTOM_CAL_ICONS_DIR + "/" + icon_name

    def custom_cal_format_icon_label(filename):
        name = os.path.splitext(filename)[0]
        return name.replace("_", " ").replace("-", " ").strip().title()

    def custom_cal_create_event(name, start_date, end_date=None, is_multiday=False,
                                recurrence="none", custom_interval_type="days", custom_interval_num=1,
                                category="misc", meta=None, icon=None):
        if meta is None:
            meta = {}

        if end_date is None or not is_multiday:
            end_date = start_date

        s_dt = datetime.date(start_date[0], start_date[1], start_date[2])
        e_dt = datetime.date(end_date[0], end_date[1], end_date[2])
        if e_dt < s_dt:
            e_dt = s_dt
            end_date = start_date

        import time
        event_id = "cust_evt_{}_{}_{}".format(
            s_dt.strftime("%Y%m%d"),
            int(time.time()),
            len(persistent._mas_custom_calendar_events)
        )

        event_data = {
            "id": event_id,
            "name": name.strip(),
            "start_date": (s_dt.year, s_dt.month, s_dt.day),
            "end_date": (e_dt.year, e_dt.month, e_dt.day),
            "is_multiday": is_multiday,
            "recurrence": recurrence,
            "custom_interval_type": custom_interval_type,
            "custom_interval_num": max(1, int(custom_interval_num)),
            "category": category,
            "meta": meta,
            "icon": icon,
            "last_greeted_date": None,
            "last_countdown_date": None,
            "last_followup_date": None
        }

        persistent._mas_custom_calendar_events[event_id] = event_data
        custom_cal_sync_event_to_calendar(event_data)
        renpy.save_persistent()
        return event_id

    def custom_cal_delete_event(event_id):
        if event_id not in persistent._mas_custom_calendar_events:
            return False

        event_data = persistent._mas_custom_calendar_events[event_id]
        custom_cal_remove_event_from_calendar(event_data)
        del persistent._mas_custom_calendar_events[event_id]
        renpy.save_persistent()
        return True

    def custom_cal_get_events_for_date(check_date):
        matched_events = []
        if not persistent._mas_custom_calendar_events:
            return matched_events

        for event_id, evt in persistent._mas_custom_calendar_events.items():
            if custom_cal_is_event_on_date(evt, check_date):
                matched_events.append(evt)
        return matched_events

    def custom_cal_is_event_on_date(evt, check_date):
        s_dt = datetime.date(evt["start_date"][0], evt["start_date"][1], evt["start_date"][2])
        e_dt = datetime.date(evt["end_date"][0], evt["end_date"][1], evt["end_date"][2])
        duration_days = (e_dt - s_dt).days

        if check_date < s_dt:
            return False

        recurrence = evt.get("recurrence", "none")

        if recurrence == "none":
            return s_dt <= check_date <= e_dt

        elif recurrence == "weekly":
            delta_days = (check_date - s_dt).days
            offset = delta_days % 7
            return offset <= duration_days

        elif recurrence == "monthly":
            try:
                anchor_this_month = datetime.date(check_date.year, check_date.month, s_dt.day)
            except ValueError:
                return False

            if anchor_this_month <= check_date <= anchor_this_month + datetime.timedelta(days=duration_days):
                return True

            if check_date.month > 1:
                prev_month = check_date.month - 1
                prev_year = check_date.year
            else:
                prev_month = 12
                prev_year = check_date.year - 1
            try:
                anchor_prev = datetime.date(prev_year, prev_month, s_dt.day)
                if anchor_prev <= check_date <= anchor_prev + datetime.timedelta(days=duration_days):
                    return True
            except ValueError:
                pass
            return False

        elif recurrence == "yearly":
            try:
                anchor_this_year = datetime.date(check_date.year, s_dt.month, s_dt.day)
            except ValueError:
                return False

            return anchor_this_year <= check_date <= anchor_this_year + datetime.timedelta(days=duration_days)

        elif recurrence == "custom":
            interval_type = evt.get("custom_interval_type", "days")
            interval_num = max(1, evt.get("custom_interval_num", 1))

            if interval_type == "days":
                return ((check_date - s_dt).days % interval_num) <= duration_days

            elif interval_type == "weeks":
                return ((check_date - s_dt).days % (interval_num * 7)) <= duration_days

            elif interval_type == "months":
                month_diff = (check_date.year - s_dt.year) * 12 + (check_date.month - s_dt.month)
                if month_diff >= 0 and month_diff % interval_num == 0:
                    try:
                        anchor = datetime.date(check_date.year, check_date.month, s_dt.day)
                        return anchor <= check_date <= anchor + datetime.timedelta(days=duration_days)
                    except ValueError:
                        return False
                return False

        return False

    def custom_cal_sync_event_to_calendar(evt):
        event_id = evt["id"]
        name = evt["name"]
        recurrence = evt.get("recurrence", "none")
        s_dt = datetime.date(evt["start_date"][0], evt["start_date"][1], evt["start_date"][2])
        e_dt = datetime.date(evt["end_date"][0], evt["end_date"][1], evt["end_date"][2])
        duration = (e_dt - s_dt).days

        custom_cal_remove_event_from_calendar(evt)

        if recurrence == "yearly" and duration == 0:
            store.mas_calendar.addRepeatable(
                event_id,
                name,
                s_dt.month,
                s_dt.day,
                []
            )
        else:
            today = datetime.date.today()
            for year in range(today.year - 1, today.year + 3):
                cur_dt = datetime.date(year, 1, 1)
                end_of_year = datetime.date(year, 12, 31)
                one_day = datetime.timedelta(days=1)
                while cur_dt <= end_of_year:
                    if custom_cal_is_event_on_date(evt, cur_dt):
                        cal_entry_id = "{}_{}_{}_{}".format(event_id, cur_dt.year, cur_dt.month, cur_dt.day)
                        store.mas_calendar.addRepeatable(
                            cal_entry_id,
                            name,
                            cur_dt.month,
                            cur_dt.day,
                            [cur_dt.year]
                        )
                    cur_dt += one_day

    def custom_cal_remove_event_from_calendar(evt):
        event_id = evt["id"]
        for m in range(1, 13):
            for d in range(1, 32):
                if m in store.mas_calendar.calendar_database and d in store.mas_calendar.calendar_database[m]:
                    day_dict = store.mas_calendar.calendar_database[m][d]
                    keys_to_remove = [k for k in day_dict if k == event_id or k.startswith(event_id + "_")]
                    for k in keys_to_remove:
                        try:
                            store.mas_calendar.removeRepeatable(k, month=m, day=d)
                        except:
                            if k in day_dict:
                                del day_dict[k]

    def custom_cal_sync_all():
        if persistent._mas_custom_calendar_events:
            for event_id, evt in persistent._mas_custom_calendar_events.items():
                custom_cal_sync_event_to_calendar(evt)

init 5 python:
    custom_cal_sync_all()
