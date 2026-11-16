init -990 python in mas_submod_utils:
    Submod(
        author="Natashenka",
        name="Custom Calendar",
        description="Lets you add custom dates and events to the MAS calendar.",
        version="2.0.0"
    )

default persistent._mas_custom_calendar_events = {}

init 1 python:
    if persistent._mas_custom_calendar_events is None:
        persistent._mas_custom_calendar_events = {}

    # Migrate legacy v1.0 data if present
    if hasattr(persistent, "_mas_custom_dates") and persistent._mas_custom_dates:
        for legacy_id, legacy_data in persistent._mas_custom_dates.items():
            if legacy_id not in persistent._mas_custom_calendar_events:
                import datetime
                _today = datetime.date.today()
                _m = legacy_data.get("month", 1)
                _d = legacy_data.get("day", 1)
                _y = _today.year
                persistent._mas_custom_calendar_events[legacy_id] = {
                    "id": legacy_id,
                    "name": legacy_data.get("name", "Custom Date"),
                    "start_date": (_y, _m, _d),
                    "end_date": (_y, _m, _d),
                    "is_multiday": False,
                    "recurrence": "yearly",
                    "custom_interval_type": "days",
                    "custom_interval_num": 1,
                    "category": "misc",
                    "meta": {},
                    "icon": None,
                    "last_greeted_date": None,
                    "last_countdown_date": None,
                    "last_followup_date": None
                }
        persistent._mas_custom_dates = {}
        renpy.save_persistent()
