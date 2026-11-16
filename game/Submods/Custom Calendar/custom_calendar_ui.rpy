init 10 python:
    _orig_MASCalendar_setupDayButtons = store.MASCalendar._setupDayButtons
    _orig_MASCalendar_init = store.MASCalendar.__init__
    _orig_MASCalendar_event = store.MASCalendar.event

    store.custom_cal_delete_mode = False
    store.custom_cal_active_instance = None

    def _custom_MASCalendar_init(self, select_date=False):
        store.custom_cal_active_instance = self
        _orig_MASCalendar_init(self, select_date)
        if store.custom_cal_delete_mode:
            self.can_select_date = True

        btn_idle = "mod_assets/hkb_idle_background.png" if self.day_mode else "mod_assets/hkb_idle_background_d.png"
        btn_hover = "mod_assets/hkb_hover_background.png" if self.day_mode else "mod_assets/hkb_hover_background_d.png"
        btn_disable = "mod_assets/hkb_disabled_background.png" if self.day_mode else "mod_assets/hkb_disabled_background_d.png"

        txt_color = "#000000" if self.day_mode else "#ffffff"

        add_t_idle = Text("+ Add Date", font=gui.default_font, size=15, color=txt_color, outlines=[])
        add_t_hover = Text("+ Add Date", font=gui.default_font, size=15, color="#ff77aa" if self.day_mode else "#ffaacc", outlines=[])

        self.btn_custom_add = MASButtonDisplayable(
            add_t_idle,
            add_t_hover,
            add_t_idle,
            Image(btn_idle),
            Image(btn_hover),
            Image(btn_disable),
            390,
            622,
            120,
            35,
            hover_sound=gui.hover_sound,
            activate_sound=gui.activate_sound,
            return_value="CUSTOM_CAL_ADD"
        )
        self.const_buttons.append(self.btn_custom_add)

        del_label = "Done Deleting" if store.custom_cal_delete_mode else "- Remove Date"
        del_t_idle = Text(del_label, font=gui.default_font, size=14, color=txt_color, outlines=[])
        del_t_hover = Text(del_label, font=gui.default_font, size=14, color="#ff4444", outlines=[])

        self.btn_custom_delete = MASButtonDisplayable(
            del_t_idle,
            del_t_hover,
            del_t_idle,
            Image(btn_idle),
            Image(btn_hover),
            Image(btn_disable),
            530,
            622,
            120,
            35,
            hover_sound=gui.hover_sound,
            activate_sound=gui.activate_sound,
            return_value="CUSTOM_CAL_TOGGLE_DELETE"
        )
        self.const_buttons.append(self.btn_custom_delete)

    def _custom_MASCalendar_event(self, ev, x, y, st):
        if ev.type in self.MOUSE_EVENTS:
            sel_action = self._buttonSelect(ev, x, y, st)
            if sel_action == "CUSTOM_CAL_ADD":
                renpy.call_in_new_context("custom_cal_open_add_menu")
                renpy.redraw(self, 0)
                return None
            elif sel_action == "CUSTOM_CAL_TOGGLE_DELETE":
                store.custom_cal_delete_mode = not store.custom_cal_delete_mode
                self.can_select_date = store.custom_cal_delete_mode
                del_label = "Done Deleting" if store.custom_cal_delete_mode else "- Remove Date"
                txt_color = "#000000" if self.day_mode else "#ffffff"
                self.btn_custom_delete.idle_text = Text(del_label, font=gui.default_font, size=14, color=txt_color, outlines=[])
                self.btn_custom_delete.hover_text = Text(del_label, font=gui.default_font, size=14, color="#ff4444", outlines=[])
                self._setupDayButtons()
                renpy.redraw(self, 0)
                return None
            elif isinstance(sel_action, tuple) and sel_action[0] == "CUSTOM_CAL_DELETE_CLICK":
                clicked_dt = sel_action[1]
                if isinstance(clicked_dt, datetime.datetime):
                    clicked_date = clicked_dt.date()
                else:
                    clicked_date = clicked_dt
                renpy.call_in_new_context("custom_cal_confirm_delete_date", clicked_date)
                self._setupDayButtons()
                renpy.redraw(self, 0)
                return None
        return _orig_MASCalendar_event(self, ev, x, y, st)

    def _custom_MASCalendar_setupDayButtons(self):
        _orig_MASCalendar_setupDayButtons(self)

        if store.custom_cal_delete_mode:
            for idx, date_val in enumerate(self.dates):
                if idx < len(self.day_buttons):
                    self.day_buttons[idx].return_value = ("CUSTOM_CAL_DELETE_CLICK", date_val)

        for container, button_pos in self.day_button_texts:
            for idx, date_val in enumerate(self.dates):
                b_x = self.INITIAL_POSITION_X + ((idx % 7) * self.DAY_BUTTON_WIDTH)
                b_y = self.INITIAL_POSITION_Y + (self.DAY_NAME_BUTTON_HEIGHT * 2) + ((idx // 7) * self.DAY_BUTTON_HEIGHT)
                if button_pos == (b_x, b_y) and date_val.month == self.selected_month:
                    matched_evts = custom_cal_get_events_for_date(date_val.date())
                    if matched_evts:
                        if any(e.get("is_multiday", False) for e in matched_evts):
                            bar_disp = Solid("#ff7799CC", xsize=self.DAY_BUTTON_WIDTH - 6, ysize=3)
                            bar_container = Fixed(
                                bar_disp,
                                pos=(3, self.DAY_BUTTON_HEIGHT - 5),
                                xsize=self.DAY_BUTTON_WIDTH - 6,
                                ysize=3
                            )
                            container.add(bar_container)
                    break

    store.MASCalendar.__init__ = _custom_MASCalendar_init
    store.MASCalendar._setupDayButtons = _custom_MASCalendar_setupDayButtons
    store.MASCalendar.event = _custom_MASCalendar_event

default cal_form_step = 1
default cal_form_name = ""
default cal_form_s_day = 1
default cal_form_s_month = 1
default cal_form_s_year = 2026
default cal_form_birth_year = 2000
default cal_form_e_day = 1
default cal_form_e_month = 1
default cal_form_e_year = 2026
default cal_form_is_multiday = False
default cal_form_recurrence = "none"
default cal_form_interval_type = "days"
default cal_form_interval_num = 1
default cal_form_category = "misc"
default cal_form_meta_extra = ""
default cal_form_icon = None
default cal_emoji_picker_open = False
default cal_form_error = ""

# Override MAS's internal calendar runner so ALL calendar calls use our loop
label _mas_start_calendar(select_date=True):
    call custom_calendar_main_loop
    return _return

label mas_start_calendar_read_only:
    call custom_calendar_main_loop
    return _return

label mas_start_calendar_select_date:
    call custom_calendar_main_loop
    return _return

label custom_calendar_main_loop:
    python:
        store.custom_cal_delete_mode = False

    label .loop:
        python:
            _should_drop_shields = not store.mas_calendar.enabled
            mas_calRaiseOverlayShield()
            HKBHideButtons()

            ui.add(store.MASCalendar(False))
            cal_action = ui.interact()

            HKBShowButtons()
            if _should_drop_shields:
                mas_calDropOverlayShield()

        if cal_action == "CUSTOM_CAL_ADD":
            call custom_cal_open_add_menu
            jump custom_calendar_main_loop.loop

        elif cal_action == "CUSTOM_CAL_TOGGLE_DELETE":
            python:
                store.custom_cal_delete_mode = not store.custom_cal_delete_mode
                if store.custom_cal_active_instance:
                    store.custom_cal_active_instance.can_select_date = store.custom_cal_delete_mode
                    store.custom_cal_active_instance._setupDayButtons()
            jump custom_calendar_main_loop.loop

        elif isinstance(cal_action, tuple) and cal_action[0] == "CUSTOM_CAL_DELETE_CLICK":
            $ clicked_dt = cal_action[1]
            if isinstance(clicked_dt, datetime.datetime):
                $ clicked_date = clicked_dt.date()
            else:
                $ clicked_date = clicked_dt
            
            call custom_cal_confirm_delete_date(clicked_date)
            jump custom_calendar_main_loop.loop

        elif cal_action == store.MASCalendar.CALENDAR_CLOSE or cal_action == "":
            return

        jump custom_calendar_main_loop.loop

label custom_cal_confirm_delete_date(target_date):
    python:
        matching_evts = custom_cal_get_events_for_date(target_date)
    
    if not matching_evts:
        m 1eka "There are no custom events on that day to remove, [player]."
        return

    python:
        evt_to_delete = matching_evts[0]
        del_evt_name = evt_to_delete["name"]
        del_evt_id = evt_to_delete["id"]

    m 1euc "Are you sure you want to remove '[del_evt_name]' from the calendar?"
    m 3eka "If it repeats, all past and future occurrences will be removed as well."

    menu:
        "Yes, remove it.":
            python:
                custom_cal_delete_event(del_evt_id)
                if store.custom_cal_active_instance:
                    store.custom_cal_active_instance._setupDayButtons()
            m 1eua "Got it! I've removed '[del_evt_name]' from the calendar."
        "No, keep it.":
            m 1hua "Okay, keeping it on the calendar!"
    return

label custom_cal_open_add_menu:
    python:
        import datetime
        _t = datetime.date.today()
        cal_form_step = 1
        cal_form_name = ""
        cal_form_s_day = _t.day
        cal_form_s_month = _t.month
        cal_form_s_year = _t.year
        cal_form_e_day = _t.day
        cal_form_e_month = _t.month
        cal_form_e_year = _t.year
        cal_form_is_multiday = False
        cal_form_recurrence = "none"
        cal_form_interval_type = "days"
        cal_form_interval_num = 1
        cal_form_category = "misc"
        cal_form_meta_extra = ""
        cal_form_icon = None
        cal_emoji_picker_open = False
        cal_form_error = ""

    call screen mas_custom_date_add_modal
    return

init python:
    _cal_frame_bg = Frame("gui/frame.png", 4, 4)
    _cal_btn_idle_bg = Frame("gui/button/choice_idle_background.png", 4, 4)
    _cal_btn_hover_bg = Frame("gui/button/choice_hover_background.png", 4, 4)

screen mas_custom_date_add_modal():
    modal True
    zorder 100

    add Solid("#000000B2")

    frame:
        xsize 840
        ysize 640
        xalign 0.5
        yalign 0.5
        background _cal_frame_bg
        padding (30, 25)

        vbox:
            spacing 14
            xfill True

            # Header
            hbox:
                xfill True
                text "Create Custom Calendar Event":
                    font gui.default_font
                    size 24
                    bold True
                    color gui.accent_color
                    outlines [(1, "#00000055", 0, 0)]
                    yalign 0.5

                textbutton "Cancel":
                    xalign 1.0
                    background _cal_btn_idle_bg
                    hover_background _cal_btn_hover_bg
                    selected_background _cal_btn_hover_bg
                    padding (16, 6)
                    text_font gui.default_font
                    text_size 16
                    text_color "#2b1b21"
                    text_hover_color "#000000"
                    text_selected_color "#000000"
                    text_outlines []
                    action Return()

            # Step Tabs
            hbox:
                spacing 10
                xalign 0.5
                for s_num, s_title in [(1, "Title"), (2, "Dates"), (3, "Repeat"), (4, "Category")]:
                    if cal_form_step == s_num:
                        textbutton "[s_num]. [s_title]":
                            background _cal_btn_hover_bg
                            padding (14, 6)
                            text_font gui.default_font
                            text_size 15
                            text_bold True
                            text_color "#2b1b21"
                            text_hover_color "#000000"
                            text_selected_color "#000000"
                            text_outlines []
                            action NullAction()
                    else:
                        textbutton "[s_num]. [s_title]":
                            background _cal_btn_idle_bg
                            hover_background _cal_btn_hover_bg
                            selected_background _cal_btn_hover_bg
                            padding (14, 6)
                            text_font gui.default_font
                            text_size 15
                            text_color "#2b1b21"
                            text_hover_color "#000000"
                            text_selected_color "#000000"
                            text_outlines []
                            action SetVariable("cal_form_step", s_num)

            null height 4

            # Main Content Area
            frame:
                xfill True
                ysize 390
                background _cal_frame_bg
                padding (22, 20)

                if cal_form_step == 1:
                    vbox:
                        spacing 14
                        text "Step 1: Event Name" font gui.default_font bold True size 19 color gui.accent_color outlines [(1, "#00000055", 0, 0)]
                        text "Give your event a memorable name (e.g., 'History Exam', 'Trip to Paris', 'Game Night'):" font gui.default_font size 15 color "#2b1b21" outlines []

                        frame:
                            xfill True
                            ysize 54
                            background _cal_frame_bg
                            padding (12, 10)
                            input:
                                pixel_width 700
                                value VariableInputValue("cal_form_name")
                                length 45
                                font gui.default_font
                                color "#2b1b21"
                                outlines []
                                size 20

                elif cal_form_step == 2:
                    vbox:
                        spacing 12
                        text "Step 2: Date & Duration" font gui.default_font bold True size 19 color gui.accent_color outlines [(1, "#00000055", 0, 0)]

                        hbox:
                            spacing 16
                            textbutton ("● Single Day" if not cal_form_is_multiday else "○ Single Day"):
                                background _cal_btn_idle_bg
                                hover_background _cal_btn_hover_bg
                                selected_background _cal_btn_hover_bg
                                padding (14, 6)
                                text_font gui.default_font
                                text_size 15
                                text_color "#2b1b21"
                                text_hover_color "#000000"
                                text_selected_color "#000000"
                                text_bold (not cal_form_is_multiday)
                                text_outlines []
                                action SetVariable("cal_form_is_multiday", False)
                            textbutton ("● Multi-Day Span" if cal_form_is_multiday else "○ Multi-Day Span"):
                                background _cal_btn_idle_bg
                                hover_background _cal_btn_hover_bg
                                selected_background _cal_btn_hover_bg
                                padding (14, 6)
                                text_font gui.default_font
                                text_size 15
                                text_color "#2b1b21"
                                text_hover_color "#000000"
                                text_selected_color "#000000"
                                text_bold cal_form_is_multiday
                                text_outlines []
                                action SetVariable("cal_form_is_multiday", True)

                        null height 4

                        text "Start Date (DD - MM - YYYY):" font gui.default_font size 15 color "#2b1b21" bold True outlines []
                        hbox:
                            spacing 20
                            vbox:
                                spacing 4
                                text "Day: [cal_form_s_day]" font gui.default_font size 15 color "#2b1b21" outlines []
                                hbox:
                                    spacing 6
                                    textbutton "-":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_day", 31 if cal_form_s_day <= 1 else cal_form_s_day - 1)
                                    textbutton "+":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_day", (cal_form_s_day % 31) + 1)
                            vbox:
                                spacing 4
                                text "Month: [cal_form_s_month]" font gui.default_font size 15 color "#2b1b21" outlines []
                                hbox:
                                    spacing 6
                                    textbutton "-":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_month", 12 if cal_form_s_month <= 1 else cal_form_s_month - 1)
                                    textbutton "+":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_month", (cal_form_s_month % 12) + 1)
                            vbox:
                                spacing 4
                                text "Year: [cal_form_s_year]" font gui.default_font size 15 color "#2b1b21" outlines []
                                hbox:
                                    spacing 6
                                    textbutton "-":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_year", max(1900, cal_form_s_year - 1))
                                    textbutton "+":
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (10, 4)
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_outlines []
                                        action SetVariable("cal_form_s_year", min(datetime.date.today().year, cal_form_s_year + 1))

                        if cal_form_is_multiday:
                            null height 4
                            text "End Date (DD - MM - YYYY):" font gui.default_font size 15 color "#2b1b21" bold True outlines []
                            hbox:
                                spacing 20
                                vbox:
                                    spacing 4
                                    text "Day: [cal_form_e_day]" font gui.default_font size 15 color "#2b1b21" outlines []
                                    hbox:
                                        spacing 6
                                        textbutton "-":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_day", 31 if cal_form_e_day <= 1 else cal_form_e_day - 1)
                                        textbutton "+":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_day", (cal_form_e_day % 31) + 1)
                                vbox:
                                    spacing 4
                                    text "Month: [cal_form_e_month]" font gui.default_font size 15 color "#2b1b21" outlines []
                                    hbox:
                                        spacing 6
                                        textbutton "-":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_month", 12 if cal_form_e_month <= 1 else cal_form_e_month - 1)
                                        textbutton "+":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_month", (cal_form_e_month % 12) + 1)
                                vbox:
                                    spacing 4
                                    text "Year: [cal_form_e_year]" font gui.default_font size 15 color "#2b1b21" outlines []
                                    hbox:
                                        spacing 6
                                        textbutton "-":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_year", max(1900, cal_form_e_year - 1))
                                        textbutton "+":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_e_year", min(datetime.date.today().year, cal_form_e_year + 1))

                elif cal_form_step == 3:
                    vbox:
                        spacing 12
                        text "Step 3: Repeat Schedule" font gui.default_font bold True size 19 color gui.accent_color outlines [(1, "#00000055", 0, 0)]

                        grid 2 3:
                            spacing 10
                            for rec_key, rec_label in [
                                ("none", "Does Not Repeat"),
                                ("weekly", "Every Week"),
                                ("monthly", "Every Month"),
                                ("yearly", "Every Year"),
                                ("custom", "Custom Interval")
                            ]:
                                textbutton (("● " + rec_label) if cal_form_recurrence == rec_key else ("○ " + rec_label)):
                                    background _cal_btn_idle_bg
                                    hover_background _cal_btn_hover_bg
                                    selected_background _cal_btn_hover_bg
                                    padding (14, 6)
                                    text_font gui.default_font
                                    text_size 15
                                    text_color "#2b1b21"
                                    text_hover_color "#000000"
                                    text_selected_color "#000000"
                                    text_bold (cal_form_recurrence == rec_key)
                                    text_outlines []
                                    action SetVariable("cal_form_recurrence", rec_key)
                            null

                        if cal_form_recurrence == "custom":
                            null height 6
                            hbox:
                                spacing 12
                                text "Repeat every:" font gui.default_font size 15 color "#2b1b21" outlines [] yalign 0.5
                                textbutton "▲":
                                    background _cal_btn_idle_bg
                                    hover_background _cal_btn_hover_bg
                                    selected_background _cal_btn_hover_bg
                                    padding (10, 4)
                                    text_color "#2b1b21"
                                    text_hover_color "#000000"
                                    text_selected_color "#000000"
                                    text_outlines []
                                    action SetVariable("cal_form_interval_num", min(99, cal_form_interval_num + 1))
                                text "[cal_form_interval_num]" font gui.default_font size 16 bold True color "#2b1b21" outlines [] yalign 0.5
                                textbutton "▼":
                                    background _cal_btn_idle_bg
                                    hover_background _cal_btn_hover_bg
                                    selected_background _cal_btn_hover_bg
                                    padding (10, 4)
                                    text_color "#2b1b21"
                                    text_hover_color "#000000"
                                    text_selected_color "#000000"
                                    text_outlines []
                                    action SetVariable("cal_form_interval_num", max(1, cal_form_interval_num - 1))

                                for itype, ilabel in [("days", "Days"), ("weeks", "Weeks"), ("months", "Months")]:
                                    textbutton ilabel:
                                        background Frame(("gui/button/choice_hover_background.png" if cal_form_interval_type == itype else "gui/button/choice_idle_background.png"), 4, 4)
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (12, 6)
                                        text_font gui.default_font
                                        text_size 15
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_bold (cal_form_interval_type == itype)
                                        text_outlines []
                                        action SetVariable("cal_form_interval_type", itype)

                elif cal_form_step == 4:
                    vbox:
                        spacing 12
                        text "Step 4: Category & Details" font gui.default_font bold True size 19 color gui.accent_color outlines [(1, "#00000055", 0, 0)]
                        text "Choosing a category allows Monika to react with tailored greetings, countdowns, and check-ins:" font gui.default_font size 14 color "#2b1b21" outlines []

                        hbox:
                            spacing 30
                            grid 3 3:
                                spacing 8
                                for cat_key, cat_name in [
                                    ("birthday", "Birthday"),
                                    ("holiday", "Holiday"),
                                    ("trip", "Trip"),
                                    ("exam", "Exam"),
                                    ("duedate", "Due Date"),
                                    ("goal", "Goal"),
                                    ("misc", "Misc / Other")
                                ]:
                                    textbutton (("● " + cat_name) if cal_form_category == cat_key else ("○ " + cat_name)):
                                        background _cal_btn_idle_bg
                                        hover_background _cal_btn_hover_bg
                                        selected_background _cal_btn_hover_bg
                                        padding (12, 6)
                                        text_font gui.default_font
                                        text_size 15
                                        text_color "#2b1b21"
                                        text_hover_color "#000000"
                                        text_selected_color "#000000"
                                        text_bold (cal_form_category == cat_key)
                                        text_outlines []
                                        action SetVariable("cal_form_category", cat_key)
                                null
                                null

                            if cal_form_category == "birthday":
                                vbox:
                                    spacing 6
                                    yalign 0.5
                                    text "What year were they born?" font gui.default_font size 15 color "#2b1b21" bold True outlines []
                                    text "Year: [cal_form_birth_year]" font gui.default_font size 15 color "#2b1b21" outlines []
                                    hbox:
                                        spacing 6
                                        textbutton "-":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_birth_year", max(1900, cal_form_birth_year - 1))
                                        textbutton "+":
                                            background _cal_btn_idle_bg
                                            hover_background _cal_btn_hover_bg
                                            selected_background _cal_btn_hover_bg
                                            padding (10, 4)
                                            text_color "#2b1b21"
                                            text_hover_color "#000000"
                                            text_selected_color "#000000"
                                            text_outlines []
                                            action SetVariable("cal_form_birth_year", min(datetime.date.today().year, cal_form_birth_year + 1))

                        null height 4

                        if cal_form_category == "birthday":
                            text "Whose birthday is it?" font gui.default_font size 15 color "#2b1b21" bold True outlines []
                            frame:
                                xfill True
                                ysize 46
                                background _cal_frame_bg
                                padding (12, 8)
                                input:
                                    pixel_width 700
                                    value VariableInputValue("cal_form_meta_extra")
                                    length 40
                                    font gui.default_font
                                    color "#2b1b21"
                                    outlines []
                        elif cal_form_category == "trip":
                            text "Where are you going? (Destination):" font gui.default_font size 15 color "#2b1b21" bold True outlines []
                            frame:
                                xfill True
                                ysize 46
                                background _cal_frame_bg
                                padding (12, 8)
                                input:
                                    pixel_width 700
                                    value VariableInputValue("cal_form_meta_extra")
                                    length 40
                                    font gui.default_font
                                    color "#2b1b21"
                                    outlines []


            if cal_form_error:
                text "[cal_form_error]":
                    font gui.default_font
                    size 15
                    color "#cc0000"
                    bold True
                    outlines []

            # Navigation Buttons
            hbox:
                xfill True
                if cal_form_step > 1:
                    textbutton "← Back":
                        background _cal_btn_idle_bg
                        hover_background _cal_btn_hover_bg
                        selected_background _cal_btn_hover_bg
                        padding (20, 8)
                        text_font gui.default_font
                        text_size 16
                        text_color "#2b1b21"
                        text_hover_color "#000000"
                        text_selected_color "#000000"
                        text_outlines []
                        action [SetVariable("cal_form_error", ""), SetVariable("cal_form_step", cal_form_step - 1)]
                else:
                    null

                if cal_form_step < 4:
                    textbutton "Next →":
                        xalign 1.0
                        background _cal_btn_idle_bg
                        hover_background _cal_btn_hover_bg
                        selected_background _cal_btn_hover_bg
                        padding (20, 8)
                        text_font gui.default_font
                        text_size 16
                        text_color "#2b1b21"
                        text_hover_color "#000000"
                        text_selected_color "#000000"
                        text_outlines []
                        action [SetVariable("cal_form_error", ""), SetVariable("cal_form_step", cal_form_step + 1)]
                else:
                    textbutton "✔ Save Event":
                        xalign 1.0
                        background _cal_btn_idle_bg
                        hover_background _cal_btn_hover_bg
                        selected_background _cal_btn_hover_bg
                        padding (20, 8)
                        text_font gui.default_font
                        text_size 16
                        text_bold True
                        text_color "#2b1b21"
                        text_hover_color "#000000"
                        text_selected_color "#000000"
                        text_outlines []
                        action Function(custom_cal_submit_form)


init python:
    def custom_cal_submit_form():
        global cal_form_error
        if not store.cal_form_name.strip():
            store.cal_form_error = "Please enter an event name in Step 1!"
            store.cal_form_step = 1
            renpy.restart_interaction()
            return

        meta = {}
        if store.cal_form_category == "birthday":
            meta["person_name"] = store.cal_form_meta_extra.strip() or "someone special"
            meta["birth_year"] = store.cal_form_birth_year
        elif store.cal_form_category == "trip":
            meta["destination"] = store.cal_form_meta_extra.strip() or "somewhere fun"

        s_tuple = (store.cal_form_s_year, store.cal_form_s_month, store.cal_form_s_day)
        if store.cal_form_is_multiday:
            e_tuple = (store.cal_form_e_year, store.cal_form_e_month, store.cal_form_e_day)
        else:
            e_tuple = s_tuple

        custom_cal_create_event(
            name=store.cal_form_name,
            start_date=s_tuple,
            end_date=e_tuple,
            is_multiday=store.cal_form_is_multiday,
            recurrence=store.cal_form_recurrence,
            custom_interval_type=store.cal_form_interval_type,
            custom_interval_num=store.cal_form_interval_num,
            category=store.cal_form_category,
            meta=meta,
            icon=store.cal_form_icon
        )

        if store.custom_cal_active_instance:
            store.custom_cal_active_instance._setupDayButtons()

        renpy.hide_screen("mas_custom_date_add_modal")
        renpy.end_interaction(True)
