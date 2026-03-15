"""
Scenario OmniLife: 7-Day Life Scenario (72 tasks)

Based on OmniLife-7D.md design:
- Day 1 (Mon): 10 tasks - Busy Monday + Preference anchors
- Day 2 (Tue): 11 tasks - Memory misleading + Meeting A tracking #2
- Day 3 (Wed): 11 tasks - Spatiotemporal conflicts + Address reuse
- Day 4 (Thu): 8 tasks - Budget stress test + Cross-app chains
- Day 5 (Fri): 8 tasks - Meeting B + Ask-before-buy trap
- Day 6 (Sat): 11 tasks - Weekend tasks + Preference constraints
- Day 7 (Sun): 13 tasks - Weekly closure + Full-week review

Core capabilities:
- [REF] Reference resolution across days
- [PRE] Preference learning and enforcement
- [CON] Conflict detection (time/space/budget)
- [CAU] Causal consistency maintenance
"""

from absl import logging
from typing import Optional
import random

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.seven_day_base import SevenDayScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioOmniLife_7Day")
class ScenarioOmniLife7DayEvaluator(SevenDayScenarioEvaluator):
    """
    Scenario OmniLife: 7-Day Complete Life Scenario
    
    72 tasks across 7 days, testing:
    - Cross-day reference resolution
    - User preference learning and alignment
    - Spatiotemporal conflict handling
    - Budget constraint enforcement
    - Multi-meeting progress tracking
    """
    
    app_names = (
        "clock", "simple calendar pro", "simple sms messenger", "markor",
        "chrome", "pro expense", "opentracks", "audio recorder", "files",
        "camera", "contacts", "tasks", "broccoli recipe", "retro music"
    )
    
    scenario_id = "OmniLife"
    complexity = 5.0
    
    def __init__(self, params: dict = None):
        """Initialize OmniLife 7-Day Scenario"""
        if params is None:
            params = {}
        
        # Generate parameters
        if 'generated_params' not in params:
            generated_params = self.generate_random_params(params.get('seed'))
            params['generated_params'] = generated_params
        else:
            generated_params = params['generated_params']
        
        # Set scenario metadata
        scenario_params = {
            'scenario_id': 'OmniLife',
            'name': 'OmniLife 7-Day Complete Life',
            'start_date': '2026-01-19',  # Monday
            'total_max_steps': 720,  # 72 tasks * ~10 steps
            'generated_params': generated_params,
            'reset_mode': params.get('reset_mode', False),   # ⚡ Reset mode support
            'clarity_level': params.get('clarity_level', None),
        }
        
        super().__init__(scenario_params)
        
        # Initialize 7 days
        self._init_days()
        
        # Add all subtasks
        self._add_all_subtasks(generated_params)
    
    def _init_days(self):
        """Initialize 7-day configuration"""
        dates = [
            ('2026-01-19', 'Monday'),
            ('2026-01-20', 'Tuesday'),
            ('2026-01-21', 'Wednesday'),
            ('2026-01-22', 'Thursday'),
            ('2026-01-23', 'Friday'),
            ('2026-01-24', 'Saturday'),
            ('2026-01-25', 'Sunday'),
        ]
        
        for day_idx, (date, day_name) in enumerate(dates):
            self.add_day(day_idx, date, day_name)
    
    @classmethod
    def generate_random_params(cls, seed: Optional[int] = None) -> dict:
        """Generate random parameters for the scenario"""
        if seed is not None:
            random.seed(seed)
        
        # Basic shared parameters
        # ✅ Ensure the username does not conflict with any attendees:
        # - Meeting A: John, Bob, Nierson, Hession
        # - Seminar: Alice, Charlie, Diana, Frank
        # - Meeting B: Tom, Jerry, Mike, Lisa
        # - Avoid Michael (confusable with Mike) and Emily (conflicts with the distractor Emily Davis)
        user_names = ['David', 'Sarah', 'Jessica', 'Ryan', 'Alex']
        user_name = random.choice(user_names)
        
        # Meeting A attendees (Day 1)
        meeting_a_attendees = ['John', 'Bob', 'Nierson', 'Hession']
        meeting_a_full = [f"{name} Smith" if name == 'John' else 
                          f"{name} Johnson" if name == 'Bob' else
                          f"{name} Williams" if name == 'Nierson' else
                          f"{name} Brown" for name in meeting_a_attendees]
        
        # Seminar attendees (Day 2, different group)
        seminar_attendees = ['Alice', 'Charlie', 'Diana', 'Frank']
        seminar_full = [f"{name} Davis" for name in seminar_attendees]
        
        # Meeting B attendees (Day 5, different from A and seminar)
        meeting_b_attendees = ['Tom', 'Jerry', 'Mike', 'Lisa']
        meeting_b_full = [f"{name} Wilson" for name in meeting_b_attendees]
        
        return {
            'seed': seed,
            'user_name': user_name,
            'meeting_a': {
                'title': 'Company Weekly Meeting',
                'location': 'Conference Room A',
                'attendees': meeting_a_attendees,
                'attendees_full': meeting_a_full,
            },
            'seminar': {
                'title': 'Weekly Seminar',  # Similar name trap!
                'location': 'Room B',
                'attendees': seminar_attendees,
                'attendees_full': seminar_full,
            },
            'meeting_b': {
                'title': 'Weekly Sync',  # Similar name trap!
                'location': 'Meeting Room 1',
                'attendees': meeting_b_attendees,
                'attendees_full': meeting_b_full,
                'time': '10:00',  # Monday 10:00 AM
            },
            'alarm': {
                'original_hour': 6,
                'original_minute': 50,
                'shift_minutes': 10,
                'new_hour': 6,
                'new_minute': 40,
            },
            'products': {
                'table': {'sku': 'B07FM3WKJ8', 'name': 'Outdoor Patio Folding Side Table green', 'price': 54.99},
                'usb_drive': {'sku': 'B00J2FALDK', 'name': 'SanDisk Cruzer Glide 16GB', 'price': 119.99},
                'supplies': {'sku': 'B074QVN413', 'name': 'Tide PODS', 'price': 150.00},
                'meat_alt': {'sku': 'B07KB88W7G', 'name': 'Plant-based protein', 'price': 135.00},
            },
        }
    
    # ==================== Environment Initialization ====================
    
    _environment_initialized = False
    _contacts_initialized = False
    
    def initialize_task(self, env):
        """
        Initialize the 7-day scenario environment for OmniLife
        
        Performs batch initialization for all days:
        1. Clear and create initial alarms (for W1-01)
        2. Create calendar events (for W1-02, W1-03, W2-01, W5-01, etc.)
        3. Create contacts (for all SMS tasks)
        4. Set initial preferences
        5. Clear app data (Markor, Expense, OpenTracks, Audio Recorder, Tasks)
        
        ⚠️ IMPORTANT: This method should only be called ONCE at the start of the scenario.
        Data created in Day 1 must persist through Day 7 (e.g., SMS conversations, audio recordings).
        """
        # ⚡ Reset mode: skip batch initialization; initialize each task independently
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization for OmniLife")
            logging.info("   Each task will be initialized independently before execution")
            super().initialize_task(env)  # Call only the parent class's log-printing portion
            # Ensure timezone is UTC
            from scendroid.env import adb_utils
            try:
                adb_utils.set_root_if_needed(env.controller)
                adb_utils.issue_generic_request(
                    ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'], env.controller
                )
                adb_utils.issue_generic_request(
                    ['shell', 'setprop', 'persist.sys.timezone', 'UTC'], env.controller
                )
                logging.info("   ✅ Timezone confirmed: UTC")
            except Exception as e:
                logging.warning(f"   ⚠️  Could not set timezone: {e}")
            return

        # Prevent duplicate initialization (protect cross-day data)
        if self._environment_initialized:
            logging.warning("⚠️ Environment already initialized - skipping to preserve cross-day data")
            return
        
        super().initialize_task(env)
        
        logging.info("🔧 Batch initializing OmniLife scenario environment...")
        logging.info("   ⚠️ This initialization happens ONLY ONCE at scenario start")
        
        # ⚠️ critical fix: ensure timezone is UTC first during scenario initialization
        # this fixes the Calendar displaying incorrect time issue
        from scendroid.env import adb_utils
        logging.info("   🌍 ensuring device timezone is UTC...")
        try:
            # set timezone to UTC (using ScenDroid standard method)
            adb_utils.set_root_if_needed(env.controller)
            
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            
            # also set system properties
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            
            logging.info("   ✅ timezone confirmed as UTC")
        except Exception as e:
            logging.warning(f"   ⚠️  Could not set timezone: {e}")
        
        try:
            # 1. Create initial alarms (for W1-01 adjustment)
            self._setup_clocks(env)
            
            # 2. Create calendar events (for Day 1, Day 2, Day 5 tasks)
            self._setup_calendar_events(env)
            
            # 3. Create contacts (for SMS tasks)
            self._setup_contacts(env)
            
            # 4. Clean up app data
            self._cleanup_app_data(env)
            
            # 4.5. Clean up Tasks (for W3-03, W6-01 tasks)
            self._cleanup_tasks(env)
            
            # 4.6. Clean up Audio Recorder (for W2-02, W2-04, W3-07 tasks)
            self._cleanup_audiorecorder(env)
            
            # 4.7. Clean up Camera and Files (must be done before creating images)
            self._cleanup_camera_files(env)
            
            # 4.8. Clean up Retro Music (for W2-06 playlist tasks)
            # ⚠️ IMPORTANT: This calls clear_internal_storage, which clears Download directory!
            self._cleanup_retromusic(env)
            
            # 4.9. Clean up OpenTracks (for W2-06, W6-06 activity tracking)
            self._cleanup_opentracks(env)
            
            # 5. Setup Expense with historical data (for W3-11, W4-01, etc.)
            self._setup_expense(env)
            
            # 6. Setup system initial state (Bluetooth OFF, DND OFF)
            self._setup_system_state(env)
            
            # 7. Set initial preferences
            self._setup_preferences()
            
            # 8. Setup Broccoli recipes (for W6-02)
            # 🔧 Fix: Create both egg and light recipe simultaneously
            self._setup_broccoli_recipes(env)
            
            # 9. 🆕 Setup Tasks picnic checklist (for W7-01)
            self._setup_tasks_picnic(env)
            
            # 10. 🆕 Setup OpenTracks Saturday walk (for W6-09)
            self._setup_opentracks_saturday(env)
            
            # 11. 🆕 Setup OpenTracks weekly history (for W7-07)
            self._setup_opentracks_weekly(env)
            
            # ========== CREATE FILES (MUST be after _cleanup_retromusic!) ==========
            # ⚠️ _cleanup_retromusic calls clear_internal_storage, which clears Download
            # All image creation must happen AFTER that to avoid being deleted
            
            # 12. Create breakfast receipt image (for W2-03) - after cleanup
            self._create_breakfast_receipt(env)
            
            # 13. 🆕 Create breakfast photo (for W6-05)
            self._create_breakfast_photo(env)
            
            # 13.5. 🆕 Setup photos for W7-08 (fully reuse the batch initialization from E-F8)
            self._setup_photos_for_w7_08(env)
            
            # 14. Create trip info image (for W3-01)
            self._create_trip_info_image(env)
            
            # 15. Create return flight image (for W4-06)
            self._create_return_flight_image(env)
            
            # 16. Create dinner receipt photo (for W3-09)
            self._create_dinner_receipt_photo(env)
            
            # Note: All Calendar meetings are created in _setup_calendar_events() (step 2)
            # This includes:
            # - Morning Meeting (W3-02)
            # - Keynote Speech (W4-03, W4-05)
            # - Team Discussion (W4-04)
            # - Mountain Picnic (W7-02)
            
            # Note: Hotel Front Desk contact is NOT created here
            # It will be created by user in W3-06 task (before W3-07 needs it)
            
            # Note: Chrome login is handled by seven_day_base._initialize_shopping_subtask()
            # when Shopping task starts, not during batch initialization
            
            # Mark initialization as complete (prevent subsequent redundant cleanup)
            self._environment_initialized = True
            
            logging.info("✅ Batch initialization complete")
            logging.info("   ✅ Cross-day data will be preserved throughout the 7-day scenario")
            
        except Exception as e:
            logging.error(f"❌ Batch initialization error: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def _setup_clocks(self, env):
        """Create initial alarms (for W1-01 adjustment)"""
        logging.info("   ⏰ Creating initial alarms...")
        
        from scendroid.env import adb_utils
        import time
        
        # Clear existing alarm data
        try:
            logging.info("      🗑️  Clearing existing alarms...")
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
            logging.info("      ✅ Alarm data cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # Get alarm parameters
        alarm = self.generated_params.get('alarm', {})
        original_hour = alarm.get('original_hour', 6)
        original_minute = alarm.get('original_minute', 50)
        
        # Create weekday alarm (to be adjusted in W1-01)
        self._set_alarm_with_days(env, hour=original_hour, minute=original_minute, 
                                  message="Work", days=[2, 3, 4, 5, 6])  # Mon-Fri
        time.sleep(1.0)
        
        # Create weekend alarm (should not be changed in W1-01)
        self._set_alarm_with_days(env, hour=9, minute=30, 
                                  message="Weekend", days=[1, 7])  # Sat-Sun
        time.sleep(1.0)
        
        # Create sleep alarm (daily)
        self._set_alarm_with_days(env, hour=22, minute=30, 
                                  message="Sleep", days=[1, 2, 3, 4, 5, 6, 7])
        time.sleep(1.0)
        
        logging.info(f"   ✅ Alarms created (Work: {original_hour:02d}:{original_minute:02d})")
    
    def _set_alarm_with_days(self, env, hour: int, minute: int, message: str, days: list):
        """Set alarm with repeat days"""
        from scendroid.env import adb_utils
        import time
        
        safe_message = message.replace(' ', '_')
        
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', str(hour),
            '--ei', 'android.intent.extra.alarm.MINUTES', str(minute),
            '--es', 'android.intent.extra.alarm.MESSAGE', safe_message,
        ]
        
        if days:
            days_str = ','.join(str(d) for d in days)
            cmd.extend(['--eia', 'android.intent.extra.alarm.DAYS', days_str])
        
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
    
    def _setup_calendar_events(self, env):
        """
        Create ALL calendar events for the 7-day scenario
        
        🔧 Fix: Create all required calendar events in one go to avoid scattered creation
        
        Created events:
        1. Day 1 (Mon 01-19) 09:00: Company Weekly Meeting (W1-02, W1-03, W1-04)
        2. Day 3 (Wed 01-21) 10:00: Morning Meeting (W3-02 — conflicts with Flight)
        3. Day 4 (Thu 01-22) 14:00: Keynote Speech (W4-03, W4-05)
        4. Day 4 (Thu 01-22) 18:00: Team Discussion (W4-04 — conflicts with exercise)
        5. Day 7 (Sun 01-25) 10:00: Mountain Picnic (W7-02)
        6. Day 8 (Mon 01-26) 10:00: Weekly Sync (W5-01, W5-02)
        """
        logging.info("   📅 Creating ALL calendar events...")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime, timedelta
        import calendar as cal_module
        import time
        from scendroid.env import adb_utils
        
        # ✅ fix 1: use clear_app_data to fully reset Calendar app (including view settings)
        adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
        time.sleep(1.0)
        
        # launch Calendar once and return, ensure app initialization complete (skip first-run wizard)
        adb_utils.start_activity(
            "com.simplemobiletools.calendar.pro/.activities.MainActivity",
            None,  # extra_args
            env.controller
        )
        time.sleep(2.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        # ✅ fix 2: re-set timezone after clearing app data (prevent timezone reset)
        logging.info("      🌍 re-confirming device timezone is UTC...")
        adb_utils.set_root_if_needed(env.controller)
        
        adb_utils.issue_generic_request(
            ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
            env.controller
        )
        
        adb_utils.issue_generic_request(
            ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
            env.controller
        )
        
        # Clear existing events
        calendar_utils.clear_calendar_db(env)
        
        # Base date: Monday 2026-01-19
        base_date = datetime(2026, 1, 19, 0, 0, 0)
        
        # Get parameters
        meeting_a = self.generated_params.get('meeting_a', {})
        meeting_a_title = meeting_a.get('title', 'Company Weekly Meeting')
        meeting_a_location = meeting_a.get('location', 'Conference Room A')
        meeting_a_attendees = meeting_a.get('attendees_full', ['John Smith', 'Bob Johnson'])
        
        meeting_b = self.generated_params.get('meeting_b', {})
        meeting_b_title = meeting_b.get('title', 'Weekly Sync')
        meeting_b_location = meeting_b.get('location', 'Meeting Room 1')
        meeting_b_attendees = meeting_b.get('attendees_full', ['Tom Wilson'])
        
        seminar = self.generated_params.get('seminar', {})
        seminar_attendees = seminar.get('attendees_full', ['Alice Davis', 'Charlie Davis'])
        
        user_name = self.generated_params.get('user_name', 'Emily')
        
        events = []
        
        # ========== Event 1: Day 1 (Mon 01-19) 09:00 - Company Weekly Meeting ==========
        meeting_a_dt = base_date.replace(hour=9, minute=0)
        meeting_a_start_ts = cal_module.timegm(meeting_a_dt.timetuple())
        meeting_a_end_ts = meeting_a_start_ts + (60 * 60)  # 1 hour
        
        attendees_str_a = f"Attendees: {user_name}, " + ", ".join(meeting_a_attendees)
        event1 = sqlite_schema_utils.CalendarEvent(
            start_ts=meeting_a_start_ts,
            end_ts=meeting_a_end_ts,
            title=meeting_a_title,
            location=meeting_a_location,
            description=attendees_str_a,
        )
        events.append(event1)
        logging.info(f"   📌 Event 1: Day 1 (Mon 01-19) 09:00 - {meeting_a_title}")
        
        # ========== Event 2: Day 3 (Wed 01-21) 10:00 - Morning Meeting (W3-02 conflict) ==========
        day3 = base_date + timedelta(days=2)  # Wednesday
        morning_meeting_dt = day3.replace(hour=10, minute=0)
        morning_meeting_start_ts = cal_module.timegm(morning_meeting_dt.timetuple())
        morning_meeting_end_ts = morning_meeting_start_ts + (60 * 60)  # 1 hour
        
        event2 = sqlite_schema_utils.CalendarEvent(
            start_ts=morning_meeting_start_ts,
            end_ts=morning_meeting_end_ts,
            title="Morning Meeting",
            location="Office",
            description="Team sync meeting",
        )
        events.append(event2)
        logging.info(f"   📌 Event 2: Day 3 (Wed 01-21) 10:00 - Morning Meeting (conflicts with Flight in W3-02)")
        
        # ========== Event 3: Day 4 (Thu 01-22) 14:00 - Keynote Speech ==========
        day4 = base_date + timedelta(days=3)  # Thursday
        keynote_dt = day4.replace(hour=14, minute=0)
        keynote_start_ts = cal_module.timegm(keynote_dt.timetuple())
        keynote_end_ts = keynote_start_ts + (60 * 60)  # 1 hour
        
        event3 = sqlite_schema_utils.CalendarEvent(
            start_ts=keynote_start_ts,
            end_ts=keynote_end_ts,
            title="Keynote Speech",
            location="Main Hall",
            description="Conference keynote presentation",
        )
        events.append(event3)
        logging.info(f"   📌 Event 3: Day 4 (Thu 01-22) 14:00 - Keynote Speech (for W4-03, W4-05)")
        
        # ========== Event 4: Day 4 (Thu 01-22) 18:00 - Team Discussion (W4-04 conflict) ==========
        team_discussion_dt = day4.replace(hour=18, minute=0)
        team_discussion_start_ts = cal_module.timegm(team_discussion_dt.timetuple())
        team_discussion_end_ts = team_discussion_start_ts + (60 * 60)  # 1 hour
        
        event4 = sqlite_schema_utils.CalendarEvent(
            start_ts=team_discussion_start_ts,
            end_ts=team_discussion_end_ts,
            title="Team Discussion",
            location="Conference Room",
            description="Project review meeting",
        )
        events.append(event4)
        logging.info(f"   📌 Event 4: Day 4 (Thu 01-22) 18:00 - Team Discussion (conflicts with exercise in W4-04)")
        
        # ========== Event 5: Day 7 (Sun 01-25) 10:00 - Mountain Picnic ==========
        day7 = base_date + timedelta(days=6)  # Sunday
        picnic_dt = day7.replace(hour=10, minute=0)
        picnic_start_ts = cal_module.timegm(picnic_dt.timetuple())
        picnic_end_ts = picnic_start_ts + (2 * 60 * 60)  # 2 hours
        
        attendees_str_picnic = f"Attendees: {user_name}, " + ", ".join(seminar_attendees)
        event5 = sqlite_schema_utils.CalendarEvent(
            start_ts=picnic_start_ts,
            end_ts=picnic_end_ts,
            title="Mountain Picnic",
            location="East Valley Trail",
            description=attendees_str_picnic,
        )
        events.append(event5)
        logging.info(f"   📌 Event 5: Day 7 (Sun 01-25) 10:00 - Mountain Picnic (for W7-02)")
        
        # ========== Event 6: Day 8 (Mon 01-26) 10:00 - Weekly Sync (Meeting B) ==========
        next_monday = base_date + timedelta(days=7)
        meeting_b_dt = next_monday.replace(hour=10, minute=0)
        meeting_b_start_ts = cal_module.timegm(meeting_b_dt.timetuple())
        meeting_b_end_ts = meeting_b_start_ts + (60 * 60)  # 1 hour
        
        attendees_str_b = f"Attendees: {user_name}, " + ", ".join(meeting_b_attendees)
        event6 = sqlite_schema_utils.CalendarEvent(
            start_ts=meeting_b_start_ts,
            end_ts=meeting_b_end_ts,
            title=meeting_b_title,
            location=meeting_b_location,
            description=attendees_str_b,
        )
        events.append(event6)
        logging.info(f"   📌 Event 6: Day 8 (Mon 01-26) 10:00 - {meeting_b_title}")
        
        # Add all events to database
        calendar_utils.add_events(events, env)
        time.sleep(2.0)
        
        logging.info(f"   ✅ All {len(events)} calendar events created successfully")
    
    def _setup_contacts(self, env):
        """Create contacts for SMS tasks"""
        # Prevent duplicate cleanup (protect cross-day SMS data)
        if self._contacts_initialized:
            logging.warning("   ⚠️ Contacts already initialized - skipping to preserve SMS data")
            return
        
        logging.info("   👥 Creating contacts...")
        logging.info("   ⚠️ This clears existing SMS data - only runs once at scenario start")
        
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        import time
        
        # Clear existing contacts
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        # Clear existing SMS
        try:
            from scendroid.task_evals.common_validators import sms_validators
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("      ✅ SMS database cleared")
            
            # ✅ Important: Open and close the SMS app to refresh the UI (refer to scenario_c/e/d/b/a implementations)
            logging.info("      📱 Refreshing SMS UI...")
            
            # Step 1: Force-stop the SMS app (clear UI cache)
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            
            # Step 2: Open the SMS app
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)  # etc., wait for the app to fully load
            
            # Step 3: Press the BACK key four times to ensure returning to the home screen (conversation → contact → home screen → exit)
            logging.info("      📱 pressing back to return to home screen...")
            for _ in range(4):  # press back button multiple times to ensure return to home screen
                adb_utils.issue_generic_request(
                    ["shell", "input", "keyevent", "KEYCODE_BACK"],
                    env.controller
                )
                time.sleep(0.3)
            
            # Step 4: Press the HOME key to exit to the desktop
            logging.info("      📱 pressing Home to exit to desktop...")
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
            logging.info("      ✅ SMS UI refreshed (force stop + open + back button + Home key)")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear SMS: {e}")
        
        # Get attendees from parameters
        meeting_a = self.generated_params.get('meeting_a', {})
        seminar = self.generated_params.get('seminar', {})
        meeting_b = self.generated_params.get('meeting_b', {})
        
        meeting_a_attendees_full = meeting_a.get('attendees_full', [])
        seminar_attendees_full = seminar.get('attendees_full', [])
        meeting_b_attendees_full = meeting_b.get('attendees_full', [])
        
        # Create contacts for all attendees
        contacts = []
        
        # Meeting A attendees (phone 555-01xx)
        for i, name in enumerate(meeting_a_attendees_full):
            contacts.append({"name": name, "phone": f"555-01{i+1:02d}"})
        
        # Seminar attendees (phone 555-02xx)
        for i, name in enumerate(seminar_attendees_full):
            contacts.append({"name": name, "phone": f"555-02{i+1:02d}"})
        
        # Meeting B attendees (phone 555-03xx)
        for i, name in enumerate(meeting_b_attendees_full):
            contacts.append({"name": name, "phone": f"555-03{i+1:02d}"})
        
        # ✅ External contact (for W3-06, W4-07)
        contacts.append({"name": "Sarah Miller", "phone": "555-0801"})
        
        logging.info(f"   📞 Adding {len(contacts)} contacts...")
        
        successfully_added = 0
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name')
            phone = contact.get('phone')
            if not name or not phone:
                continue
            
            # Retry mechanism
            for attempt in range(2):
                try:
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.0)
                    
                    contacts_utils.add_contact(
                        name,
                        phone,
                        env.controller,
                        ui_delay_sec=2.0
                    )
                    logging.info(f"      ✅ Added {i}/{len(contacts)}: {name} ({phone})")
                    successfully_added += 1
                    time.sleep(2.0)
                    break
                    
                except Exception as e:
                    if attempt == 1:
                        logging.error(f"      ❌ Failed to add '{name}' (after 2 attempts): {e}")
                    else:
                        logging.warning(f"      ⚠️  Attempt {attempt + 1} failed for '{name}': {e}")
                    time.sleep(1.0)
        
        logging.info(f"   ✅ {successfully_added}/{len(contacts)} contacts created")
        
        # ✅ Refresh Contacts UI (similar to SMS refresh)
        try:
            logging.info("      📱 Refreshing Contacts UI...")
            
            # step1: open Contacts app
            adb_utils.start_activity(
                "com.simplemobiletools.contacts.pro/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)  # etc., wait for the app to fully load
            
            # Step 2: Press the BACK key three times to refresh and exit
            logging.info("      📱 Pressing back button to refresh and exit...")
            for _ in range(3):
                adb_utils.issue_generic_request(
                    ["shell", "input", "keyevent", "KEYCODE_BACK"],
                    env.controller
                )
                time.sleep(0.3)
            
            logging.info("      ✅ Contacts UI refreshed")
            
        except Exception as e:
            logging.warning(f"      ⚠️ Could not refresh Contacts UI: {e}")
        
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        # Mark contacts as initialized
        self._contacts_initialized = True
        logging.info("   ✅ Contacts created")
    
    def _cleanup_app_data(self, env):
        """Clean up app data"""
        logging.info("   🗑️  Cleaning up app data...")
        
        from scendroid.env import adb_utils, device_constants
        from scendroid.utils import file_utils
        import time
        
        # 1. Markor - only clear directory
        try:
            logging.info(f"      📁 Clearing Markor directory...")
            markor_dir = device_constants.MARKOR_DATA
            
            cmd = ['shell', 'mkdir', '-p', markor_dir]
            adb_utils.issue_generic_request(cmd, env.controller)
            
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info(f"      ✅ Markor directory cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Markor cleanup failed: {e}")
        
        logging.info("   ✅ App data cleaned (Markor only, Expense handled separately)")
    
    def _setup_expense(self, env):
        """Setup Expense and add history records (refer to scenario_d)
        
        OmniLife scenario description:
        - base_date = 2026-01-19 (Day 1, Monday)
        - Day 1 (Jan 19): Add history expense of approximately $48.99
        - Day 2 (Jan 20): User adds $6.80 for breakfast (W2-03)
        - Day 3 (Jan 21): User adds $304.99 for Taxi ($35) + Hotel ($250) + USB ($19.99) (W3-10)
        - W3-11 (Day 3, 22:30): Query expenses for the most recent 3 days
        
        History expense design:
        - Days -6 to -3 (Jan 13–16): Distractors, approximately $80.00
        - Day -2 (Jan 17): Distractor, approximately $15.00
        - Day-1 (Jan 18): historical expense, approx. $25.00
        - Day 1 (Jan 19): historical expense, approx. $48.99
        - Day 2 (Jan 20): $0 (user added $6.80 in W2-03)
        - Day 3 (Jan 21): $0 (user added $304.99 in W3-10)
        
        W3-11 expected_total = $25.00 (Day-1) + $48.99 (Day 1 historical) + $6.80 (Day 2 user) + $304.99 (Day 3 user) = $385.78
        """
        logging.info("   💰 setup Expense and add historical records...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env.setup_device import apps
        from datetime import datetime, timedelta
        import time
        import random
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # 1. check if database exists
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database does not exist, initializing...")
                apps.ExpenseApp.setup(env)
            
            # 2. Clear existing expenses
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("      ✅ Expense data cleared")
            
            # 3. Get baseline date (Day 1 = 2026-01-19)
            base_date_str = self.context.base_date or '2026-01-19'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            
            all_expenses = []
            
            expense_names = ['Coffee', 'Lunch', 'Dinner', 'Snacks', 'Metro', 'Taxi', 'Supplies', 'Parking', 'Breakfast']
            categories = [4, 4, 4, 4, 6, 6, 7, 6, 4]  # Food=4, Transport=6, Others=7
            
            # 4. Add distractor expenses (Day-6 to Day-3, approx. $80.00)
            distractor_days_far = [6, 5, 4, 3]  # Jan 13–16
            distractor_amount_far = 80.00
            per_day_far = distractor_amount_far / len(distractor_days_far)
            
            for days_ago in distractor_days_far:
                num_records = random.randint(1, 2)
                day_total = per_day_far
                
                for j in range(num_records):
                    if j == num_records - 1:
                        amount = day_total
                    else:
                        amount = day_total * random.uniform(0.4, 0.6)
                        day_total -= amount
                    
                    expense_date = base_date - timedelta(days=days_ago)
                    amount_cents = int(amount * 100)
                    date_ts = int(expense_date.timestamp()) * 1000
                    
                    expense = sqlite_schema_utils.Expense(
                        name=random.choice(expense_names),
                        amount=amount_cents,
                        category=random.choice(categories),
                        created_date=date_ts,
                        modified_date=date_ts,
                    )
                    all_expenses.append(expense)
            
            # 5. Add Day-2 distractor expense (Jan 17, approx. $15.00)
            expense_date = base_date - timedelta(days=2)
            amount_cents = int(15.00 * 100)
            date_ts = int(expense_date.timestamp()) * 1000
            
            expense = sqlite_schema_utils.Expense(
                name="Parking",
                amount=amount_cents,
                category=6,  # Transport
                created_date=date_ts,
                modified_date=date_ts,
            )
            all_expenses.append(expense)
            
            # 6. Add Day-1 historical expense (Jan 18, approx. $25.00)
            # This will be included in "recent 3 days"
            expense_date = base_date - timedelta(days=1)
            
            # Split into two records
            amounts_day_minus_1 = [12.50, 12.50]
            names_day_minus_1 = ["Lunch", "Coffee"]
            cats_day_minus_1 = [4, 4]
            
            for amount, name, cat in zip(amounts_day_minus_1, names_day_minus_1, cats_day_minus_1):
                amount_cents = int(amount * 100)
                date_ts = int(expense_date.timestamp()) * 1000
                
                expense = sqlite_schema_utils.Expense(
                    name=name,
                    amount=amount_cents,
                    category=cat,
                    created_date=date_ts,
                    modified_date=date_ts,
                )
                all_expenses.append(expense)
            
            # 7. Add Day 1 historical expense (Jan 19, Monday)
            # This will be included in "recent 3 days"
            # 🆕 Add Table ($54.99) for W4-02
            expense_date = base_date
            
            # Add Table $54.99
            amount_cents = int(54.99 * 100)
            date_ts = int(expense_date.timestamp()) * 1000
            
            expense = sqlite_schema_utils.Expense(
                name="Table",
                amount=amount_cents,
                category=7,  # Others/Furniture
                created_date=date_ts,
                modified_date=date_ts,
            )
            all_expenses.append(expense)
            
            # Note: Expenses for Day 2 and Day 3 are manually added by the user in the task
            # Day 2 (Jan 20, Tuesday): W2-03 added $6.80 (Campus Breakfast)
            # Day 3 (Jan 21, Wednesday): W3-10 added $304.99 (Taxi $35 + Hotel $250 + USB $19.99)
            # Day 4 (Jan 22, Thursday): User query
            
            # 8. Insert historical expenses
            if all_expenses:
                sqlite_utils.insert_rows_to_remote_db(
                    rows=all_expenses,
                    exclude_key='expense_id',
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    app_name=_APP_NAME,
                    env=env,
                )
                logging.info(f"      ✅ added {len(all_expenses)} historical expense records")
                logging.info(f"         - Distractors (Day-6 to Day-3): $80.00")
                logging.info(f"         - Distractor (Day-2): $15.00")
                logging.info(f"         - Recent 3-day historical (Day-1): $25.00")
                logging.info(f"         - Day 1 (Monday): $54.99 (Table)")
                logging.info(f"         - Day 2 (Tuesday) added by user: $6.80 + $35 + $250 = $291.80 (W2-03)")
                logging.info(f"         - Day 3 (Wednesday) added by user: $19.99 (W3-10)")
                logging.info(f"         - W4-01 Last 2 days (Tue+Wed): $291.80 + $19.99 = $311.79")
                logging.info(f"         - W4-02 Last 3 days (Mon+Tue+Wed): $54.99 + $291.80 + $19.99 = $366.78")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Expense setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_tasks(self, env):
        """
        Cleanup Tasks app database and skip the initialize configuration screen (refer to scenario_d)
        
        🔧 Fix: First launch app to create database, then cleanup data
        """
        logging.info("   📝 cleanup Tasks...")
        
        from scendroid.task_evals.information_retrieval import task_app_utils
        from scendroid.env import adb_utils
        import time
        
        try:
            # 1. Launch and close the Tasks app first (ensure database creation + skip initialize configuration screen)
            logging.info("      Launch and close Tasks app (create database + skip initialize)...")
            try:
                adb_utils.launch_app("tasks", env.controller)
                time.sleep(2.0)
                adb_utils.close_app("tasks", env.controller)
                time.sleep(0.5)
            except Exception as e:
                logging.debug(f"      Launch/close app: {e}")
            
            # 2. cleanup Tasks database
            logging.info("      cleanup Tasks database...")
            task_app_utils.clear_task_db(env)
            logging.info("      ✅ Tasks database cleared")
            
            # 3. return to home screen
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Tasks cleaned and initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Tasks cleanup failed: {e}")
            import traceback
            logging.debug(traceback.format_exc())
    
    def _setup_system_state(self, env):
        """Setup system initial status (refer to scenario_d)"""
        logging.info("   ⚙️ Setup system initial status...")
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # 1. Turn off Bluetooth
            adb_utils.toggle_bluetooth(env.controller, 'off')
            logging.info("      ✅ Bluetooth is turned off")
            
            # 2. Turn off Do Not Disturb
            # Setup zen_mode = 0 (OFF) — simultaneously setup global and secure settings
            adb_utils.issue_generic_request([
                'shell', 'settings', 'put', 'global', 'zen_mode', '0'
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'settings', 'put', 'secure', 'zen_mode', '0'
            ], env.controller)
            # Additionally use cmd notification to disable DND
            adb_utils.issue_generic_request([
                'shell', 'cmd', 'notification', 'set_dnd', 'off'
            ], env.controller)
            logging.info("      ✅ Do Not Disturb has been disabled")
            
            time.sleep(1.0)
            
        except Exception as e:
            logging.warning(f"   ⚠️ System status setup failed: {e}")
    
    def _cleanup_audiorecorder(self, env):
        """Cleanup Audio Recorder app and related audio recording files (refer to scenario_d)"""
        logging.info("   🎤 cleanup Audio Recorder...")
        
        from scendroid.env import adb_utils, tools, device_constants
        import time
        
        try:
            # 1. Cleanup audio recording files in the Downloads folder
            logging.info("      Cleaning up audio recording files in Downloads...")
            download_path = f"{device_constants.EMULATOR_DATA}/Download"
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.wav',
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.mp3',
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.m4a',
            ], env.controller)
            
            # 2. Cleanup external storage audio recording files for Audio Recorder
            logging.info("      Cleaning up audio recording files in external storage...")
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}/AudioRecorder",
                f"{device_constants.EMULATOR_DATA}/Recordings",
                f"{device_constants.EMULATOR_DATA}/Music",
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', audio_dir
                ], env.controller)
            
            # 3. Use 'pm clear' to completely clear app data
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            
            # 4. grant permissions
            adb_utils.grant_permissions(
                "com.dimowner.audiorecorder",
                "android.permission.RECORD_AUDIO",
                env.controller,
            )
            adb_utils.grant_permissions(
                "com.dimowner.audiorecorder",
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            
            # 5. Launch the app to handle the onboarding interface
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)
            
            # 6. Tap the onboarding button
            try:
                controller = tools.AndroidToolController(env=env.controller)
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done']:
                    try:
                        controller.click_element(btn_text)
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except:
                pass
            
            # close app
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Audio Recorder has been cleaned up and set up")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Audio Recorder cleanup failed: {e}")
    
    def _cleanup_camera_files(self, env):
        """Cleanup Camera and Files related data (refer to scenario_d)"""
        logging.info("   📷 cleanup Camera and Files...")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import time
        
        try:
            # Cleanup DCIM directory (Camera photos)
            file_utils.clear_directory(device_constants.GALLERY_DATA, env.controller)
            logging.info("      ✅ Camera photos have been cleared")
            
            # Cleanup Download directory (receipts, trip images, etc.)
            file_utils.clear_directory(device_constants.DOWNLOAD_DATA, env.controller)
            logging.info("      ✅ Download directory has been cleared")
            
            # Cleanup possible other folders
            folders_to_clean = [
                'Jan_Trip', 'Business_Trip', 'Conference_2026', 'Travel_Docs',
                'Lectures', 'Documents', 'Study', 'Research',
            ]
            for folder in folders_to_clean:
                folder_path = f"{device_constants.EMULATOR_DATA}/{folder}"
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', folder_path
                ], env.controller)
            
            time.sleep(0.5)
            logging.info("      ✅ Files directory has been cleaned up")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Camera/Files cleanup failed: {e}")
    
    def _cleanup_retromusic(self, env):
        """Cleanup Retro Music data and initialize songs (refer to scenario_c)"""
        logging.info("   🎵 Cleaning up and initializing Retro Music...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.task_evals.single import retro_music
        from scendroid.env import adb_utils, device_constants
        from scendroid.utils import file_utils
        import random
        import time
        
        try:
            # 1. Cleanup playlist database
            logging.info("      Step 1: Cleaning up playlist database...")
            retro_music._clear_playlist_dbs(env)
            
            # 2. Cleanup music file storage (using clear_internal_storage)
            logging.info("      Step 2: Cleaning up music storage...")
            user_data_generation.clear_internal_storage(env)
            
            # 3. Prepare song list (refer to subtask_7 in scenario_c)
            available_songs = [
                'My Heart is Yours', 'Endless Summer', 'Whispering Wind', 'Lost in the Echo',
                'Chasing Shadows', 'Night Drive', 'Echoes of Silence', 'Bright Lights',
                'Moments', 'Forever Young', 'Rising Sun', 'Silent Dreams',
                'City of Stars', 'Moonlight Sonata', 'Through the Storm', 'Return to Paradise',
            ]
            noise_songs = [
                'Voices in the Hall', 'Under the Sky', "Dreamer's Awake", 'Serenity Now',
                'Falling Feathers', 'Orbiting Stars', 'Reflections', 'Beyond the Horizon',
            ]
            
            # ⚠️ W7-03 will directly use the actual song names from available_songs; no additional creation is needed
            all_songs = available_songs + noise_songs
            logging.info(f"      Step 3: Creating {len(all_songs)} music files...")
            logging.info(f"         - Group 1 (W2-07 & W7-03): {len(available_songs)} songs")
            logging.info(f"         - Group 2 (Noise): {len(noise_songs)} songs")
            
            # 4. Create an MP3 file for each song (each 2–4 minutes long)
            total_duration_ms = 0
            
            for song_name in all_songs:
                # Construct file path
                file_path = file_utils.convert_to_posix_path(
                    device_constants.MUSIC_DATA, f"{song_name}.mp3"
                )
                
                # Each song is 2–4 minutes long
                duration_ms = random.randint(2 * 60 * 1000, 4 * 60 * 1000)
                total_duration_ms += duration_ms
                
                # create MP3 file
                user_data_generation.write_mp3_file_to_device(
                    file_path,
                    env,
                    title=song_name,
                    artist=random.choice(user_data_generation.COMMON_GIVEN_NAMES),
                    duration_milliseconds=duration_ms,
                )
            
            # 5. Scan the music directory to update the media library
            logging.info("      Step 4: Scanning music directory...")
            retro_music._scan_music_directory(env)
            time.sleep(2.0)
            
            # 6. Launch and close the app to ensure initialization is complete
            logging.info("      Step 5: Launching and closing Retro Music...")
            try:
                adb_utils.launch_app("retro music", env.controller)
                time.sleep(2.0)
                adb_utils.close_app("retro music", env.controller)
                time.sleep(0.5)
            except Exception as e:
                logging.debug(f"      Launch/close app: {e}")
            
            # Calculate total duration
            total_minutes = total_duration_ms / (60 * 1000)
            logging.info(f"   ✅ Retro Music initialized ({len(all_songs)} songs, total {total_minutes:.1f} min)")
            logging.info(f"      📋 Group 1 (W2-07 & W7-03): {len(available_songs)} songs - {available_songs[:3]}...")
            logging.info(f"      📋 Group 2 (Noise): {len(noise_songs)} songs - {noise_songs[:3]}...")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Retro Music setup failed: {e}")
            import traceback
            logging.debug(traceback.format_exc())
    
    def _cleanup_opentracks(self, env):
        """
        Cleanup OpenTracks data and grant permissions (refer to scenario_c)
        
        🔧 Fix: First launch the app to create the database and authorize, then clean up data
        """
        logging.info("   🏃 cleanup OpenTracks...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.env import adb_utils, tools
        import time
        
        try:
            # 1. get package name
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
            # 2. grant permissions
            logging.info("      granting OpenTracks permissions...")
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.ACCESS_COARSE_LOCATION",
                env.controller,
            )
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.ACCESS_FINE_LOCATION",
                env.controller,
            )
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            
            # 3. Launch and close the app (to ensure database creation + initialization dialog handling)
            logging.info("      Launching and closing OpenTracks (database creation + dialog handling)...")
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                # Attempt to handle Bluetooth permission dialog
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ Clicked the Bluetooth 'Allow' button")
                    time.sleep(1.0)
                except:
                    logging.debug("      No Bluetooth popup or click failed")
                
                adb_utils.close_app("activity tracker", env.controller)
                time.sleep(0.5)
            except Exception as e:
                logging.debug(f"      Launch/close app: {e}")
            
            # 4. clean database
            logging.info("      cleanup OpenTracks database...")
            activity_app_utils.clear_db(env)
            logging.info("      ✅ OpenTracks database cleared")
            
            # 5. return to home screen
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ OpenTracks cleaned and initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️ OpenTracks cleanup failed: {e}")
            import traceback
            logging.debug(traceback.format_exc())
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization logic
        
        Execute corresponding initialization before a specific subtask starts
        """
        if subtask_idx >= len(self.seven_day_subtasks):
            return super().initialize_subtask(subtask_idx, env)
        
        subtask = self.seven_day_subtasks[subtask_idx]
        
        # ⚡ Reset mode: Special initialization for SMS/OpenTracks has already been handled in _reset_initialize_subtask
        # Directly call the parent class (seven_day_base will detect reset_mode and delegate to _reset_initialize_subtask)
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        # === Non-reset mode: Execute special pre-initialization for each task ===
        
        # W1-09: SMS Progress Summary - Need to simulate attendees' replies
        if subtask.task_id == "W1-09":
            logging.warning("   💬 W1-09 initialization - Setting up SMS progress replies...")
            self._setup_sms_for_w1_09(env)
        
        # W2-08: SMS Summary to Markor - Need to simulate discussion progress replies and distractors
        if subtask.task_id == "W2-08":
            logging.warning("   💬 W2-08 initialization - Setting up SMS progress replies and distractors...")
            self._setup_sms_for_w2_08(env)
        
        # W3-02: Morning Meeting has already been created during batch initialization; no need to create it here
        # (Retain this comment to prevent confusion)
        
        # W5-03: SMS simulation - Meeting B confirmation reply
        if subtask.task_id == "W5-03":
            logging.warning("   💬 W5-03 initialization - Setting up Meeting B confirmation reply...")
            self._setup_sms_for_w5_03(env)
        
        # W5-07: SMS simulation - Meeting A final status
        if subtask.task_id == "W5-07":
            logging.warning("   💬 W5-07 initialization - Setting up Meeting A final status...")
            self._setup_sms_for_w5_07(env)
        
        # W7-10: SMS simulation - Meeting B final confirmation
        if subtask.task_id == "W7-10":
            logging.warning("   💬 W7-10 initialization - Setting up Meeting B final confirmation...")
            self._setup_sms_for_w7_10(env)
        
        # 🆕 W7-07: OpenTracks re-initialization - Fully reuse E-F7's _initialize_today_track
        if subtask.task_id == "W7-07":
            logging.warning("   🏃 W7-07 initialization - Preparing today's exercise track (reusing E-F7)...")
            self._initialize_today_track_for_w7_07(env)
        
        # Call parent class method (handles time setup, creates evaluator, etc.)
        super().initialize_subtask(subtask_idx, env)
    
    def _setup_sms_for_w1_09(self, env):
        """Initialize SMS replies for W1-09 (simulate attendees' replies to the W1-04 SMS)
        
        ⚠️ Important: Do NOT clear existing SMS!
        - W1-04 user has already sent a meeting reminder SMS to four attendees
        - W1-09 must retain those SMS and add replies from some attendees
        - Add distractors (SMS from non-attendees)
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies for W1-09...")
        logging.warning("=" * 60)
        
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        try:
            # get parameters
            params = self.generated_params
            meeting_a = params['meeting_a']
            attendees_full = meeting_a['attendees_full']  # ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown']
            
            # Create phone number mapping (based on assignments in _setup_contacts)
            name_to_phone = {
                'John Smith': '555-0101',
                'Bob Johnson': '555-0102',
                'Nierson Williams': '555-0103',
                'Hession Brown': '555-0104',
            }
            
            # 1. Prepare progress replies (2–3 people reply)
            progress_replies = [
                {'from': 'John Smith', 'content': "Got it, see you at 9am!"},
                {'from': 'Bob Johnson', 'content': "Thanks for the reminder. I'll be there."},
            ]
            
            # 2. Prepare distractors (2 SMS from non-attendees)
            # ✅ Avoid using names from user_names (David, Sarah, Jessica, Ryan, Alex)
            # ✅ Avoid using names of Meeting A attendees (John, Bob, Nierson, Hession)
            # ✅ Use different phone number prefixes (555-09xx) to avoid conflicts with Meeting A/Seminar/Meeting B
            distractor_messages = [
                {'from': 'Karen Martinez', 'phone': '555-0901', 'content': "Hey, are you free for coffee this afternoon?"},
                {'from': 'Johnathan Taylor', 'phone': '555-0902', 'content': "Did you see the game last night?"},
            ]
            
            logging.warning(f"   Step 1: Adding {len(progress_replies)} progress replies...")
            logging.warning(f"   📋 Progress replies from attendees:")
            for reply in progress_replies:
                logging.warning(f"      - {reply['from']}: \"{reply['content']}\"")
            logging.warning(f"   📋 Distractor messages:")
            for distractor in distractor_messages:
                logging.warning(f"      - {distractor['from']}: \"{distractor['content']}\"")
            
            # 3. Add progress reply SMS
            progress_count = 0
            for reply in progress_replies:
                from_name = reply['from']
                content = reply['content']
                phone = name_to_phone.get(from_name)
                
                if phone:
                    try:
                        # Use text_emulator to simulate receiving SMS
                        adb_utils.text_emulator(
                            env.controller,
                            phone,  # Sender's phone number
                            content,  # SMS content
                        )
                        progress_count += 1
                        logging.warning(f"      ✅ [{progress_count}] SMS from {from_name} ({phone}): \"{content}\"")
                        time.sleep(1.0)
                    except Exception as e:
                        logging.error(f"      ❌ Failed to add SMS from {from_name}: {e}")
                else:
                    logging.error(f"      ❌ No phone found for {from_name}")
            
            time.sleep(0.5)
            logging.warning(f"   ✅ Added {progress_count} progress replies")
            
            # 4. Add distractor SMS
            distractor_count = 0
            for distractor in distractor_messages:
                from_name = distractor['from']
                phone = distractor['phone']
                content = distractor['content']
                
                try:
                    adb_utils.text_emulator(
                        env.controller,
                        phone,
                        content,
                    )
                    distractor_count += 1
                    logging.warning(f"      ✅ [{distractor_count}] Distractor from {from_name} ({phone}): \"{content}\"")
                    time.sleep(1.0)
                except Exception as e:
                    logging.error(f"      ❌ Failed to add distractor from {from_name}: {e}")
            
            time.sleep(1.0)
            logging.warning(f"   ✅ Added {distractor_count} distractor messages")
            
            # 5. etc. Pending SMS database sync
            logging.warning("   ⏳ Waiting for SMS database to sync...")
            time.sleep(3.0)
            
            # 6. Force-refresh SMS app
            logging.warning("   Step 2: Refreshing SMS app...")
            try:
                # Close the SMS app
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(1.0)
                
                # open SMS app
                logging.warning("      📱 opening SMS app...")
                adb_utils.start_activity(
                    "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                    None,
                    env.controller
                )
                time.sleep(2.0)
                
                # Press the BACK key four times to ensure returning to the home screen
                logging.warning("      📱 pressing back to return to home screen...")
                for _ in range(4):
                    adb_utils.issue_generic_request(
                        ["shell", "input", "keyevent", "KEYCODE_BACK"],
                        env.controller
                    )
                    time.sleep(0.3)
                
                # Press the HOME key to exit to the desktop
                logging.warning("      📱 pressing Home to exit to desktop...")
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                
                logging.warning("   ✅ SMS app refreshed")
            except Exception as e:
                logging.warning(f"   ⚠️ Failed to refresh SMS app: {e}")
            
            logging.warning("=" * 60)
            logging.warning(f"✅ W1-09 SMS setup complete!")
            logging.warning(f"   Progress replies: {progress_count}")
            logging.warning(f"   Distractors: {distractor_count}")
            logging.warning("=" * 60)
            
        except Exception as e:
            logging.error(f"❌ Failed to setup SMS for W1-09: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def _setup_sms_for_w2_08(self, env):
        """Initialize SMS replies for W2-08 (simulating seminar discussion progress replies + distractors)
        
        ⚠️ Important: Use the correct seminar participants (Alice, Charlie, Diana, Frank)
        instead of Meeting A participants from Day 1 (John, Bob, Nierson, Hession)
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies for W2-08...")
        logging.warning("=" * 60)
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # Prepare progress reply messages (progress feedback from seminar participants)
            # Use seminar participants: Alice, Charlie, Diana (phone numbers 555-02xx)
            progress_replies = [
                {'from': 'Alice Davis', 'phone': '555-0201', 'content': "Finished the paper abstract section"},
                {'from': 'Charlie Davis', 'phone': '555-0202', 'content': "Completed the review of section 2"},
                {'from': 'Diana Davis', 'phone': '555-0203', 'content': "Implementation code is ready"},
            ]
            
            # Prepare distractor messages (non-seminar SMS messages—using Meeting A participants)
            distractor_messages = [
                {'from': 'John Smith', 'phone': '555-0101', 'content': "Want to grab lunch tomorrow?"},
                {'from': 'Bob Johnson', 'phone': '555-0102', 'content': "Have you read that book I mentioned?"},
            ]
            
            logging.warning(f"   Adding {len(progress_replies)} progress replies + {len(distractor_messages)} distractors...")
            
            # Add progress reply SMS messages
            for reply in progress_replies:
                adb_utils.text_emulator(env.controller, reply['phone'], reply['content'])
                logging.warning(f"      ✅ SMS from {reply['from']}")
                time.sleep(1.0)
            
            # Add distractor SMS messages
            for distractor in distractor_messages:
                adb_utils.text_emulator(env.controller, distractor['phone'], distractor['content'])
                logging.warning(f"      ✅ Distractor from {distractor['from']}")
                time.sleep(1.0)
            
            time.sleep(3.0)
            
            # refresh SMS app
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)
            
            for _ in range(4):
                adb_utils.issue_generic_request(
                    ["shell", "input", "keyevent", "KEYCODE_BACK"],
                    env.controller
                )
                time.sleep(0.3)
            
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
            logging.warning("✅ W2-08 SMS setup complete!")
            
        except Exception as e:
            logging.error(f"❌ Failed to setup SMS for W2-08: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def _setup_preferences(self):
        """Preferences will be set by W1-06 task"""
        logging.info("   🎯 Preferences ready...")
        
        # Note: Preferences will be created by W1-06 (WeekPlan.md)
        # PreferenceStore uses parse_and_store(), not set()
        # The W1-06 task will create:
        # - Diet: light, no fried
        # - Budget: dining ≤ $120, non-essential > $100 ask-first
        # - Exercise: 18:30 for 30min
        
        logging.info("   ✅ Preferences will be created by W1-06")
    
    def _setup_broccoli_recipes(self, env):
        """
        Setup Broccoli recipes (for W6-02)
        
        🔧 Fix: Use the same recipe creation logic as in scenario_b
        Refer to the implementation of scenario_b._setup_broccoli_recipe()
        
        Created recipes:
        1. ✅ Scrambled Eggs with Toast (correct answer: contains eggs + ≤15 minutes)
        2. ❌ Classic Egg Casserole (distractor: contains eggs but >15 minutes)
        3. ❌ Perfect Poached Eggs (distractor: contains eggs but >15 minutes)
        4. ❌ Quick Avocado Toast (distractor: ≤15 minutes but no eggs)
        5. ❌ Banana Smoothie (distractor: ≤15 minutes but no eggs)
        """
        logging.info("   🥦 Setting up Broccoli recipes...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import time
        import subprocess
        
        _DB_PATH = '/data/data/com.flauschcode.broccoli/databases/broccoli'
        _TABLE_NAME = 'recipes'
        _APP_NAME = 'broccoli app'
        
        try:
            # 1. Launch and close the app to ensure database initialization
            logging.info("      📱 Launching Broccoli app to initialize database...")
            try:
                adb_utils.launch_app(_APP_NAME, env.controller)
                time.sleep(2.0)
            except subprocess.TimeoutExpired:
                logging.info("      Broccoli launch timed out (expected behavior)")
                time.sleep(1.0)
            
            adb_utils.close_app(_APP_NAME, env.controller)
            time.sleep(1.0)
            
            # 2. Clear existing recipes
            logging.info("      🗑️  Clearing existing recipes...")
            try:
                sqlite_utils.delete_all_rows_from_table(
                    table_name=_TABLE_NAME,
                    remote_db_file_path=_DB_PATH,
                    env=env,
                    app_name=_APP_NAME
                )
                logging.info("      ✅ Existing recipes cleared")
            except Exception as e:
                logging.warning(f"      ⚠️  Failed to clear existing recipes: {e}")
            
            # 3. createrecipedata
            recipes = []
            
            # ✅ Correct answer: Scrambled Eggs with Toast (eggs + ≤15 minutes)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Scrambled Eggs with Toast',
                description='A easy breakfast with eggs.',
                servings='2',
                preparationTime='10 minutes',
                ingredients='eggs, butter, salt, pepper, bread',
                directions='Beat eggs. Cook in butter. Serve with toast.',
                favorite=0
            ))
            
            # ❌ Distractor 1: Classic Egg Casserole (eggs but 45 minutes > 15 minutes)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Classic Egg Casserole',
                description='A hearty breakfast bake with eggs and cheese.',
                servings='6',
                preparationTime='45 minutes',
                ingredients='eggs, cheese, milk, bread, sausage, onion',
                directions='Layer bread and sausage. Mix eggs with milk. Pour over. Bake for 45 minutes.',
                favorite=0
            ))
            
            # ❌ Distractor 2: Perfect Poached Eggs (eggs but 25 minutes > 15 minutes)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Perfect Poached Eggs',
                description='Restaurant-style poached eggs with runny yolk.',
                servings='2',
                preparationTime='25 minutes',
                ingredients='eggs, vinegar, water, salt, butter, toast',
                directions='Bring water to simmer. Add vinegar. Create vortex. Drop eggs. Cook 3-4 minutes.',
                favorite=0
            ))
            
            # ❌ Distractor 3: Quick Avocado Toast (5 minutes but no eggs)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Quick Avocado Toast',
                description='Healthy and quick breakfast option.',
                servings='1',
                preparationTime='5 minutes',
                ingredients='avocado, bread, lemon, salt, pepper',
                directions='Toast bread. Mash avocado. Spread on toast. Season.',
                favorite=0
            ))
            
            # ❌ Distractor 4: Banana Smoothie (8 minutes but no eggs)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Banana Smoothie',
                description='Quick and healthy morning drink.',
                servings='1',
                preparationTime='8 minutes',
                ingredients='banana, milk, yogurt, honey, ice',
                directions='Blend all ingredients until smooth.',
                favorite=0
            ))
            
            # ============================================================
            # 🆕 Group 2: BBQ recipe required for W7-01
            # ============================================================
            logging.info("      Creating Group 2: BBQ recipes for W7-01...")
            
            # ✅ Correct answer: Picnic BBQ (recipe required for W7-01)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Picnic BBQ',
                description='Perfect for an outdoor picnic! A delicious BBQ experience.',
                servings='4-6',
                preparationTime='45 minutes',
                # ⚠️ Important: Ingredients must include the required_items for W7-01
                ingredients='Beef, Chicken, Tomato, Lettuce, BBQ Sauce, Salt, Pepper',
                directions='1. Prepare all ingredients. 2. Fire up the grill. 3. Cook meat to desired doneness. 4. Serve with vegetables.',
                favorite=0
            ))
            
            # ❌ Distractor 5: Vegetable Soup (not BBQ)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Vegetable Soup',
                description='A healthy homemade soup.',
                servings='4',
                preparationTime='30 minutes',
                ingredients='carrots, celery, onions, broth, potatoes, herbs',
                directions='Chop vegetables. Simmer in broth until tender. Season to taste.',
                favorite=0
            ))
            
            # ❌ Distractor 6: Pasta Salad (salad, not BBQ)
            recipes.append(sqlite_schema_utils.Recipe(
                title='Pasta Salad',
                description='A refreshing cold pasta dish.',
                servings='6',
                preparationTime='20 minutes',
                ingredients='pasta, cherry tomatoes, cucumber, olives, feta cheese, olive oil',
                directions='Cook pasta. Mix with vegetables and dressing. Chill before serving.',
                favorite=0
            ))
            
            # 4. Insert all recipes into the database (batch insertion)
            logging.info(f"      Inserting {len(recipes)} recipes into database...")
            sqlite_utils.insert_rows_to_remote_db(
                rows=recipes,
                exclude_key='recipeId',
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                app_name=_APP_NAME,
                env=env,
            )
            
            for recipe in recipes:
                logging.info(f"      ✅ Added recipe: {recipe.title} ({recipe.preparationTime})")
            
            logging.info("   ✅ Broccoli recipes setup complete (8 recipes: 2 correct + 6 distractors)")
            logging.info("      Group 1 (W6-02): 5 egg recipes (1 correct)")
            logging.info("      Group 2 (W7-01): 3 BBQ recipes (1 correct)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to setup broccoli recipes: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_breakfast_receipt(self, env):
        """Create breakfast receipt image (fully reuse the implementation from scenario_c)"""
        logging.info("   🧾 Creating breakfast receipt image...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        from PIL import Image, ImageDraw, ImageFont
        import os
        import tempfile
        import time
        
        try:
            # Fixed parameters (consistent with W2-03 task)
            amount = 6.80
            name = "Campus Breakfast"
            
            # Construct receipt text
            receipt_text = f"""
═══════════════════════════════════
       CAMPUS CAFETERIA
           RECEIPT
═══════════════════════════════════

Date: January 7, 2026
Time: 09:15 AM

───────────────────────────────────
Item                          Price
───────────────────────────────────

{name}                    ${amount:.2f}

───────────────────────────────────
Subtotal:                  ${amount:.2f}
Tax:                        $0.00
───────────────────────────────────
Total:                     ${amount:.2f}

Payment Method: Cash

═══════════════════════════════════
      Thank you for your visit!
═══════════════════════════════════
"""
            
            # Use _draw_text to generate image (consistent with scenario_c/d)
            image = user_data_generation._draw_text(receipt_text.strip(), font_size=18)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "breakfast_receipt.png")
            image.save(temp_path)
            
            # ⚠️ Critical fix: First delete the old file on the device
            remote_path = f"{device_constants.DOWNLOAD_DATA}/breakfast_receipt.png"
            try:
                adb_utils.issue_generic_request(['shell', 'rm', '-f', remote_path], env.controller)
                logging.info(f"      🗑️  Delete old file: {remote_path}")
                time.sleep(0.3)
            except Exception as e:
                logging.debug(f"      Failed to delete old file (may not exist): {e}")
            
            # Copy to the device's Download directory (do NOT clear the entire directory!)
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            
            # etc. Wait for file transfer to complete
            time.sleep(0.5)
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # scan media library
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Breakfast receipt created: {remote_path}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create breakfast receipt: {e}")
    
    def _create_trip_info_image(self, env):
        """Generate itinerary info PNG image (fully reuse the implementation from scenario_d)"""
        logging.info("   📄 Generating itinerary info image...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        try:
            user_name = self.generated_params['user_name']
            
            info_text = f"""
═══════════════════════════════════
    FLIGHT BOOKING CONFIRMATION
═══════════════════════════════════

Passenger: {user_name} Chen
Flight: UA 456
Date: January 21, 2026

Departure: 09:30
Arrival: 12:30
Destination: San Francisco

───────────────────────────────────
    ACCOMMODATION DETAILS
───────────────────────────────────

Hotel: Marriott Union Square
Address: 480 Sutter Street, San Francisco
Front Desk: 415-555-0199

───────────────────────────────────
    SHIPPING ADDRESS (for orders)
───────────────────────────────────

Office: TechCorp SF Branch
Address: 123 Tech Park Drive, Suite 400, San Francisco

═══════════════════════════════════
"""
            
            # use _draw_text to generate image
            image = user_data_generation._draw_text(info_text.strip(), font_size=18)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "Conference_Trip_Info.png")
            image.save(temp_path)
            
            # ⚠️ Critical fix: First delete the old file on the device
            remote_path = f"{device_constants.DOWNLOAD_DATA}/Conference_Trip_Info.png"
            try:
                adb_utils.issue_generic_request(['shell', 'rm', '-f', remote_path], env.controller)
                logging.info(f"      🗑️  Deleting old file: {remote_path}")
                time.sleep(0.3)
            except Exception as e:
                logging.debug(f"      Failed to delete old file (may not exist): {e}")
            
            # Copy to the device's Downloads directory
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # scan media library
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Itinerary info image created: {remote_path}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create itinerary info image: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_return_flight_image(self, env):
        """Generate return flight info PNG image (for W4-06)"""
        logging.info("   📄 Generating return flight info image...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        try:
            user_name = self.generated_params['user_name']
            
            info_text = f"""
═══════════════════════════════════
    RETURN FLIGHT CONFIRMATION
═══════════════════════════════════

Passenger: {user_name} Chen
Flight: UA 789
Date: January 16, 2026

Departure: 18:30
Arrival: 22:30
Origin: San Francisco
Destination: Home

═══════════════════════════════════
"""
            
            # use _draw_text to generate image
            image = user_data_generation._draw_text(info_text.strip(), font_size=18)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "Return_Flight_Info.png")
            image.save(temp_path)
            
            # ⚠️ Critical fix: First delete the old file on the device
            remote_path = f"{device_constants.DOWNLOAD_DATA}/Return_Flight_Info.png"
            try:
                adb_utils.issue_generic_request(['shell', 'rm', '-f', remote_path], env.controller)
                logging.info(f"      🗑️  Deleting old file: {remote_path}")
                time.sleep(0.3)
            except Exception as e:
                logging.debug(f"      Failed to delete old file (may not exist): {e}")
            
            # Copy to the device's Downloads directory
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # scan media library
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Return flight info image created: {remote_path}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create return flight info image: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_conflicting_meeting_for_w3_02(self, env):
        """Create a conflicting Morning Meeting for W3-02 (10:00–11:00, conflicting with Flight 9:30–12:30)"""
        logging.info("   🚨 Creating conflicting Morning Meeting for W3-02...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import calendar as cal_module
        import time
        
        try:
            # Get the date for Day 3
            day3_config = self.days.get(2)  # Day 3 (index2)
            if not day3_config:
                logging.warning("   ⚠️ Day 3 config not found")
                return
            
            base_date = day3_config.date
            
            # Create Morning Meeting: 10:00–11:00 (conflicting with Flight 9:30–12:30)
            meeting_start = base_date.replace(hour=10, minute=0, second=0, microsecond=0)
            meeting_start_ts = cal_module.timegm(meeting_start.timetuple())
            meeting_end_ts = meeting_start_ts + (60 * 60)  # 1hours
            
            conflict_event = sqlite_schema_utils.CalendarEvent(
                start_ts=meeting_start_ts,
                end_ts=meeting_end_ts,
                title="Morning Meeting",
                location="Office",
                description="Regular team sync",
            )
            
            # insert into database
            _DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
            _TABLE = "events"
            
            sqlite_utils.insert_row(_TABLE, _DB_PATH, conflict_event, env.controller)
            
            # refreshCalendar app
            adb_utils.close_app("simple calendar pro", env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Conflicting Morning Meeting created (10:00-11:00, conflicts with Flight 9:30-12:30)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create conflicting meeting: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_conflicting_meeting_for_w4_04(self, env):
        """Create a conflicting meeting for W4-04 (18:00–19:00, conflicting with daily exercise 18:00–18:30)"""
        logging.info("   🚨 Creating conflicting Team Discussion for W4-04...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import calendar as cal_module
        import time
        
        try:
            # Get the date for Day 4
            day4_config = self.days.get(3)  # Day 4 (index3)
            if not day4_config:
                logging.warning("   ⚠️ Day 4 config not found")
                return
            
            base_date = day4_config.date
            
            # Create Team Discussion: 18:00–19:00 (conflicting with daily exercise 18:00–18:30)
            meeting_start = base_date.replace(hour=18, minute=0, second=0, microsecond=0)
            meeting_start_ts = cal_module.timegm(meeting_start.timetuple())
            meeting_end_ts = meeting_start_ts + (60 * 60)  # 1hours
            
            conflict_event = sqlite_schema_utils.CalendarEvent(
                start_ts=meeting_start_ts,
                end_ts=meeting_end_ts,
                title="Team Discussion",
                location="Conference Room",
                description="Project review meeting",
            )
            
            # insert into database
            _DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
            _TABLE = "events"
            
            sqlite_utils.insert_row(_TABLE, _DB_PATH, conflict_event, env.controller)
            
            # refreshCalendar app
            adb_utils.close_app("simple calendar pro", env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Conflicting Team Discussion created (18:00-19:00, conflicts with exercise 18:00-18:30)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create conflicting meeting: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_keynote_meeting_for_day4(self, env):
        """Create a Keynote meeting for Day 4 (14:00–15:00, for use by W4-03 and W4-05)"""
        logging.info("   📅 Creating Keynote meeting for Day 4...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import calendar as cal_module
        import time
        
        try:
            # Get the date for Day 4
            day4_config = self.days.get(3)  # Day 4 (index3)
            if not day4_config:
                logging.warning("   ⚠️ Day 4 config not found")
                return
            
            base_date = day4_config.date
            
            # createKeynote: 14:00-15:00
            meeting_start = base_date.replace(hour=14, minute=0, second=0, microsecond=0)
            meeting_start_ts = cal_module.timegm(meeting_start.timetuple())
            meeting_end_ts = meeting_start_ts + (60 * 60)  # 1hours
            
            keynote_event = sqlite_schema_utils.CalendarEvent(
                start_ts=meeting_start_ts,
                end_ts=meeting_end_ts,
                title="Keynote Speech",
                location="Main Hall",
                description="Conference keynote presentation",
            )
            
            # insert into database
            _DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
            _TABLE = "events"
            
            sqlite_utils.insert_row(_TABLE, _DB_PATH, keynote_event, env.controller)
            
            # refreshCalendar app
            adb_utils.close_app("simple calendar pro", env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Keynote meeting created (14:00-15:00, for W4-03 and W4-05)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create keynote meeting: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_breakfast_photo(self, env):
        """
        🆕 Create breakfast photo (for W6-05)
        
        Place it in the DCIM/Camera directory to simulate a newly taken photo
        Avoid instability from on-site photography
        """
        logging.info("   📷 Creating breakfast photo...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        try:
            photo_text = """
═══════════════════════════════════
      🍳  MY BREAKFAST  🍳
═══════════════════════════════════

A delicious plate of scrambled eggs
with fresh herbs and vegetables

Perfect Saturday morning meal!

═══════════════════════════════════
"""
            
            # use _draw_text to generate image
            image = user_data_generation._draw_text(photo_text.strip(), font_size=20)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "breakfast.png")
            image.save(temp_path)
            
            # Target path: DCIM/Camera (simulating camera capture)
            # device_constants does not define DCIM_DATA; directly use hardcoded path (refer to scenario_e)
            camera_dir = "/sdcard/DCIM/Camera"
            adb_utils.issue_generic_request(['shell', 'mkdir', '-p', camera_dir], env.controller)
            time.sleep(0.3)
            
            remote_path = f"{camera_dir}/breakfast.png"
            
            # Delete old file (if exists)
            try:
                adb_utils.issue_generic_request(['shell', 'rm', '-f', remote_path], env.controller)
                time.sleep(0.3)
            except:
                pass
            
            # Copy to device
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # scan media library
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Breakfast photo created: {remote_path}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create breakfast photo: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_opentracks_saturday(self, env):
        """
        🆕 Initialize OpenTracks Saturday walking data (for W6-09)
        
        Refer to the implementation in scenario_b._setup_opentracks_activities()
        Create Saturday walking track: Central Park, 2.5 km, 35 minutes
        """
        logging.info("   🏃 Initializing OpenTracks Saturday walk...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime
        import calendar
        
        try:
            # Get the date for Day 6 (Saturday)
            day6_config = self.days.get(5)  # Day 6 (index5)
            if not day6_config:
                logging.warning("   ⚠️ Day 6 config not found")
                return
            
            # base_date may be a string or datetime; needs conversion
            base_date = day6_config.date
            if isinstance(base_date, str):
                base_date = datetime.strptime(base_date, '%Y-%m-%d')
            
            # Create walking track: starts at 15:00, duration 35 minutes, distance 2.5 km
            walk_start_dt = base_date.replace(hour=15, minute=0, second=0, microsecond=0)
            walk_start_ts = int(calendar.timegm(walk_start_dt.timetuple()) * 1000)  # milliseconds
            walk_duration_ms = int(35 * 60 * 1000)  # 35minutes
            walk_stop_ts = walk_start_ts + walk_duration_ms
            walk_distance_m = int(2.5 * 1000)  # 2.5km
            
            activity = sqlite_schema_utils.SportsActivity(
                name="Central Park Walk",
                description="Central Park",  # Location as description
                category='walking',
                activity_type='walking',
                starttime=walk_start_ts,
                stoptime=walk_stop_ts,
                numpoints=int(35 * 2),  # Approximately one point every 30 seconds
                totaldistance=walk_distance_m,
                totaltime=walk_duration_ms,
                movingtime=int(walk_duration_ms * 0.9),  # 90% move time
                avgspeed=walk_distance_m / (walk_duration_ms / 1000.0),  # m/s
                avgmovingspeed=(walk_distance_m / (walk_duration_ms / 1000.0)) / 0.9,
                elevationgain=15.0,
                elevationloss=15.0,
            )
            
            # Add to database (using the _add_activities method, passing a list)
            activity_app_utils._add_activities([activity], env)
            
            logging.info(f"   ✅ Saturday walk created: {walk_start_dt.strftime('%Y-%m-%d %H:%M')}, "
                        f"2.5km, 35min, Central Park")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to setup OpenTracks Saturday data: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_opentracks_weekly(self, env):
        """
        🆕 Initialize OpenTracks weekly history data (for W7-07)
        
        Refer to the implementation of scenario_e._setup_opentracks_history()
        Create multiple Hiking records for this week, for weekly statistics
        """
        logging.info("   🏃 Initializing OpenTracks weekly history...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime, timedelta
        import calendar
        import random
        
        try:
            # Get the date of Day 1 (Monday) as the base date
            day1_config = self.days.get(0)  # Day 1 (index0)
            if not day1_config:
                logging.warning("   ⚠️ Day 1 config not found")
                return
            
            # base_date may be a string or datetime; conversion is required
            base_date = day1_config.date
            if isinstance(base_date, str):
                base_date = datetime.strptime(base_date, '%Y-%m-%d')
            
            activities = []
            
            # Create Hiking records for this week (Monday–Saturday, total of 6 days)
            # 📊 Total: approximately 15 km, 5 hours
            for day_offset in range(6):
                date = base_date + timedelta(days=day_offset)
                start_hour = random.choice([8, 9, 10, 17, 18])
                start_dt = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                
                # Distance: 2–3 km
                distance_km = random.uniform(2.0, 3.5)
                distance_m = int(distance_km * 1000)
                
                # duration: 40-60minutes
                duration_min = random.randint(40, 60)
                duration_ms = duration_min * 60 * 1000
                
                start_ts = int(calendar.timegm(start_dt.timetuple()) * 1000)
                stop_ts = start_ts + duration_ms
                
                activity = sqlite_schema_utils.SportsActivity(
                    name=f"Hiking - Day {day_offset+1}",
                    description=f"Hiking - Week {day_offset+1}",
                    category='hiking',
                    activity_type='hiking',
                    starttime=start_ts,
                    stoptime=stop_ts,
                    numpoints=int(duration_min * 2),  # Approximately one point every 30 seconds
                    totaldistance=distance_m,
                    totaltime=duration_ms,
                    movingtime=int(duration_ms * 0.85),  # 85% move time
                    avgspeed=distance_m / (duration_ms / 1000.0),  # m/s
                    avgmovingspeed=(distance_m / (duration_ms / 1000.0)) / 0.85,
                    elevationgain=random.randint(30, 80),
                    elevationloss=random.randint(30, 80),
                )
                
                activities.append(activity)
                logging.info(f"      📌 Day {day_offset+1}: {distance_km:.1f}km, {duration_min}min")
            
            # Add all activities to the database (using the _add_activities method, adding all at once)
            activity_app_utils._add_activities(activities, env)
            
            logging.info(f"   ✅ Weekly Hiking data created ({len(activities)} activities)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to setup OpenTracks weekly data: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_tasks_picnic(self, env):
        """
        🆕 Initialize Tasks app picnic checklist data (for W7-01)
        
        Fully refer to the implementation of scenario_e._setup_tasks()
        Create a "Tomato" task (existing supplies) + distractor tasks
        
        ⚠️ Critical fix: Use "pm clear" to completely erase all data (including the lists table)
        """
        logging.info("   📝 Initializing Tasks picnic checklist...")
        
        from scendroid.task_evals.information_retrieval import task_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime
        import random
        import uuid
        import time
        
        try:
            # 1. Use "pm clear" to completely erase Tasks app data (including all tables: tasks, lists, etc.)
            logging.info("      🔧 Completely clearing Tasks app data (pm clear)...")
            adb_utils.issue_generic_request([
                'shell', 'pm', 'clear', 'org.tasks'
            ], env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Tasks app data has been completely cleared")
            
            # 2. Launch and close the Tasks app (create database + skip initialization configuration screen)
            logging.info("      🔧 Launching Tasks app (create database + skip initialization configuration)...")
            try:
                adb_utils.launch_app("tasks", env.controller)
                time.sleep(2.0)
                adb_utils.close_app("tasks", env.controller)
                time.sleep(0.5)
            except Exception as e:
                logging.debug(f"      Launch/close app: {e}")
            
            # 3. get base_date (Day 7 - Sunday)
            day7_config = self.days.get(6)  # Day 7 (index6)
            if not day7_config:
                logging.warning("      ⚠️ Day 7 config not found")
                return
            
            base_date = day7_config.date
            if isinstance(base_date, str):
                base_date = datetime.strptime(base_date, '%Y-%m-%d')
            
            # 4. 🚨 Important logic: Only create tasks for "already_have" items (with incomplete status)
            # The user must manually add required_items to Tasks (this is part of the task)
            # Then check off the "already_have" tasks
            # 🔧 Fix: Change to "BBQ Sauce and Salt" to avoid conflict with the recipe ingredient "Tomato"
            already_have = ["BBQ Sauce", "Salt"]
            
            # 5. Create an "existing supplies" task (incomplete status; user must check it off)
            have_tasks = []
            for i, item in enumerate(already_have):
                due_ts = int(base_date.replace(hour=8).timestamp()) * 1000
                created_ts = due_ts - 7 * 24 * 3600 * 1000  # Created 7 days ago
                
                task = sqlite_schema_utils.Task(
                    title=item,
                    importance=1,  # Medium priority
                    dueDate=due_ts,
                    hideUntil=0,
                    created=created_ts,
                    modified=created_ts,
                    completed=0,  # Not completed; user must check it off
                    deleted=0,
                    notes='Picnic supply item',
                    remoteId=str(uuid.uuid4().int),
                )
                have_tasks.append(task)
            
            # 6. Add distractor tasks (unrelated to the picnic)
            distractor_tasks = []
            distractor_titles = [
                'Buy groceries', 'Reply to emails', 'Schedule dentist',
                'Call mom', 'Pay bills', 'Clean room',
            ]
            
            for i, title in enumerate(distractor_titles):
                due_ts = int(base_date.replace(hour=random.randint(8, 20)).timestamp()) * 1000
                created_ts = due_ts - 7 * 24 * 3600 * 1000
                
                task = sqlite_schema_utils.Task(
                    title=title,
                    importance=random.randint(0, 1),  # Low/medium priority
                    dueDate=due_ts,
                    hideUntil=0,
                    created=created_ts,
                    modified=created_ts,
                    completed=0,
                    deleted=0,
                    notes=None,
                    remoteId=str(uuid.uuid4().int),
                )
                distractor_tasks.append(task)
            
            # 7. Add all tasks
            all_tasks = have_tasks + distractor_tasks
            task_app_utils.add_tasks(all_tasks, env)
            
            logging.info(f"      ✅ Added {len(have_tasks)} existing supplies tasks")
            logging.info(f"      ✅ Added {len(distractor_tasks)} distractor tasks")
            logging.info(f"      📋 existing supplies: {already_have}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to setup Tasks picnic data: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_mountain_picnic_meeting(self, env):
        """
        🆕 Create Mountain Picnic meeting (for W7-02)
        
        Day 7 (Sunday), 10:00–12:00, Location: East Valley Trail
        The user needs to modify the location to West Peak Lookout and notify attendees
        """
        logging.info("   🏔️ Creating Mountain Picnic meeting...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import calendar as cal_module
        import time
        
        try:
            # Get the date of Day 7 (Sunday)
            day7_config = self.days.get(6)  # Day 7 (index6)
            if not day7_config:
                logging.warning("   ⚠️ Day 7 config not found")
                return
            
            base_date = day7_config.date
            
            # create Mountain Picnic: 10:00-12:00
            meeting_start = base_date.replace(hour=10, minute=0, second=0, microsecond=0)
            meeting_start_ts = cal_module.timegm(meeting_start.timetuple())
            meeting_end_ts = meeting_start_ts + (2 * 60 * 60)  # 2hours
            
            # Attendees: Use seminar attendees (Alice, Charlie, Diana, Frank)
            seminar = self.generated_params.get('seminar', {})
            attendees = seminar.get('attendees_full', ['Alice Davis', 'Charlie Davis'])
            user_name = self.generated_params.get('user_name', 'David')
            
            attendees_str = f"Attendees: {user_name}, " + ", ".join(attendees)
            
            picnic_event = sqlite_schema_utils.CalendarEvent(
                start_ts=meeting_start_ts,
                end_ts=meeting_end_ts,
                title="Mountain Picnic",
                location="East Valley Trail",  # Original location, to be modified to West Peak Lookout
                description=attendees_str,
            )
            
            # insert into database
            _DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
            _TABLE = "events"
            
            sqlite_utils.insert_row(_TABLE, _DB_PATH, picnic_event, env.controller)
            
            # refresh Calendar app
            adb_utils.close_app("simple calendar pro", env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Mountain Picnic meeting created (10:00-12:00, East Valley Trail)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create Mountain Picnic meeting: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _create_dinner_receipt_photo(self, env):
        """Create a fake dinner receipt photo (refer to the _create_breakfast_photo method in scenario_b)
        
        Place it in the Download directory, allowing the user to move it to Jan_Trip/Receipts
        Because the simulator's camera capture does not display actual content, it would mislead the agent
        """
        logging.info("   📷 Creating dinner receipt photo...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        try:
            # Download folder path
            download_path = device_constants.DOWNLOAD_DATA
            
            # Ensure the Download directory exists
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', download_path], env.controller
            )
            time.sleep(0.3)
            
            # Construct receipt photo content
            photo_text = """
═══════════════════════════════════
      🍽️  DINNER RECEIPT  🍽️
═══════════════════════════════════

    Restaurant: The Grill House
    Date: January 21, 2026
    Time: 18:00
    
    ─────────────────────────────────
    ITEMS:
    ─────────────────────────────────
    Grilled Salmon............ $28.50
    Caesar Salad.............. $12.00
    Sparkling Water........... $ 4.50
    ─────────────────────────────────
    Subtotal.................. $45.00
    Tax (8%).................. $ 3.60
    ─────────────────────────────────
    TOTAL..................... $48.60
    ─────────────────────────────────
    
    Payment: Cash
    
    Thank you for dining with us!
    
═══════════════════════════════════
"""
            
            # use _draw_text to generate image
            image = user_data_generation._draw_text(photo_text.strip(), font_size=18)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "dinner_receipt.png")
            image.save(temp_path)
            
            # ⚠️ Critical fix: First delete the old file on the device
            remote_path = f"{download_path}/dinner_receipt.png"
            try:
                adb_utils.issue_generic_request(['shell', 'rm', '-f', remote_path], env.controller)
                logging.info(f"      🗑️  Deleting old file: {remote_path}")
                time.sleep(0.3)
            except Exception as e:
                logging.debug(f"      Failed to delete old file (may not exist): {e}")
            
            # Copy to the Download directory
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            logging.info(f"      ✅ Receipt photo created: {remote_path}")
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Scan the media library to ensure the file is recognized
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Dinner receipt photo created in the Download directory")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create receipt photo: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_sms_for_w5_03(self, env):
        """Initialize SMS replies for W5-03 (simulate confirmation replies from Meeting B attendees)
        Fully refer to the _setup_sms_for_task8 implementation in scenario_c
        
        ⚠️ Important: Do not clear existing SMS! Retain the notification SMS sent by W5-02
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies for W5-03 (Meeting B confirmations)...")
        logging.warning("=" * 60)
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Do not clear existing SMS! Retain the notification SMS sent by the W5-02 user
            logging.warning("   Step 1: Preserving existing SMS from W5-02...")
            
            # Get Meeting B attendees
            meeting_b = self.generated_params.get('meeting_b', {})
            attendees = meeting_b.get('attendees_full', [])  # List of names
            
            logging.warning(f"   Step 2: Adding {len(attendees)} confirmation replies from Meeting B attendees...")
            
            # Simulate confirmations from 2–3 people (assign phone numbers according to _setup_contacts)
            confirmation_replies = []
            for i in range(min(3, len(attendees))):
                confirmation_replies.append({
                    "from_name": attendees[i],
                    "from_phone": f"555-03{i+1:02d}",  # Meeting B uses 555-03xx
                    "content": ["Got it! I'll be there at 10:00.", 
                               "Confirmed. See you Monday morning.",
                               "Thanks for the reminder! I'll be there."][i]
                })
            
            # Add confirmation replies (use text_emulator to simulate receipt)
            for reply in confirmation_replies:
                try:
                    logging.warning(f"      → {reply['from_name']}: \"{reply['content']}\"")
                    adb_utils.text_emulator(
                        env.controller,
                        reply['from_phone'],
                        reply['content']
                    )
                    time.sleep(1.5)
                except Exception as e:
                    logging.warning(f"      ⚠️ Failed to add reply from {reply['from_name']}: {e}")
            
            # Refresh the SMS application
            logging.warning("   Step 3: Refreshing SMS app...")
            try:
                adb_utils.close_app(env.controller, "Simple SMS Messenger")
                time.sleep(1.0)
                adb_utils.start_app(env.controller, "Simple SMS Messenger")
                time.sleep(2.0)
                adb_utils.press_back_button(env.controller)
                time.sleep(0.5)
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                logging.warning("   ✅ SMS app refreshed")
            except Exception as e:
                logging.warning(f"   ⚠️ SMS refresh failed: {e}")
            
            logging.warning("=" * 60)
            logging.warning(f"✅ W5-03 SMS setup complete: {len(confirmation_replies)} confirmations added")
            logging.warning("=" * 60)
            
        except Exception as e:
            logging.warning(f"   ❌ W5-03 SMS setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_sms_for_w5_07(self, env):
        """Initialize SMS replies for W5-07 (simulate final status replies from Meeting A attendees)
        Fully refer to the _setup_sms_for_task8 implementation in scenario_c
        
        ⚠️ Important: Do not clear existing SMS! Retain the progress replies from W1-09
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies for W5-07 (Meeting A final status)...")
        logging.warning("=" * 60)
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Do not clear existing SMS! Retain all previous SMS
            logging.warning("   Step 1: Preserving all existing SMS...")
            
            # Get Meeting A attendees
            meeting_a = self.generated_params.get('meeting_a', {})
            attendees = meeting_a.get('attendees_full', [])  # List of names
            
            logging.warning(f"   Step 2: Adding {len(attendees)} final status updates from Meeting A attendees...")
            
            # Simulate final status replies (some confirm, some do not reply)
            # Assign phone numbers according to _setup_contacts (Meeting A uses 555-01xx)
            final_replies = []
            for i in range(min(2, len(attendees))):  # Add replies only for the first two attendees
                final_replies.append({
                    "from_name": attendees[i],
                    "from_phone": f"555-01{i+1:02d}",  # Meeting A uses 555-01xx
                    "content": ["All set for Monday! Prepared the slides.",
                               "Ready. Will bring the Q3 report."][i]
                })
            
            # The third and fourth attendees do not reply, indicating non-confirmation
            
            # Add replies
            for reply in final_replies:
                try:
                    logging.warning(f"      → {reply['from_name']}: \"{reply['content']}\"")
                    adb_utils.text_emulator(
                        env.controller,
                        reply['from_phone'],
                        reply['content']
                    )
                    time.sleep(1.5)
                except Exception as e:
                    logging.warning(f"      ⚠️ Failed to add reply from {reply['from_name']}: {e}")
            
            # Refresh the SMS application
            logging.warning("   Step 3: Refreshing SMS app...")
            try:
                adb_utils.close_app(env.controller, "Simple SMS Messenger")
                time.sleep(1.0)
                adb_utils.start_app(env.controller, "Simple SMS Messenger")
                time.sleep(2.0)
                adb_utils.press_back_button(env.controller)
                time.sleep(0.5)
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                logging.warning("   ✅ SMS app refreshed")
            except Exception as e:
                logging.warning(f"   ⚠️ SMS refresh failed: {e}")
            
            logging.warning("=" * 60)
            logging.warning(f"✅ W5-07 SMS setup complete: {len(final_replies)} final updates added")
            logging.warning("=" * 60)
            
        except Exception as e:
            logging.warning(f"   ❌ W5-07 SMS setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    

    def _setup_sms_for_w7_10(self, env):
        """Initialize SMS replies for W7-10 (simulate final confirmation replies from Meeting B attendees)
        Fully refer to the _setup_sms_for_task8 implementation in scenario_c
        
        ⚠️ Important: Do NOT clear existing SMS! Retain the confirm reply for W5-03.
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies for W7-10 (Meeting B final confirmations)...")
        logging.warning("=" * 60)
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Do NOT clear existing SMS! Retain all previous SMS.
            logging.warning("   Step 1: Preserving all existing SMS...")
            
            # Get attendees for Meeting B
            meeting_b = self.generated_params.get('meeting_b', {})
            attendees = meeting_b.get('attendees_full', [])  # List of names
            
            logging.warning(f"   Step 2: Adding {len(attendees)} final confirmations from Meeting B attendees...")
            
            # Simulate the final confirm reply (partial confirm)
            # Assign phone numbers according to _setup_contacts (Meeting B uses 555-03xx)
            final_replies = []
            for i in range(min(2, len(attendees))):
                final_replies.append({
                    "from_name": attendees[i],
                    "from_phone": f"555-03{i+1:02d}",  # Meeting B uses 555-03xx
                    "content": ["All set! See you Monday at 10.",
                               "Confirmed. I'll bring the slides."][i]
                })
            
            # Add reply
            for reply in final_replies:
                try:
                    logging.warning(f"      → {reply['from_name']}: \"{reply['content']}\"")
                    adb_utils.text_emulator(
                        env.controller,
                        reply['from_phone'],
                        reply['content']
                    )
                    time.sleep(1.5)
                except Exception as e:
                    logging.warning(f"      ⚠️ Failed to add reply from {reply['from_name']}: {e}")
            
            # Refresh the SMS app
            logging.warning("   Step 3: Refreshing SMS app...")
            try:
                adb_utils.close_app(env.controller, "Simple SMS Messenger")
                time.sleep(1.0)
                adb_utils.start_app(env.controller, "Simple SMS Messenger")
                time.sleep(2.0)
                adb_utils.press_back_button(env.controller)
                time.sleep(0.5)
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                logging.warning("   ✅ SMS app refreshed")
            except Exception as e:
                logging.warning(f"   ⚠️ SMS refresh failed: {e}")
            
            logging.warning("=" * 60)
            logging.warning(f"✅ W7-10 SMS setup complete: {len(final_replies)} final confirmations added")
            logging.warning("=" * 60)
            
        except Exception as e:
            logging.warning(f"   ❌ W7-10 SMS setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    

    # ==================== Day-by-day Subtask Definition ====================
    
    def _add_all_subtasks(self, params: dict):
        """Add all 71 subtasks across 7 days"""
        self._add_day1_subtasks(params)   # 10 tasks
        self._add_day2_subtasks(params)   # 11 tasks
        self._add_day3_subtasks(params)   # 11 tasks
        self._add_day4_subtasks(params)   # 8 tasks
        self._add_day5_subtasks(params)   # 8 tasks
        self._add_day6_subtasks(params)   # 11 tasks
        self._add_day7_subtasks(params)   # 13 tasks
    
    # ==================== Day 1: Monday - Baseline + Preferences ====================
    
    def _add_day1_subtasks(self, params: dict):
        """Day 1 (Monday): 10 tasks - Establish preferences and Meeting A baseline"""
        user_name = params['user_name']
        meeting_a = params['meeting_a']
        alarm = params['alarm']
        product_table = params['products']['table']
        
        # W1-01: Adjust weekday alarm (reuse A1)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=1, task_id="W1-01",
            evaluator_name="LayeredClockSetAlarm",
            params={
                "alarm_time_hour": alarm['new_hour'],
                "alarm_time_minute": alarm['new_minute'],
                "alarm_enabled": True,
                "check_original_removed": True,
                "original_hour": alarm['original_hour'],
                "original_minute": alarm['original_minute'],
            },
            time="06:55",  # ✅ FIXED: Morning, after the alarm time
            narration=f"{user_name} almost overslept this morning, decides to wake up earlier this week",
            user_instruction=f"Good morning! I want to wake up {alarm['shift_minutes']} minutes earlier every weekday this week. Change my weekday alarm. Don't touch the weekend alarm.",
            reset_user_instruction=(
                f"Open the Clock app. Find the weekday alarm at "
                f"{alarm['original_hour']}:{alarm['original_minute']:02d} AM and change it to "
                f"{alarm['new_hour']}:{alarm['new_minute']:02d} AM. "
                f"Do not touch the weekend alarm at 9:30 AM."
            ),
            max_steps=20,
            context_updates={'weekday_alarm_time': f"{alarm['new_hour']}:{alarm['new_minute']:02d}", 'alarm_shift_minutes': alarm['shift_minutes']},
        )
        
        # W1-02: Check morning schedule (reuse A2, QA)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=2, task_id="W1-02",
            evaluator_name="LayeredCalendarCheckMeetingAnswer",
            params={"must_contain_keywords": ["meeting", meeting_a['title'].split()[0].lower()], "min_keywords_found": 1},
            time="08:10",  # ✅ FIXED: Before the 09:00 meeting
            narration=f"{user_name} wants to check the morning schedule before heading out",
            user_instruction="Check Simple Calendar Pro and tell me what meetings I have (include time) this morning before 12 PM.",
            reset_user_instruction=(
                f"Open Simple Calendar Pro and check today's schedule. "
                f"Tell me all meetings before 12 PM today (include exact time for each)."
            ),
            max_steps=20,
            requires_answer=True,
            context_updates={'morning_items_checked': True},
        )
        
        # W1-03: Extract meeting attendees (reuse A4, QA)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=3, task_id="W1-03",
            evaluator_name="LayeredCalendarExtractAttendees",
            params={
                "event_title": meeting_a['title'],
                "required_attendees": meeting_a['attendees'],
                "min_attendees_found": 4,
            },
            time="08:25",  # ✅ FIXED: Before the 09:00 meeting
            narration=f"{user_name} is about to join the meeting and needs the details",
            user_instruction=f"Tell me the location and all the attendees of this meeting.",
            reset_user_instruction=(
                f"Open Simple Calendar Pro, find the '{meeting_a['title']}' event. "
                f"Tell me the location and all attendees of this meeting."
            ),
            max_steps=20,
            requires_answer=True,
            context_updates={'meetingA_title': meeting_a['title'], 'meetingA_attendees': meeting_a['attendees']},
            tags=["REF"],
        )
        
        # W1-04: Send group meeting reminder (reuse A5)
        # Build contact mapping (name → phone number), consistent with the assignment in _setup_contacts
        contacts_map = {}
        for i, name in enumerate(meeting_a['attendees_full']):
            contacts_map[name] = f"555-01{i+1:02d}"  # Meeting A uses 555-01xx
        
        self.add_subtask_to_day(
            day_idx=0, subtask_id=4, task_id="W1-04",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": meeting_a['attendees_full'],
                "message_must_contain_time": "9:00",  # ✅ FIXED: Meeting time is 09:00–10:00
                "message_must_contain_location": [meeting_a['location']],
                "forbidden_recipients": ["Johnathan Taylor", "Karen Martinez"],  # ✅ Distractor contacts, should not receive the notification
                "min_messages_sent": 4,
                "contacts_map": contacts_map,  # ✅ Add contact mapping
            },
            time="08:40",  # ✅ FIXED: Before the 09:00 meeting
            narration=f"Send meeting reminders to all attendees",
            user_instruction="Send SMS to all attendees to remind them about today's meeting (include time and location).",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Send a message to each of these 4 people: "
                f"{', '.join(meeting_a['attendees_full'])}. "
                f"The message should mention the '{meeting_a['title']}' at 9:00 AM in {meeting_a['location']}."
            ),
            max_steps=30,
            context_updates={'meetingA_notified_count': 4},
        )
        
        # W1-05: Create meeting minutes template in Markor (reuse A6)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=5, task_id="W1-05",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WorkLog.md",
                "required_sections": ["Title", "Time", "Location", "Attendees", "Discussion"],
                "sections_with_content": ["Title", "Time", "Location", "Attendees"],
            },
            time="10:20",  # ✅ FIXED: After the 09:00–10:00 meeting ends
            narration="Prepare meeting notes template in WorkLog.md",
            user_instruction=f"Open Markor and create a meeting notes file called WorkLog.md. Include sections for: Title, Time, Location, Attendees, and Discussion. Fill in the {meeting_a['title']} details.",
            reset_user_instruction=(
                f"Open Markor and create a new file called 'WorkLog.md'. "
                f"Include these sections: Title, Time, Location, Attendees, and Discussion. "
                f"Fill in the meeting details: Title='{meeting_a['title']}', "
                f"Time='9:00 AM', Location='{meeting_a['location']}', "
                f"Attendees={', '.join(meeting_a['attendees_full'])}."
            ),
            max_steps=25,
            context_updates={'artifact_worklog_created': True},
        )
        
        # W1-06: ✅ Newly added: Create WeekPlan.md (preference anchor)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=6, task_id="W1-06",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WeekPlan.md",
                "required_sections": ["Diet", "Budget", "Exercise"],
                "sections_with_content": ["Diet", "Budget", "Exercise"],
            },
            time="10:30",  # ✅ FIXED
            narration="Establish weekly preferences: diet (light/no fried), budget (dining ≤$120, >$100 ask), exercise (18:30, 30min)",
            user_instruction="Create another new file called WeekPlan.md. Record my weekly goals: (1) Diet - I'm on a weight loss plan, only light food, no fried stuff; (2) Budget - dining expenses should stay within $120, if I want to buy something that exceeds this, ask me first; (3) Exercise - I want to exercise at 18:30 daily for 30 minutes, if I try to schedule something at that time, remind me about this.",
            reset_user_instruction=(
                "Open Markor and create a new file called 'WeekPlan.md'. "
                "Record my weekly goals with the following sections and content: "
                "(1) Diet: I'm on a weight loss plan, only light food, no fried food; "
                "(2) Budget: dining expenses within $120/week, ask me before buying anything over $100; "
                "(3) Exercise: daily exercise at 18:30 for 30 minutes, remind me if something conflicts."
            ),
            max_steps=25,
            context_updates={
                'preferences.diet': 'light/no fried',
                'preferences.budget': 120.0,
                'preferences.exercise': '18:30/30min',
                'artifact_weekplan_created': True,
            },
            tags=["PRE"],
        )
        
        # W1-07: Place shopping order (reuse A8)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=7, task_id="W1-07",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_table['sku'],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [product_table['sku']]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="11:00",  # ✅ FIXED
            narration="Order outdoor table for patio",
            user_instruction=f"On the current shopping website (ignore the internet access), search for '{product_table['name']}', add it to your cart, and complete the purchase by placing an order.",
            reset_user_instruction=(
                f"On the current shopping website (ignore the internet access), "
                f"search for '{product_table['name']}' (SKU: {product_table['sku']}), "
                f"add it to your cart, and complete the purchase."
            ),
            max_steps=40,
            context_updates={'orderA_sku': product_table['sku'], 'orderA_amount': product_table['price']},
        )
        
        # W1-08: Record expense (reuse A9)
        # ✅ Check only the amount; do NOT check the name (the name could be "table", "shopping", "patio", etc.)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=8, task_id="W1-08",
            evaluator_name="LayeredExpenseAddSingle",
            params={
                # "name": "",  # ✅ Do NOT pass the name parameter; the evaluator will skip the name check
                "amount": product_table['price'],
            },
            time="11:10",  # ✅ FIXED
            narration="Record shopping expense",
            user_instruction=f"Open Pro Expense and record the expense I just bought.",
            reset_user_instruction=(
                f"Open Pro Expense app and add a new expense: "
                f"amount ${product_table['price']:.2f} for the outdoor table purchase."
            ),
            max_steps=20,
            context_updates={'weekly_spend': product_table['price']},
        )
        
        # W1-09: ✅ Newly added: First meeting progress tracking (Message QA)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=9, task_id="W1-09",
            evaluator_name="LayeredSMSProgressSummary",
            params={
                "target_meeting": meeting_a['title'],
                "expected_attendees": meeting_a['attendees'],
                "min_reply_count": 2,
            },
            time="15:00",  # ✅ OK: Several hours after the meeting
            narration="Check who replied to meeting A reminders",
            user_instruction="Check the SMS messages. Those 4 people I sent meeting reminders to this morning - who has replied? Give me a quick summary.",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. I sent meeting reminders this morning to: "
                f"{', '.join(meeting_a['attendees_full'])}. "
                f"Check who has replied to the '{meeting_a['title']}' meeting reminder. "
                f"Give me a summary of who replied and who hasn't."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'meetingA_rsvp_v1': 'checked'},
            tags=["REF", "AGG"],
        )
        
        # W1-10: Evening summary (reuse A10)
        self.add_subtask_to_day(
            day_idx=0, subtask_id=10, task_id="W1-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "must_mention_meeting": True,
                "meeting_keywords": [meeting_a['title'], "meeting", "9am"],
                "must_mention_expense": True,
                "expense_amount": product_table['price'],
            },
            time="20:00",  # ✅ FIXED: Evening
            narration="Evening summary in WorkLog: meeting + expense",
            user_instruction="Open Markor and add a daily summary to WorkLog.md mentioning today's key events ( must include meeting name, time, location, and today's expense).",
            reset_user_instruction=(
                f"Open Markor, open 'WorkLog.md' and append a daily summary. "
                f"The summary must mention: the '{meeting_a['title']}' at 9:00 AM in '{meeting_a['location']}', "
                f"and today's expense of ${product_table['price']:.2f}."
            ),
            max_steps=20,
            context_updates={'worklog_appended_day1': True},
        )
    
    # ==================== Day 2: Tuesday - Memory Misleading ====================
    
    def _add_day2_subtasks(self, params: dict):
        """Day 2 (Tuesday): 11 tasks – Fully reuse the tested implementation from Scenario C"""
        user_name = params['user_name']
        seminar = params['seminar']
        meeting_a = params['meeting_a']
        
        # ========== W2-01: Alarm + create Seminar calendar event (reuse C1) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=11, task_id="W2-01",
            evaluator_name="LayeredCrossAppClockCalendar",
            params={
                "alarm_time_hour": 7,
                "alarm_time_minute": 30,
                "alarm_label": "Morning Seminar",
                "event_title": seminar['title'],
                "event_hour": 9,
                "event_minute": 0,
                "event_duration_minutes": 90,
                "event_location": seminar['location'],
                "event_description": f"Attendees: {', '.join(seminar['attendees'])}",
            },
            time="07:00",
            narration=f"Morning. Set alarm for seminar and create calendar event.",
            user_instruction=f"Set an alarm for 7:30 AM labeled 'Morning Seminar'. "
                            f"Then create a calendar event titled '{seminar['title']}' at 9:00, "
                            f"duration 90 minutes, in {seminar['location']}, with attendees: {', '.join(seminar['attendees'])}.",
            reset_user_instruction=(
                f"Complete two tasks: "
                f"(1) Open Clock app and set an alarm for 7:30 AM labeled 'Morning Seminar'. "
                f"(2) Open Simple Calendar Pro and create an event titled '{seminar['title']}' "
                f"at 9:00 AM, duration 90 minutes, location '{seminar['location']}', "
                f"attendees: {', '.join(seminar['attendees'])}."
            ),
            max_steps=35,
            context_updates={'seminar_created': True},
        )
        
        # ========== W2-02: Classroom audio recording (reuse C2) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=12, task_id="W2-02",
            evaluator_name="LayeredAudioRecorderRecordAudio",
            params={},
            time="08:05",
            narration=f"Seminar begins. Need high-quality recording.",
            user_instruction="Open Audio Recorder, change the sample rate to 32kHz and set the recording format to Wav for better quality, start recording the lecture, and then stop the recording after a few seconds to save the file.",
            reset_user_instruction=(
                "Open Audio Recorder. Go to Settings, change the sample rate to 32kHz "
                "and set the recording format to Wav. Then return to the main screen, "
                "start recording the lecture, and stop the recording after a few seconds to save the file."
            ),
            max_steps=25,
            context_updates={'audio_tue_recording': True},
        )
        
        # ========== W2-03: Record expense from receipt (reuse C3) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=13, task_id="W2-03",
            evaluator_name="LayeredExpenseFromReceipt",
            params={
                "amount": 6.80,
                "receipt_file": "breakfast_receipt.png",
            },
            time="10:30",
            narration="After seminar, had breakfast. The receipt is saved in the Download folder.",
            user_instruction="Check the breakfast receipt in Files (Download folder) and record the expense in Pro Expense.",
            reset_user_instruction=(
                "Open Files app, go to the Download folder and find 'breakfast_receipt.png'. "
                "The receipt shows $6.80 for breakfast. Open Pro Expense and record this expense of $6.80."
            ),
            max_steps=30,
            context_updates={'expense_tue_breakfast': 6.80, 'weekly_spend': '+6.80'},
        )
        
        # ========== W2-04: Rename and move audio recording (reuse C4) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=14, task_id="W2-04",
            evaluator_name="LayeredCrossAppAudioRecorderFiles",
            params={
                "expected_filename": "Seminar_Tue",
                "target_folder": "Documents/Lectures",
            },
            time="12:00",
            narration="To review later, need to organize the recording file.",
            user_instruction="Rename my morning audio recording to 'Seminar_Tue'. "
                            "Then move this file to the 'Documents/Lectures' folder in Files. Create the folder if needed.",
            reset_user_instruction=(
                "Open Audio Recorder, record a short audio clip and save it as 'Seminar_Tue'. "
                "Then open Files, find the recording, and move it to the 'Documents/Lectures' folder "
                "(create the folder if it doesn't exist)."
            ),
            max_steps=35,
            context_updates={'audio_tue_organized': True},
        )
        
        # ========== W2-05: Modify the time of "this morning's seminar" and send notification (reuse C5, with modified reference) ==========
        # Prepare participant information
        attendees_for_sms = [{"name": name, "number": phone} for name, phone in zip(seminar['attendees'], ['555-0201', '555-0202', '555-0203', '555-0204'])]
        
        self.add_subtask_to_day(
            day_idx=1, subtask_id=15, task_id="W2-05",
            evaluator_name="LayeredCrossAppMeetingUpdateNotify",
            params={
                "update_type": "time",
                "event_title": seminar['title'],
                "original_hour": 9,
                "original_minute": 0,
                "new_hour": 10,
                "new_minute": 0,
                "duration_minutes": 90,
                "location": seminar['location'],
                "attendees": attendees_for_sms,
                "message_must_contain": ["10:00"],
            },
            time="08:30",
            narration="Need to postpone this morning's seminar before it starts.",
            user_instruction="The seminar we discussed this morning needs to be moved to 10:00. "
                            "Update it in the calendar, then use Simple SMS Messenger to notify all participants about the new time.",
            reset_user_instruction=(
                f"Open Simple Calendar Pro, find '{seminar['title']}' at 9:00 AM and change it to 10:00 AM "
                f"(keep 90-minute duration, location '{seminar['location']}'). "
                f"Then open Simple SMS Messenger and notify all participants: "
                f"{', '.join(seminar['attendees'])} — tell them the new time is 10:00 AM."
            ),
            max_steps=45,
            context_updates={'seminar_time_updated': True},
            tags=["REF"],
        )
        
        # ========== W2-06: Shopping (reuse C6) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=16, task_id="W2-06",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": "B00J2FALDK",
                "product_name_keywords": ["SanDisk"],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": ["B00J2FALDK"]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="16:00",
            narration="After the seminar, need to order USB drives for data backup.",
            user_instruction="On the current webpage (ignore the internet access), clear my cart, add the 'SanDisk Cruzer Glide 16GB' to my cart and place an order.",
            reset_user_instruction=(
                "On the current shopping website (ignore the internet access), "
                "clear the cart, then search for 'SanDisk Cruzer Glide 16GB', "
                "add it to the cart and place an order."
            ),
            max_steps=35,
            context_updates={'orderB_sku': 'B00J2FALDK'},
        )
        
        # ========== W2-07: Exercise preparation - playlist + OpenTracks (reuse C7) ==========
        # available_songs matches the song list created in _cleanup_retromusic
        available_songs = [
            'My Heart is Yours', 'Endless Summer', 'Whispering Wind', 'Lost in the Echo',
            'Chasing Shadows', 'Night Drive', 'Echoes of Silence', 'Bright Lights',
            'Moments', 'Forever Young', 'Rising Sun', 'Silent Dreams',
            'City of Stars', 'Moonlight Sonata', 'Through the Storm', 'Return to Paradise',
        ]
        
        self.add_subtask_to_day(
            day_idx=1, subtask_id=17, task_id="W2-07",
            evaluator_name="LayeredCrossAppMusicPlaylistTrack",
            params={
                "playlist_name": "Workout Mix",
                "min_duration_minutes": 30,
                "available_songs": available_songs,  # ✅ Uses the song list from initialize
                "shuffle_play": True,
                "start_tracking": True,
            },
            time="17:30",
            narration="Want to exercise. Need to create a workout playlist (at least 30 minutes) and start tracking.",
            user_instruction="Create a 30+ minute playlist 'Workout Mix', shuffle play it, then start OpenTracks.",
            reset_user_instruction=(
                "Open Retro Music app and create a new playlist named 'Workout Mix'. "
                "Add enough songs to make it at least 30 minutes long (choose any from the library). "
                "Set it to shuffle play. Then open OpenTracks and start recording your activity."
            ),
            max_steps=45,
            context_updates={'exercise_started': True},
        )
        
        # ========== W2-08: Consolidate SMS replies into Markor (reuse C8) ==========
        # Note: SMS initialization is handled in initialize_subtask (see scenario_c)
        # ⚠️ Use the correct seminar attendees: Alice, Charlie, Diana
        self.add_subtask_to_day(
            day_idx=1, subtask_id=18, task_id="W2-08",
            evaluator_name="LayeredMarkorSMSSummary",
            params={
                "file_name": "DiscussionSummary.md",
                "required_keywords": ["alice", "charlie", "diana", "paper", "review", "code"],  # seminar attendees
                "distractor_keywords": ["john", "bob", "lunch", "book"],  # Meeting A attendees used as distractors
                "progress_replies": [
                    {"from": "Alice Davis", "content": "Finished the paper abstract section"},
                    {"from": "Charlie Davis", "content": "Completed the review of section 2"},
                    {"from": "Diana Davis", "content": "Implementation code is ready"},
                ],
                "distractor_messages": [
                    {"from": "John Smith", "content": "Want to grab lunch?"},
                    {"from": "Bob Johnson", "content": "Have you read that book?"},
                ],
            },
            time="19:00",
            narration="After the discussion, everyone replied with their progress via SMS. Need to compile them into a document.",
            user_instruction="Check Simple SMS Messenger for the progress replies from the team in today's seminar. "
                            "Create a new file 'DiscussionSummary.md' in Markor and summarize what each person reported.",
            reset_user_instruction=(
                "Open Simple SMS Messenger. Look for messages from Alice Davis, Charlie Davis, and Diana Davis "
                "about their seminar work progress. "
                "Create a new file 'DiscussionSummary.md' in Markor and summarize what each person reported. "
                "Ignore unrelated messages (e.g., from John Smith or Bob Johnson)."
            ),
            max_steps=35,
            context_updates={'seminar_progress_compiled': True},
        )
        
        # ========== W2-09: Create scheduled document (reuse C9) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=19, task_id="W2-09",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "DailySchedule.md",
                "required_sections": [
                    seminar['title'].split(':')[0].lower(),  # seminar title
                    "10:00",  # time after update
                    seminar['location'].lower(),  # location
                    "6.8",  # ✅ Breakfast expense (use 6.8, which matches both "6.8" and "6.80")
                ],
            },
            time="21:00",
            narration="Before sleep, want to record today's key events.",
            user_instruction="Create a new file 'DailySchedule.md' in Markor. Record today's schedule including: "
                            "(1) Today's meeting info (title, time, location), "
                            "(2) Breakfast expense.",
            reset_user_instruction=(
                f"Open Markor and create a new file 'DailySchedule.md'. "
                f"Record today's schedule: "
                f"(1) Seminar info: '{seminar['title']}' at 10:00 AM in '{seminar['location']}'; "
                f"(2) Breakfast expense: $6.80."
            ),
            max_steps=30,
            context_updates={'daily_schedule_created': True},
        )
        
        # ========== W2-10: Record audio recording file name into summary document (reuse C10) ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=20, task_id="W2-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "DailySchedule.md",
                "append_content": "Seminar_Tue",
            },
            time="21:30",
            narration="Almost forgot! Need to note down the recording file name for tomorrow's review.",
            user_instruction="Add a line mentioning today morning's recording file name to the markdown file you just created.",
            reset_user_instruction=(
                "Open Markor, open 'DailySchedule.md' and add a line at the end "
                "mentioning the recording file name 'Seminar_Tue' from today's lecture."
            ),
            max_steps=20,
            context_updates={'audio_referenced': True},
        )
        
        # ========== W2-11: ✅ New: Track Meeting A progress for the second time ==========
        self.add_subtask_to_day(
            day_idx=1, subtask_id=21, task_id="W2-11",
            evaluator_name="LayeredSMSProgressSummary",
            params={
                "target_meeting": meeting_a['title'],  # ✅ Lock onto Meeting A!
                "expected_attendees": meeting_a['attendees'],
                "min_reply_count": 2,
            },
            time="20:30",
            narration="Check yesterday's weekly meeting progress for replies",
            user_instruction="Check yesterday's weekly meeting notification - those 4 people I reminded, who hasn't replied yet?",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Yesterday I sent meeting reminders to: "
                f"{', '.join(meeting_a['attendees_full'])} about the '{meeting_a['title']}'. "
                f"Check who has replied and who hasn't yet. Summarize briefly."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'meetingA_progress_checked_v2': True},
            tags=["REF", "AGG"],
        )
    
    # ==================== Day 3: Wednesday - Spatiotemporal Conflicts ====================
    
    # ==================== Day 3: Wednesday - Spatiotemporal Conflicts ====================
    
    def _add_day3_subtasks(self, params: dict):
        """Day 3 (Wednesday): 11 tasks - Fully reuse the tested implementation from Scenario D"""
        user_name = params['user_name']
        
        # ========== W3-01: World Clock + Read flight time from image → calendar (reuse D-E1) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=22, task_id="W3-01",
            evaluator_name="LayeredCrossAppWorldClockCalendar",
            params={
                "city_name": "San Francisco",
                "event_title": "Flight to SF",
                "event_hour": 9,
                "event_minute": 30,
                "info_file": "Conference_Trip_Info.png",
            },
            time="06:50",
            narration="Business trip Day 1: Read flight info from image, add world clock, create calendar event",
            user_instruction="Morning. Open the Clock app and add 'San Francisco' to World Clock. "
                            "Then, open Files, find 'Conference_Trip_Info.png' in Download, "
                            "check the flight time and add a calendar event titled 'Flight to SF' at that time.",
            reset_user_instruction=(
                "Complete two tasks: "
                "(1) Open the Clock app, go to the 'World Clock' tab and add 'San Francisco'. "
                "(2) Open Files app, find 'Conference_Trip_Info.png' in the Download folder "
                "and confirm the flight departure time is 9:30 AM, then open Simple Calendar Pro "
                "and create a new event titled 'Flight to SF' at 9:30 AM."
            ),
            max_steps=35,
            context_updates={'trip_city': 'San Francisco', 'trip_tz': 'PST', 'flight_from_image': True},
            tags=["STR"],
        )
        
        # ========== W3-02: ✅ New: Resolve flight and meeting time conflict ==========
        # During initialization, "Morning Meeting" (10:00–11:00) is pre-created, conflicting with Flight (9:30–12:30)
        # The agent must reschedule the meeting to start 90 minutes after landing (14:00), lasting 1 hour
        self.add_subtask_to_day(
            day_idx=2, subtask_id=23, task_id="W3-02",
            evaluator_name="LayeredCrossAppMeetingUpdateNotify",
            params={
                "update_type": "time",
                "event_title": "Morning Meeting",
                "original_hour": 10,
                "original_minute": 0,
                "new_hour": 14,
                "new_minute": 0,
                "duration_minutes": 60,
                "attendees": [],  # ✅ Empty list, no SMS check
                "distractor_contacts": [],
                "message_must_contain": [],
            },
            time="07:00",
            narration="There's a 'Morning Meeting' at 10:00 that conflicts with flight (9:30-12:30), need to reschedule",
            user_instruction="Check my calendar. I notice there's a 'Morning Meeting' that conflicts with my flight time. "
                            "Reschedule it to start 90 minutes after the flight lands, with a 1-hour duration.",
            reset_user_instruction=(
                "Open Simple Calendar Pro. There's a 'Morning Meeting' at 10:00 and a 'Flight to SF' at 9:30 "
                "(flight duration is 3 hours, lands at 12:30). "
                "Reschedule 'Morning Meeting' to 14:00 (90 minutes after landing) with a 1-hour duration."
            ),
            max_steps=25,
            requires_answer=False,
            context_updates={'flight_conflict_resolved': True},
            tags=["CON"],
        )
        
        # ========== W3-03: One-time alarm + Highest-priority task list (reuse D-E2) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=24, task_id="W3-03",
            evaluator_name="LayeredCrossAppClockTasks",
            params={
                "alarm_hour": 7,
                "alarm_minute": 15,
                "alarm_label": "Leave for Airport",
                "is_one_time": True,
                "task_title": "Check Passport and Laptop Charger",
                "task_priority": "highest",
            },
            time="07:10",
            narration="While packing, need a final reminder to leave on time and a checklist item for essential items.",
            user_instruction="Set a one-time alarm for 7:15 AM labeled 'Leave for Airport'. "
                            "Then open Tasks and add a new task 'Check Passport and Laptop Charger' "
                            "with the highest priority, due today.",
            reset_user_instruction=(
                "Complete two tasks: "
                "(1) Open Clock app, set a one-time alarm for 7:15 AM labeled 'Leave for Airport'. "
                "(2) Open Tasks app, add a new task 'Check Passport and Laptop Charger' "
                "with the highest priority, due today."
            ),
            max_steps=25,
            context_updates={'trip_alarm_set': True, 'trip_tasks_top': True},
        )
        
        # ========== W3-04: Bluetooth + Do Not Disturb (DND) (reuse D-E3) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=25, task_id="W3-04",
            evaluator_name="LayeredSystemBluetoothDND",
            params={
                "bluetooth_on": True,
                "dnd_on": True,
            },
            time="08:30",
            narration="In the airport lounge, need to connect noise-canceling headphones and enable Do Not Disturb mode.",
            user_instruction="Turn on Bluetooth in Settings. Then enable Do Not Disturb mode "
                            "so I won't be interrupted during the flight.",
            reset_user_instruction=(
                "Open Settings: "
                "(1) Turn on Bluetooth (for noise-canceling headphones). "
                "(2) Enable Do Not Disturb mode (for the flight)."
            ),
            max_steps=20,
            context_updates={'bluetooth_on': True, 'dnd_on': True},
        )
        
        # ========== W3-05: Emergency travel gear replenishment (reuse D-E4) ==========
        product_sku = 'B00J2FALDK'
        product_name = 'SanDisk Cruzer Glide 16GB (2 Pack) USB 2.0 Flash Drive'
        office_address = '123 Tech Park Drive, Suite 400'
        address_keywords = ['123 Tech Park Drive', 'Suite 400']
        
        self.add_subtask_to_day(
            day_idx=2, subtask_id=26, task_id="W3-05",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_sku,
                "product_name_keywords": ["SanDisk", "16GB"],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [product_sku]
                        }
                    },
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.box-order-shipping-address .box-content').outerText",
                        "required_contents": {
                            "must_include": address_keywords
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="10:00",
            narration="Realize need a USB drive for handling presentation data.",
            user_instruction=f"On the current webpage (ignore the internet access), search for '{product_name}'. "
                            f"Add it to cart and complete the purchase. "
                            f"During checkout, use the office shipping address from the trip info image I viewed earlier.",
            reset_user_instruction=(
                f"On the current shopping website (ignore the internet access), "
                f"search for '{product_name}' (SKU: {product_sku}). "
                f"Add it to cart. During checkout, use shipping address: "
                f"{office_address}, San Francisco. Complete the purchase."
            ),
            max_steps=40,
            context_updates={'orderC_sku': product_sku},
        )
        
        # ========== W3-06: Create hotel contact (preparation for subsequent W3-07) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=27, task_id="W3-06",
            evaluator_name="LayeredContactsAddContact",
            params={
                "name": "Hotel Front Desk",
                "number": "415-555-0199",
                "address": "480 Sutter Street",
            },
            time="13:00",
            narration="Add hotel front desk contact for easy reference during the trip",
            user_instruction="Add a new contact: 'Hotel Front Desk', number 415-555-0199, address 480 Sutter Street",
            reset_user_instruction=(
                "Open the Contacts app and add a new contact: "
                "Name: 'Hotel Front Desk', Phone: 415-555-0199, Address: 480 Sutter Street."
            ),
            max_steps=20,
            context_updates={'hotel_contact_created': True},
        )
        
        # ========== W3-07: Partner outreach and information sharing (reuse D-E5) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=28, task_id="W3-07",
            evaluator_name="LayeredCrossAppContactsSmsVcf",
            params={
                "recipient_name": "Sarah Miller",
                "recipient_phone": "555-0801",  # ✅ External contact, avoiding conflict with Bob Johnson (555-0102)
                "message_text": "I've arrived safely",
                "vcf_contact_name": "Hotel Front Desk",
                "vcf_contact_phone": "415-555-0199",
            },
            time="13:20",
            narration="After arrival, need to share the hotel front desk contact with a colleague arriving later.",
            user_instruction="Send a text to 'Sarah Miller' saying I've arrived safely, and include the Hotel Front Desk contact info from my Contacts.",
            reset_user_instruction=(
                "Open Simple SMS Messenger and send a message to 'Sarah Miller' (555-0801) "
                "saying 'I've arrived safely'. Also include the Hotel Front Desk contact information "
                "(415-555-0199) from your Contacts in the message."
            ),
            max_steps=25,
            context_updates={'hotel_contact_shared': True},
        )
        
        # ========== W3-08: Professional meeting audio recording configuration (reuse D-E6) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=29, task_id="W3-08",
            evaluator_name="LayeredAudioRecorderWithConfig",
            params={
                "recording_name": "Keynote_AI",
                "expected_format": "wav",
                "expected_sample_rate": "48kHz",
            },
            time="15:00",
            narration="The keynote session begins. Need high-quality recording for later review.",
            user_instruction="Open Audio Recorder. Go to Settings, set the format to 'Wav' "
                            "and sample rate to '48kHz'. "
                            "Then record a short clip, stop it, and rename it to 'Keynote_AI'.",
            reset_user_instruction=(
                "Open Audio Recorder. Go to Settings, set the format to 'Wav' and sample rate to '48kHz'. "
                "Then record a short clip, stop it, and rename it to 'Keynote_AI'."
            ),
            max_steps=30,
            context_updates={'audio_wed_keynote': 'Keynote_AI'},
        )
        
        # ========== W3-09: Archive reimbursement receipts (reuse D-E7, modified to use preloaded images) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=30, task_id="W3-09",
            evaluator_name="LayeredCameraAndFilesOrganize",
            params={
                "photo_type": "existing",  # ✅ Switch to checking existing file
                "source_filename": "dinner_receipt.png",  # ✅ Specify source file name
                "target_folder": "Jan_Trip/Receipts",
                "create_folder_if_missing": True,
            },
            time="18:30",
            narration="After dinner, need to organize the receipt photo I took earlier.",
            user_instruction="I've already taken a photo of my dinner receipt and it's in the Download folder. "
                            "Open Files, create a new folder 'Jan_Trip/Receipts' in the main directory, "
                            "and move that receipt photo into it.",
            reset_user_instruction=(
                "Open Files app. Find 'dinner_receipt.png' in the Download folder. "
                "Create a new folder 'Jan_Trip/Receipts' in the root of the sdk_gphone_x86_64 storage area "
                "and move the receipt photo into it."
            ),
            max_steps=35,
            context_updates={'receipt_archived': True},
        )
        
        # ========== W3-10: Travel expense accounting + TripSummary (reuse D-E8+E9 merge) ==========
        self.add_subtask_to_day(
            day_idx=2, subtask_id=31, task_id="W3-10",
            evaluator_name="LayeredCrossAppExpenseMarkor",
            params={
                "expenses": [
                    {"name": "Taxi to Hotel", "amount": 35.0, "category": "Transportation"},
                    {"name": "Hotel Stay", "amount": 250.0, "category": "Housing"},
                    {"name": "USB Drive", "amount": 19.99, "category": "Others"},
                ],
                "summary_file": "Day1_Summary.md",
                "summary_sections": ["Date", "Expenses", "Total"],
            },
            time="21:00",
            narration="Records transportation, accommodation, and shopping expenses, then summarizes trip in Markor.",
            user_instruction="Open Pro Expense. Record today's expenses: "
                            "$35.00 for 'Taxi to Hotel' (Transportation), "
                            "$250.00 for 'Hotel Stay' (Housing), "
                            "and $19.99 for 'USB Drive' (Others). "
                            "Then open Markor and create a file 'Day1_Summary.md' with today's trip info and expenses.",
            reset_user_instruction=(
                "Open Pro Expense and record today's trip expenses: "
                "$35.00 'Taxi to Hotel' (Transportation), "
                "$250.00 'Hotel Stay' (Housing), "
                "$19.99 'USB Drive' (Others). "
                "Then open Markor and create 'Day1_Summary.md' with today's date, expenses list, and total."
            ),
            max_steps=40,
            context_updates={'expense_trip_day1': 304.99, 'trip_summary_created': True},
        )
        
        # ========== W3-11: Financial trend over the past 3 days (reuse D-E10, increased difficulty) ==========
        # Detailed expenses for the past 3 days:
        # - Day-1 (Jan 18): history $25.00 (Lunch 12.50 + Coffee 12.50)
        # - Day 1 (Jan 19): history $48.99 (Breakfast 18.50 + Metro 15.00 + Supplies 15.49)
        # - Day 2 (Jan 20): user-added $6.80 (Campus Breakfast, W2-03)
        # - Day 3 (Jan 21): user-added $304.99 (Taxi 35 + Hotel 250 + USB 19.99, W3-10)
        # Total = 25.00 + 48.99 + 6.80 + 304.99 = 385.78
        self.add_subtask_to_day(
            day_idx=2, subtask_id=32, task_id="W3-11",
            evaluator_name="LayeredExpenseStatisticsQA",
            params={
                "budget": 180.00,
                "expected_total": 385.78,  # ✅ Includes history expenses + user-added expenses
                "is_over_budget": True,
                "must_contain_keywords": [],
                "min_keywords_found": 0,
                "time_range": "last_3_days",
            },
            time="22:30",
            narration="Check the last 3 days' financial trend to see if the trip spending is within budget.",
            user_instruction="Open Pro Expense. "
                            "Tell me the total amount I've spent in the last 3 days (including today). "
                            "Has it exceeded my $180 3-day budget?",
            reset_user_instruction=(
                "Open Pro Expense. Check the total expenses for the last 3 days (including today). "
                "My 3-day budget is $180. Have I exceeded it? By how much?"
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'spend_3day_checked': True},
            tags=["AGG"],
        )
    
    def _add_day4_subtasks(self, params: dict):
        """Day 4 (Thursday): 7 tasks - Budget warnings + Cross-app chains"""
        user_name = params['user_name']
        
        # W4-01: Retrieve total expenses for the last two days (Tue+Wed = 291.80+19.99 = 311.79)
        self.add_subtask_to_day(
            day_idx=3, subtask_id=33, task_id="W4-01",
            evaluator_name="LayeredExpenseWindowQA",
            params={
                "window_days": 2,  # Last 2 days (Tue-Wed, including today)
                "expected_min": 311.0,
                "expected_max": 312.0,
            },
            time="08:00",
            narration="Trip Day 2: Check last 2 days (including today) spending",
            user_instruction="Tell me total expenses for the last 2 days (including today)",
            reset_user_instruction=(
                "Open Pro Expense. Tell me the total amount I've spent in the last 2 days (including today)."
            ),
            max_steps=20,
            requires_answer=True,
            context_updates={'spend_last2days': 'checked'},
            tags=["AGG"],
        )
        
        # W4-02: ✅ Record all expenses from the most recent 3 days into the WorkLog (name + amount)
        # Expenses for the most recent 3 days (Mon+Tue+Wed):
        # - Day 1 (Monday): Table $54.99
        # - Day 2 (Tuesday): Breakfast $6.80, Taxi $35.00, Hotel $250.00
        # - Day 3 (Wednesday): USB Drive $19.99
        self.add_subtask_to_day(
            day_idx=3, subtask_id=34, task_id="W4-02",
            evaluator_name="LayeredMarkorAppendWithKeywords",
            params={
                "file_name": "WorkLog.md",
                # Must include all expense names and amounts (flexible matching)
                "must_contain_keywords": [
                    "table", "54.99",               # Day 1 (Monday): Table $54.99
                    "breakfast", "6.8",             # Day 2 (Tuesday): Breakfast $6.80
                    "taxi", "35",                   # Day 2 (Tuesday): Taxi $35.00
                    "hotel", "250",                 # Day 2 (Tuesday): Hotel $250.00
                    "usb", "19.99",                 # Day 3 (Wednesday): USB $19.99
                ],
                "min_keywords_found": 10,  # All 10 keywords must be found
            },
            time="08:30",
            narration="Record the last 3 days' expenses (name + amount) to WorkLog for review.",
            user_instruction="Record my last 3 days' expenses (including today) in WorkLog.md (just the name and amount for each).",
            reset_user_instruction=(
                "Open Pro Expense to check last 3 days' expenses: "
                "Table $54.99 (Monday), Breakfast $6.80 + Taxi $35.00 + Hotel $250.00 (Tuesday), "
                "USB Drive $19.99 (Wednesday). "
                "Open WorkLog.md in Markor and append all the expense names and amounts."
            ),
            max_steps=25,
            context_updates={'expense_logged': True},
            tags=["AGG"],
        )
        
        # W4-03: Find the keynote event in Calendar → set up a reminder (modify the event reminder to 5 minutes before)
        # 🔧 Fix: Do not use alarm; instead, modify the Calendar event's reminder setup
        self.add_subtask_to_day(
            day_idx=3, subtask_id=35, task_id="W4-03",
            evaluator_name="LayeredCalendarSetEventReminder",  # 🔧 Switch to Calendar reminder evaluator
            params={
                "event_keyword": "keynote",  # Find the keynote event in Calendar
                "reminder_minutes_before": 5,  # Set reminder 5 minutes before
            },
            time="13:00",
            narration="Find afternoon keynote in calendar and set 5-minute-before reminder",
            user_instruction="Check calendar for keynote event and set it to remind me 5 minutes before",
            reset_user_instruction=(
                "Open Simple Calendar Pro. Find the 'Keynote Speech' event at 14:00. "
                "Set a reminder to notify you 5 minutes before it starts."
            ),
            max_steps=25,
            context_updates={'keynote_reminder_set': True},
            tags=["CAU"],
        )
        
        # W4-04: ✅ Exercise time conflict — delay the conflicting meeting to start after exercise
        # User set daily exercise time in W1-03: 18:00–18:30 (30 minutes)
        # Environment initialization creates a "Team Discussion" meeting from 18:00–19:00, conflicting with exercise time
        # Agent must delay the meeting to start after exercise ends (after 18:30), i.e., 19:00–20:00
        self.add_subtask_to_day(
            day_idx=3, subtask_id=36, task_id="W4-04",
            evaluator_name="LayeredCrossAppMeetingUpdateNotify",
            params={
                "update_type": "time",
                "event_title": "Team Discussion",
                "original_hour": 18,
                "original_minute": 0,
                "new_hour": 19,  # 30 minutes after exercise ends (18:30 + 30 minutes = 19:00)
                "new_minute": 0,
                "duration_minutes": 60,  # Maintain 1 hour
                "attendees": [],  # Empty list; do not check SMS
                "distractor_contacts": [],
                "message_must_contain": [],
            },
            time="18:00",
            narration="Today's meeting (18:00-19:00) conflicts with my weekly exercise time (18:00-18:30). Need to reschedule the meeting.",
            user_instruction="Check my calendar. I notice 'Team Discussion' at 18:00 conflicts with my daily exercise time. "
                            "Reschedule this meeting to start 30 minutes after my exercise ends, keeping the 1-hour duration.",
            reset_user_instruction=(
                "Open Simple Calendar Pro. There's a 'Team Discussion' at 18:00-19:00 that conflicts with "
                "my daily exercise time (18:00-18:30). "
                "Reschedule 'Team Discussion' to 19:00 (30 min after exercise ends), keep 1-hour duration."
            ),
            max_steps=25,
            requires_answer=False,
            context_updates={'exercise_conflict_resolved': True},
            tags=["PRE", "CON"],
        )
        
        # W4-05: ✅ Append today's meeting records (name + time) to TripSummary
        # Day 4 (January 22) meetings:
        # - Keynote: 14:00 (afternoon meeting, used in W4-03)
        # - Team Discussion: 19:00 (rescheduled time, modified in W4-04)
        self.add_subtask_to_day(
            day_idx=3, subtask_id=37, task_id="W4-05",
            evaluator_name="LayeredMarkorAppendWithKeywords",
            params={
                "file_name": "TripSummary.md",
                # Must include both today's meetings' names and times
                "must_contain_keywords": [
                    "keynote", "14:00",           # Keynote meeting
                    "team", "discussion", "19:00", # Team Discussion (rescheduled)
                ],
                "min_keywords_found": 5,  # All 5 keywords must be found
            },
            time="20:00",
            narration="Append Day 2 trip summary to TripSummary.md: record today's meetings (name + time).",
            user_instruction="Open TripSummary.md (if not exists, create it) and add Day 2 summary. Check my calendar for today's meetings and record them (meeting name and time).",
            reset_user_instruction=(
                "Open Simple Calendar Pro and check today's meetings: "
                "'Keynote Speech' at 14:00 and 'Team Discussion' at 19:00. "
                "Open 'TripSummary.md' in Markor (create if not exists) and append Day 2 summary "
                "listing these meetings with their names and times."
            ),
            max_steps=25,
            context_updates={'trip_summary_appended_day2': True},
            tags=["AGG"],
        )
        
        # W4-06: ✅ New: Write tomorrow's return flight (from image) into Markor
        self.add_subtask_to_day(
            day_idx=3, subtask_id=38, task_id="W4-06",
            evaluator_name="LayeredImageToMarkor",
            params={
                "image_folder": "Download",
                "image_keyword": "return",
                "output_file": "ReturnFlight.md",
                "extract_fields": ["flight_number", "time"],
                # 🔧 Fix: Add required keywords (flight number and time)
                "must_contain_keywords": ["UA 789", "18:30", "flight"],
                "min_keywords_found": 3,
            },
            time="20:30",
            narration="Extract return flight info from image and save to Markor",
            user_instruction="Check return flight image in Downloads and save info (flight number and time) to ReturnFlight.md (if not exists, create it)",
            reset_user_instruction=(
                "Open Files app, find the return flight image in the Download folder "
                "(look for a file with 'return' in the name). "
                "Extract the flight number and departure time from the image. "
                "Create a file 'ReturnFlight.md' in Markor with this info: flight UA 789, time 18:30."
            ),
            max_steps=25,
            context_updates={'return_flight_info_saved': True},
        )
        
        # W4-07: ✅ New: Send an SMS to colleagues confirming tomorrow's travel and return time
        self.add_subtask_to_day(
            day_idx=3, subtask_id=39, task_id="W4-07",
            evaluator_name="LayeredSmsSendMessage",
            params={
                "contact_name": "Sarah Miller",
                "number": "555-0801",  # ✅ External contact, avoiding conflict with Bob Johnson (555-0102)
                "message_must_contain": ["tomorrow", "22:30"],  # 🔧 Simplified: Check only keywords
            },
            time="21:00",
            narration="Text colleague about tomorrow's return trip",
            user_instruction="Send SMS to Sarah: tomorrow I'll be on the way back, include my arrival time",
            reset_user_instruction=(
                "Open Simple SMS Messenger and send a message to 'Sarah Miller' (555-0801). "
                "Tell her that tomorrow I'll be on my way back, and my estimated arrival time is 22:30."
            ),
            max_steps=20,
            context_updates={'return_trip_notified': True},
            tags=["CAU"],
        )
    
    # ==================== Day 5: Friday - Meeting B + Ask-before-buy + Meeting A Wrap-up ====================
    
    def _add_day5_subtasks(self, params: dict):
        """Day 5 (Friday): 8 tasks — resume work + advance Meeting B + conclude Meeting A"""
        user_name = params['user_name']
        meeting_a = params['meeting_a']
        meeting_b = params['meeting_b']
        seminar = params['seminar']
        
        # ========== W5-01: Check next Monday's calendar (new task — Calendar QA) ==========
        self.add_subtask_to_day(
            day_idx=4, subtask_id=40, task_id="W5-01",
            evaluator_name="LayeredCalendarCheckMeetingAnswer",
            params={
                "must_contain_keywords": [meeting_b['title'].lower()],
                "min_keywords_found": 1,
            },
            time="09:00",
            narration=f"Back to office: Check next Monday schedule (Meeting B: {meeting_b['title']})",
            user_instruction="Check next Monday's calendar and tell me what meetings I have",
            reset_user_instruction=(
                f"Open Simple Calendar Pro. Check next Monday's schedule and tell me "
                f"what meetings are scheduled. The main meeting is '{meeting_b['title']}' at 10:00."
            ),
            max_steps=20,
            requires_answer=True,
            context_updates={'meetingB_title': meeting_b['title']},
        )
        
        # ========== W5-02: ✅ Send SMS: notify only Meeting B attendees (trap) ==========
        # Build Meeting B contact mapping
        contacts_map_b = {}
        for i, name in enumerate(meeting_b['attendees_full']):
            contacts_map_b[name] = f"555-03{i+1:02d}"  # Meeting B uses 555-03xx
        
        self.add_subtask_to_day(
            day_idx=4, subtask_id=41, task_id="W5-02",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": meeting_b['attendees_full'],
                "message_must_contain_time": "10:00",
                "message_must_contain_location": [meeting_b['location']],
                "forbidden_recipients": meeting_a['attendees_full'] + seminar['attendees_full'],
                "min_messages_sent": len(meeting_b['attendees']),
                "contacts_map": contacts_map_b,  # ✅ Add contact mapping
            },
            time="09:30",
            narration="Notify next Monday's meeting attendees",
            user_instruction="Send SMS to next Monday's meeting attendees to remind them (include time and location)",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Send a message to each of the following people "
                f"({', '.join(meeting_b['attendees_full'])}) "
                f"to remind them about '{meeting_b['title']}' next Monday at 10:00 in '{meeting_b['location']}'. "
                f"Send individual messages to each person."
            ),
            max_steps=30,
            context_updates={'meetingB_notified': True},
            tags=["REF"],
        )
        
        # ========== W5-03: ✅ First Meeting B progress tracking (refer to C8's SMS simulation) ==========
        self.add_subtask_to_day(
            day_idx=4, subtask_id=42, task_id="W5-03",
            evaluator_name="LayeredSMSProgressSummary",
            params={
                "target_meeting": meeting_b['title'],
                "expected_attendees": meeting_b['attendees'],
                "min_reply_count": 2,
                "exclude_events": [meeting_a['title'], seminar['title']],
            },
            time="14:00",
            narration="Check who confirmed for Meeting B",
            user_instruction="Check those people I just reminded, who confirmed? Summarize briefly",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Check the replies from the people you reminded earlier "
                f"about '{meeting_b['title']}'. The attendees are: {', '.join(meeting_b['attendees'])}. "
                f"Tell me who has confirmed and who hasn't replied yet."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'meetingB_rsvp_checked': True},
            tags=["REF", "AGG"],
        )
        
        # ========== W5-04: ✅ Redesigned: Purchase decision record (using QA task) ==========
        # "I plan to buy a 1xx xx; help me record in my weekly plan whether to buy it, including yes/no and rationale"
        # 🔧 This week's budget is $500; current spending is $415.77; remaining amount is $84.23, which allows purchasing
        product = params['products']['supplies']
        product_price = 150.0
        
        self.add_subtask_to_day(
            day_idx=4, subtask_id=43, task_id="W5-04",
            evaluator_name="LayeredCalendarCheckMeetingAnswer",  # Generic QA evaluator
            params={
                # 🔧 Fix: Budget not exceeded (415.77 < 500), but item price 150 > remaining 84.23; should not be purchased
                "must_contain_keywords": ["no", "budget", "exceed"],  # Expected answer: "no"
                "min_keywords_found": 2,
            },
            time="15:00",
            narration=f"Consider buying {product['name']} (${product_price}) - need to decide and explain",
            user_instruction=f"I'm thinking about buying {product['name']} for ${product_price}. "
                            f"Should I buy it? Answer yes or no and give me a reason why.",
            reset_user_instruction=(
                f"I'm considering buying '{product['name']}' for ${product_price:.2f}. "
                f"My weekly budget is $500 and I've already spent about $415.77 this week "
                f"(leaving only $84.23). Should I buy it? Answer yes or no with a reason."
            ),
            max_steps=20,
            requires_answer=True,
            context_updates={'purchase_decision_made': True},
            tags=["PRE"],
        )
        
        # ========== W5-05: ✅ Redesigned: Weekly spending summary + budget check (refer to D-E10) ==========
        # Weekly spending: Table $54.99 + Breakfast $6.80 + Taxi $35 + Hotel $250 + USB $19.99 + ... = $415.77
        # Weekly budget: $500
        # Remaining: $84.23
        weekly_budget = 500.0  # This week's budget
        expected_total = 415.77  # 🔧 Fix: Actual Day 1–5 total
        expected_remaining = 84.23  # Remaining amount
        
        self.add_subtask_to_day(
            day_idx=4, subtask_id=44, task_id="W5-05",
            evaluator_name="LayeredExpenseStatisticsQA",
            params={
                "budget": weekly_budget,
                "expected_total": expected_total,
                "is_over_budget": False,  # 🔧 Fix: Budget not exceeded
                "expected_remaining": expected_remaining,  # 🔧 Add remaining amount verification
                "must_contain_keywords": ["415", "84", "under", "left"],  # 🔧 Check numbers
                "min_keywords_found": 2,
                "time_range": "this_week",
            },
            time="15:30",
            narration="Check this week's total spending and compare to $500 budget",
            user_instruction="Check for this week's total spending. "
                            "Tell me the total and whether I'm over budget. If over, by how much? If under, how much do I have left?",
            reset_user_instruction=(
                f"Open Pro Expense. Check this week's total spending. "
                f"My weekly budget is $500. Tell me the total amount spent this week, "
                f"whether I'm over budget, and how much I have left."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'weekly_budget_checked': True},
            tags=["AGG"],
        )
        
        # ========== W5-06: Disabled Saturday morning alarm (reusing B1) ==========
        self.add_subtask_to_day(
            day_idx=4, subtask_id=45, task_id="W5-06",
            evaluator_name="LayeredClockDisableSpecificAlarm",
            params={
                "day_offset": 1,  # Saturday
                "alarm_time_hour": 9,  # 🔧 Fix: The actual created weekend alarm is at 09:30
                "alarm_time_minute": 30,
                "keep_weekday_alarms": True,
            },
            time="21:00",
            narration="Friday night: Disable Saturday morning alarm (keep weekday alarms)",
            user_instruction="Turn off tomorrow morning's alarm, I want to sleep in on Saturday",
            reset_user_instruction=(
                "Open the Clock app, go to the Alarm tab. "
                "Find the Saturday morning alarm set for 09:30 and turn it off. "
                "Do NOT disable any weekday alarms."
            ),
            max_steps=20,
            context_updates={'sat_alarm_disabled': True},
        )
        
        # ========== W5-07: ✅ Final summary of Meeting A progress tracking (refer to SMS simulation in C8) ==========
        self.add_subtask_to_day(
            day_idx=4, subtask_id=46, task_id="W5-07",
            evaluator_name="LayeredSMSProgressSummary",
            params={
                "target_meeting": meeting_a['title'],
                "expected_attendees": meeting_a['attendees'],
                "min_reply_count": 2,
                "exclude_events": [meeting_b['title'], seminar['title']],
                "check_final_status": True,  # Final summary
            },
            time="21:30",
            narration="Final wrap-up for Meeting A: Check SMS progress one last time",
            user_instruction="Check the progress of Monday's weekly meeting - who confirmed and who didn't? Summarize briefly",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Check the replies from attendees of '{meeting_a['title']}'. "
                f"The attendees are: {', '.join(meeting_a['attendees'])}. "
                f"Tell me the final status - who confirmed, who declined, and who hasn't replied?"
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'meetingA_final_checked': True},
            tags=["REF", "AGG"],
        )
        
        # ========== W5-08: ✅ Disable DND mode (enabled in W3-04, now disabling) ==========
        # 🔧 Fix: Replace the original Meeting B Agenda task (meaningless)
        self.add_subtask_to_day(
            day_idx=4, subtask_id=47, task_id="W5-08",
            evaluator_name="LayeredSystemBluetoothDND",
            params={
                "bluetooth_on": None,  # Do not check Bluetooth status
                "dnd_on": False,  # Disable DND
            },
            time="22:00",
            narration="Back home: Turn off Do Not Disturb mode (was on during travel)",
            user_instruction="Turn off Do Not Disturb mode in Settings. I'm back home now.",
            reset_user_instruction=(
                "Open Settings and turn off Do Not Disturb mode. "
                "The DND mode was enabled during travel and should now be disabled."
            ),
            max_steps=15,
            context_updates={'dnd_off': True},
        )
    # ==================== Day 6: Saturday - Weekend Relaxation (reusing Scenario B) ====================
    
    def _add_day6_subtasks(self, params: dict):
        """Day 6 (Saturday): 11 tasks - Weekend cooking + shopping + exercise + summary"""
        user_name = params['user_name']
        
        # ========== W6-01: Disabled Saturday morning alarm (fully reusing B1) ==========
        # 🔧 Fix: Only verify whether the weekend alarm is disabled; do not verify the weekday alarm
        self.add_subtask_to_day(
            day_idx=5, subtask_id=48, task_id="W6-01",
            evaluator_name="LayeredClockDisableWeekendAlarm",  # 🔧 Use a dedicated weekend evaluator
            params={
                "expected_alarm_hour": 9,  # Expected weekend alarm hour
                "expected_alarm_minute": 30,
                "check_saturday": True,  # Check Saturday
                "check_sunday": True,    # Also check Sunday
            },
            time="10:00",
            narration="Saturday morning: Confirm weekend alarm is off",
            user_instruction="Make sure this morning's alarm is turned off. Don't change my weekday alarms.",
            reset_user_instruction=(
                "Open the Clock app, go to the Alarm tab. "
                "Make sure the weekend alarm (Saturday/Sunday 09:30) is turned off. "
                "Do NOT modify weekday alarms."
            ),
            max_steps=15,
            context_updates={'sat_alarm_off_confirmed': True},
        )
        
        # ========== W6-02: Recipe search (fully reusing B2) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=49, task_id="W6-02",
            evaluator_name="LayeredBroccoliRecipeSearchQA",
            params={
                "query_keywords": ["egg", "breakfast", "quick"],
                "recipe_keywords": ["egg"],
                "ingredient_keywords": ["egg", "butter|oil", "salt"],
                "min_ingredient_keywords": 2,
                "max_prep_time_minutes": 15,
                "must_contain_prep_time": True,
                "correct_recipe_title": "Scrambled Eggs with Toast",
            },
            time="09:00",
            narration="Saturday morning, find a quick breakfast recipe",
            user_instruction="Open Broccoli Recipe and find a quick breakfast recipe that uses eggs AND takes 15 minutes or less to prepare. Tell me the recipe name, key ingredients, and the preparation time.",
            reset_user_instruction=(
                "Open the Broccoli Recipe app. Search for a quick breakfast recipe using eggs "
                "that takes 15 minutes or less to prepare. "
                "Tell me the recipe name, "
                "its key ingredients, and preparation time."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'recipe_selected': True},
        )
        
        # ========== W6-03: Write recipe note using Markor (fully reusing B3) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=50, task_id="W6-03",
            evaluator_name="LayeredMarkorCreateRecipeNote",
            params={
                "file_name": "SaturdayBreakfast.md",
                "required_sections": ["recipe", "ingredient", "step"],
                "min_steps": 3,
                "max_steps": 5,
                "expected_recipe_title": "Scrambled Eggs with Toast",
                "expected_ingredients": ["egg", "butter", "salt", "bread"],
                "expected_prep_time": 10,
            },
            time="09:30",
            narration="Write breakfast recipe to Markor note",
            user_instruction="Open Markor and create a markdown file called 'SaturdayBreakfast.md'. Write: (1) the recipe name you found, (2) an ingredients list, and (3) 3-5 short cooking steps.",
            reset_user_instruction=(
                "Open Markor and create a new file named 'SaturdayBreakfast.md'. "
                "Write the 'Scrambled Eggs with Toast' recipe with: "
                "(1) the recipe name, (2) ingredients list (eggs, butter, salt, bread), "
                "and (3) 3-5 short cooking steps."
            ),
            max_steps=30,
            context_updates={'sat_breakfast_doc_created': True},
        )
        
        # ========== W6-04: Timer setup (fully reusing B4) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=51, task_id="W6-04",
            evaluator_name="LayeredClockStartTimer",
            params={
                "minutes": 10,  # From recipe retrieval
                "seconds": 0,
            },
            time="10:15",
            narration="Start cooking timer based on recipe prep time",
            user_instruction="Set a cooking timer based on the recipe preparation time you found and start it.",
            reset_user_instruction=(
                "Open the Clock app, go to the Timer tab. "
                "Set a timer for 10 minutes (the prep time for Scrambled Eggs with Toast) and start it."
            ),
            max_steps=15,
            context_updates={'timer_started': True, 'prep_time_minutes': 10},
        )
        
        # ========== W6-05: Take breakfast photo with Camera and archive it (fully reusing B5) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=52, task_id="W6-05",
            evaluator_name="LayeredCameraAndFilesOrganize",
            params={
                "photo_type": "camera",
                "target_folder": "Weekend/Breakfast",
                "create_folder_if_missing": True,
            },
            time="10:30",
            narration="Take breakfast photo and organize to Weekend/Breakfast folder",
            user_instruction="Take a photo of my breakfast, then open Files and move it into a folder named 'Weekend/Breakfast'. If the folder doesn't exist, create it.",
            reset_user_instruction=(
                "Open the Camera app and take a photo. "
                "Then open Files, find the photo you just took (in the DCIM/Camera folder), "
                "create a folder named 'Weekend/Breakfast' in the root of sdk_gphone_x86_64 storage, "
                "and move the photo into it."
            ),
            max_steps=35,
            context_updates={'breakfast_photo_saved': True, 'photo_path': 'Weekend/Breakfast/'},
        )
        
        # ========== W6-06: Send meeting SMS message to friend (fully reusing B6) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=53, task_id="W6-06",
            evaluator_name="LayeredSmsSendMessage",
            params={
                "contact_name": "Bob Johnson",
                "number": "555-0102",  # ✅ Second person from Meeting A
                "message": "Let's meet at 3:00 PM at Central Park for a walk.",
            },
            time="14:00",
            narration="Text friend about afternoon meetup",
            user_instruction="Text Bob Johnson: 'Let's meet at 3:00 PM at Central Park for a walk.' Keep it friendly and clear.",
            reset_user_instruction=(
                "Open Simple SMS Messenger. Send a message to Bob Johnson (555-0102): "
                "'Let's meet at 3:00 PM at Central Park for a walk.'"
            ),
            max_steps=20,
            context_updates={'friend_meet_sms_sent': True},
        )
        
        # ========== W6-07: Major shopping order (reusing W5-04 design concept) ==========
        # Note: W5-04 was changed to a QA task; here, reuse B7's shopping task
        self.add_subtask_to_day(
            day_idx=5, subtask_id=54, task_id="W6-07",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": "B078158XZ4",
                "product_keywords": ["Egg", "Organic", "12"],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": ["B078158XZ4"]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="15:00",
            narration="Weekend shopping: order groceries online",
            user_instruction="On the current webpage (ignore the internet access), clear my cart, add the 'Egg Organic 12-count' to my cart and place an order.",
            reset_user_instruction=(
                "On the current shopping website (ignore the internet access), "
                "clear my cart, then search for 'Egg Organic 12-count' (SKU: B078158XZ4). "
                "Add it to the cart and place an order."
            ),
            max_steps=30,
            context_updates={'weekend_order_sku': 'B078158XZ4', 'weekend_order_amount': 11.8},
        )
        
        # ========== W6-08: Expense recording (reusing B8, not W5-05) ==========
        # Note: W5-05 is a statistical QA task; here, reuse B8's expense-addition task
        self.add_subtask_to_day(
            day_idx=5, subtask_id=55, task_id="W6-08",
            evaluator_name="LayeredExpenseAddSingle",
            params={
                "name": "Shopping",
                "amount": 11.8,
                "note": "Weekend groceries",
                "date": "2026-01-18",  # Saturday
            },
            time="15:30",
            narration="Record weekend shopping expense",
            user_instruction="Record this shopping purchase in Expense app, name it 'Shopping', use the order total from my last order as the amount.",
            reset_user_instruction=(
                "Open Pro Expense. Record a new expense named 'Shopping' with the amount $11.80. "
                "This was the weekend grocery order for Egg Organic 12-count."
            ),
            max_steps=20,
            context_updates={'expense_weekend_purchase_added': True, 'weekly_spend': '+11.8'},
        )
        
        # ========== W6-09: View walking data in OpenTracks (fully reused from B9) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=56, task_id="W6-09",
            evaluator_name="LayeredOpenTracksQueryActivityQA",
            params={
                "correct_distance_km": 2.5,
                "correct_duration_min": 35,
                "correct_location": "Central Park",
                "friend_name": "Bob Johnson",
                "meetup_time_hour": 15,
                "meetup_time_minute": 0,
                "distance_tolerance_km": 0.5,
                "duration_tolerance_min": 5,
            },
            time="16:00",
            narration="After walking with Bob, check the walk statistics",
            user_instruction="Open OpenTracks and find the walk I did with Bob Johnson. Tell me how long we walked (duration) and how far (distance).",
            reset_user_instruction=(
                "Open the OpenTracks app. Find the most recent walk activity "
                "(the one at Central Park with Bob Johnson around 3:00 PM). "
                "Tell me the duration and distance."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'sat_walk_checked': True, 'walk_duration': 35, 'walk_distance': 2.5},
        )
        
        # ========== W6-10: Send arrival SMS after walking (new) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=57, task_id="W6-10",
            evaluator_name="LayeredSmsSendMessage",
            params={
                "contact_name": "Bob Johnson",
                "number": "555-0102",  # ✅ Person 2 for Meeting A
                "message": "I've arrived home safely.",
                "message_must_contain": ["arrived", "home"],
            },
            time="16:45",
            narration="After walk: Send arrival SMS to Bob",
            user_instruction="Text Bob Johnson that I've arrived home safely",
            reset_user_instruction=(
                "Open Simple SMS Messenger. Send a message to Bob Johnson (555-0102) "
                "saying that you've arrived home safely."
            ),
            max_steps=15,
            context_updates={'arrival_sms_sent': True},
        )
        
        # ========== W6-11: Weekend summary (fully reused from B10) ==========
        self.add_subtask_to_day(
            day_idx=5, subtask_id=58, task_id="W6-11",
            evaluator_name="LayeredMarkorRenameAndAppendSummary",
            params={
                "original_file": "SaturdayBreakfast.md",
                "new_file": "weekendsummary.md",
                "expense_keywords": ["Egg", "11.8"],
                "track_keywords": ["walk", "bob"],
            },
            time="21:00",
            narration="Consolidate weekend notes: rename breakfast note to summary and add expense and activity info",
            user_instruction="Rename 'SaturdayBreakfast.md' to 'weekendsummary.md' in Markor. Then append a brief summary about today's shopping purchase and the walk with Bob Johnson.",
            reset_user_instruction=(
                "Open Markor. Rename the file 'SaturdayBreakfast.md' to 'weekendsummary.md'. "
                "Then append a brief summary including: "
                "(1) today's grocery order for Egg Organic ($11.80), "
                "(2) the afternoon walk with Bob Johnson at Central Park (35 min, 2.5 km)."
            ),
            max_steps=30,
            context_updates={'weekend_summary_appended': True},
        )
    # ==================== Day 7: Sunday - Weekly Review + Closures (reused from Scenario E + new additions) ====================
    
    def _add_day7_subtasks(self, params: dict):
        """Day 7 (Sunday): 12 tasks - Hiking + Weekly review + Meeting & SMS summaries"""
        user_name = params['user_name']
        meeting_a = params['meeting_a']
        meeting_b = params['meeting_b']
        seminar = params['seminar']
        
        # ========== W7-01: Picnic supplies verification (fully reused from E-F1) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=59, task_id="W7-01",
            evaluator_name="LayeredCrossAppRecipeTasks",
            params={
                "recipe_title": "Picnic BBQ",
                "required_items": ["Beef", "Chicken", "Tomato", "Lettuce"],  # meats and vegetables from the recipe
                "already_have": ["BBQ Sauce", "Salt"],  # 🔧 Fix: changed to seasonings to avoid conflict with Tomato
                "check_off_items": ["BBQ Sauce", "Salt"],
            },
            time="09:00",
            narration="Preparing for picnic: check recipe and create shopping list",
            user_instruction="Open the 'Picnic BBQ' recipe in Broccoli. Add all the required meat and vegetable ingredients to my Tasks app. Then, check off the items I already have: 'BBQ Sauce' and 'Salt'.",
            reset_user_instruction=(
                "Open the Broccoli Recipe app and find the 'Picnic BBQ' recipe. "
                "Open the Tasks app and add each of the following ingredients as a separate task: "
                "'Beef', 'Chicken', 'Tomato', 'Lettuce'. "
                "Then check off the tasks for items I already have: 'BBQ Sauce' and 'Salt'."
            ),
            max_steps=35,
            context_updates={'picnic_checklist_done': True},
        )
        
        # ========== W7-02: Event location change + notification (fully reused from E-F2) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=60, task_id="W7-02",
            evaluator_name="LayeredCrossAppCalendarUpdateSMS",
            params={
                "event_title": "Mountain Picnic",
                "old_location": "East Valley Trail",
                "new_location": "West Peak Lookout",
                "event_hour": 10,
                "event_minute": 0,
                "attendees": [
                    {"name": "Alice Davis", "number": "555-0201"},      # Person 1 for Seminar
                    {"name": "Charlie Brown", "number": "555-0202"},    # Person 2 for Seminar
                    {"name": "Diana Prince", "number": "555-0203"},     # Person 3 for Seminar
                    {"name": "Frank Castle", "number": "555-0204"}      # Person 4 for Seminar
                ],  # 🔧 Fix: use all seminar attendees
                "distractor_contacts": [],
                "message_must_contain": ["West Peak Lookout"],
                "user_name": user_name,
            },
            time="10:00",
            narration="Change picnic location and notify all participants",
            user_instruction="Open Simple Calendar Pro and change the location of today's 10:00 AM 'Mountain Picnic' to 'West Peak Lookout'. Then, text all participants of this change.",
            reset_user_instruction=(
                "Open Simple Calendar Pro. Find today's 10:00 AM event 'Mountain Picnic' "
                "and change its location from 'East Valley Trail' to 'West Peak Lookout'. "
                "Then open Simple SMS Messenger and notify all participants "
                "(Alice Davis 555-0201, Charlie Brown 555-0202, Diana Prince 555-0203, Frank Castle 555-0204) "
                "about the location change to 'West Peak Lookout'."
            ),
            max_steps=40,
            context_updates={'event_location_updated': True, 'attendees_notified': True},
        )
        
        # ========== W7-03: Create hiking playlist (fully reused from E-F3) ==========
        # Use real song titles (select 8 songs from available_songs)
        hiking_songs = [
            'My Heart is Yours', 'Endless Summer', 'Whispering Wind', 'Lost in the Echo',
            'Chasing Shadows', 'Night Drive', 'Echoes of Silence', 'Bright Lights'
        ]
        songs_list_str = ', '.join([f"'{s}'" for s in hiking_songs])
        
        self.add_subtask_to_day(
            day_idx=6, subtask_id=61, task_id="W7-03",
            evaluator_name="LayeredRetroMusicCreatePlaylist",
            params={
                "playlist_name": "Mountain Hike",
                "songs": hiking_songs,
                "require_order": True,
            },
            time="11:00",
            narration="Create sequential playlist for hiking",
            user_instruction=f"Create a playlist in Retro Music titled 'Mountain Hike'. Add the following songs in this exact order: {songs_list_str}.",
            reset_user_instruction=(
                f"Open the Retro Music app. Create a new playlist named 'Mountain Hike' "
                f"and add the following songs in this exact order: {songs_list_str}."
            ),
            max_steps=40,
            context_updates={'playlist_created': True},
        )
        
        # ========== W7-04: Start trajectory recording + music (fully reused from E-F4) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=62, task_id="W7-04",
            evaluator_name="LayeredCrossAppTracksMusic",
            params={
                "start_recording": True,
                "playlist_name": "Mountain Hike",
                "check_music_playing": True,
            },
            time="13:00",
            narration="Start hiking: record tracks and play music",
            user_instruction="Open OpenTracks and start recording my activity. Then, shuffle play the playlist I just created.",
            reset_user_instruction=(
                "Open the Retro Music app, create a new playlist named 'Mountain Hike' "
                f"and add the following songs in this exact order: {songs_list_str}. "
                "Then open OpenTracks and start recording a new activity. "
                "Finally, return to Retro Music and start shuffle play for the 'Mountain Hike' playlist."
            ),
            max_steps=45,
            context_updates={'sun_hike_started': True},
        )
        
        # ========== W7-05: Record video (fully reused from E-F5) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=63, task_id="W7-05",
            evaluator_name="LayeredCameraRecordVideo",
            params={
                "mode": "video",
                "enable_grid": True,
                "min_duration": 3,
            },
            time="14:00",
            narration="Record scenic video with grid lines",
            user_instruction="Switch Camera to 'Video' mode. Turn on the grid lines and record a short video.",
            reset_user_instruction=(
                "Open the Camera app. Switch to Video mode. "
                "Go to Settings and enable grid lines. "
                "Then record a video for at least 3 seconds and stop."
            ),
            max_steps=25,
            context_updates={'video_saved': True},
        )
        
        # ========== W7-06: Purchase meat alternatives (fully reused from E-F6) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=64, task_id="W7-06",
            evaluator_name="LayeredShoppingConstrainedPurchase",
            params={
                "product_sku": "B01CTR3DLE",
                "category": "Meat Substitute",
                "price_min": 100,
                "price_max": 200,
                "sort_by": "rating",
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {"must_include": ["B01CTR3DLE"]}
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="15:00",
            narration="Order meat substitute ($100-$200, highest rated)",
            user_instruction="On the current webpage (ignore the internet access), browse the meat substitute category and find the highest rated product with a price between $100 and $200. Add it to your cart and complete the purchase by placing an order.",
            reset_user_instruction=(
                "On the current shopping website (ignore the internet access), "
                "go to the 'Meat Substitute' category, sort by rating (highest first), "
                "find a product priced between $100 and $200, add it to cart, and complete the purchase."
            ),
            max_steps=40,
            context_updates={'orderE_sku': 'B01CTR3DLE', 'orderE_amount': 113.27},
        )
        
        # ========== W7-07: Exercise data statistics QA (fully reused from E-F7) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=65, task_id="W7-07",
            evaluator_name="LayeredOpenTracksStatsQA",
            params={
                "query_type": "weekly_summary",
                "activity_type": "Hiking",
                "require_distance": True,
                "require_duration": True,
            },
            time="17:00",
            narration="Check today's hike stats and weekly exercise summary",
            user_instruction="Open OpenTracks. Tell me today's distance and duration. Also, check my statistics for Hiking this entire week and summarize my total weekly distance and exercise time.",
            reset_user_instruction=(
                "Open the OpenTracks app. Tell me today's distance and duration for the hiking activity. "
                "Also, check my statistics for 'Hiking' this entire week "
                "and summarize my total weekly distance and exercise time."
            ),
            max_steps=30,
            requires_answer=True,
            context_updates={'weekly_hike_stats': 'checked'},
        )
        
        # ========== W7-08: Photo deduplication + classification (fully reused from E-F8) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=66, task_id="W7-08",
            evaluator_name="LayeredFilesOrganizeAndDedupe",
            params={
                "source_folder": "Pictures",
                "target_folders": ["Scenery", "Portraits"],
                "scenery_patterns": ["mountain", "lake", "waterfall", "view"],
                "portrait_patterns": ["group", "selfie", "lunch", "start"],
                "dedupe_required": True,
            },
            time="18:00",
            narration="Organize photos: categorize by theme and remove duplicates",
            user_instruction="In the 'Pictures' folder, create two subfolders: 'Scenery' and 'Portraits'. Move photos based on their filenames to these folders. If you find files with the same timestamp but different suffixes, keep only one copy and delete the duplicates.",
            reset_user_instruction=(
                "Open the Files app, navigate to the 'Pictures' folder. "
                "Create two subfolders: 'Scenery' and 'Portraits'. "
                "Move photos based on their filenames: "
                "scenery photos (mountain/lake/waterfall/view) → Scenery folder; "
                "portrait photos (group/selfie/lunch/start) → Portraits folder. "
                "If you find files with the same timestamp but different suffixes, "
                "keep only one copy and delete the duplicates."
            ),
            max_steps=40,
            context_updates={'photo_dedup_done': True},
        )
        
        # ========== W7-09: Weekly expense Q&A (fully reused from E-F9) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=67, task_id="W7-09",
            evaluator_name="LayeredExpenseWeeklyQA",
            params={
                "meat_name": "Meat Substitute",
                "meat_amount": 113.27,
                "weekly_total": 491.85,
            },
            time="19:00",
            narration="Record meat purchase and report weekly total spending",
            user_instruction="Record the meat substitute purchase in Pro Expense, then tell me: what is the total amount I spent this week?",
            reset_user_instruction=(
                "Open Pro Expense. Record the meat substitute purchase ($113.27) as a new expense. "
                "Then tell me the total amount I spent this week (should be around $491.85 after this purchase)."
            ),
            max_steps=30,
            requires_answer=True,
            context_updates={'weekly_spend_total_reported': True},
        )
        
        # ========== W7-10: ✅ New: Track progress of Meeting B for the second time (refer to SMS simulation in C8) ==========
        self.add_subtask_to_day(
            day_idx=6, subtask_id=68, task_id="W7-10",
            evaluator_name="LayeredSMSProgressSummary",
            params={
                "target_meeting": meeting_b['title'],
                "expected_attendees": meeting_b['attendees'],
                "min_reply_count": 2,
                "exclude_events": [meeting_a['title'], seminar['title']],
                "check_meeting_name": False,  # 🔧 Fix: do not check meeting name, only check person names
            },
            time="20:00",
            narration="Check Meeting B progress again (2nd time)",
            user_instruction="Check next Monday's meeting - who confirmed and who's still pending? Summarize briefly",
            reset_user_instruction=(
                f"Open Simple SMS Messenger. Check the replies from attendees of '{meeting_b['title']}' "
                f"scheduled for next Monday. The attendees are: {', '.join(meeting_b['attendees'])}. "
                f"Tell me who confirmed and who hasn't replied."
            ),
            max_steps=25,
            requires_answer=True,
            context_updates={'meetingB_progress_v2': 'checked'},
            tags=["REF", "AGG"],
        )
        
        # ========== W7-11: ✅ New: Weekly meeting summary (using Markor generic evaluator) ==========
        # Summarize meeting items for each day of the week, providing the time, location, and attendees for each meeting
        # 🔧 Fix: do not check date sections, only check meeting information
        meeting_names_to_check = [
            meeting_a['title'],
            meeting_b['title'],
            seminar['title'],
            "Flight to SF",
            "Morning Meeting",
            "Keynote Speech",
            "Team Discussion",
            "Mountain Picnic"
        ]
        
        self.add_subtask_to_day(
            day_idx=6, subtask_id=69, task_id="W7-11",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WeeklyMeetingSummary.md",
                "required_sections": meeting_names_to_check,  # 🔧 Check meeting names, not dates
                "sections_with_content": meeting_names_to_check,
                "check_locations": True,  # 🔧 Check locations
                "check_attendees": True,  # 🔧 Check attendees
            },
            time="20:30",
            narration="Summarize all meetings this week to Markor",
            user_instruction="Check my calendar for this entire week. Create a file 'WeeklyMeetingSummary.md' in Markor listing all meetings, including: date, time, location, and attendees for each meeting.",
            reset_user_instruction=(
                "Open Markor. Create a file 'WeeklyMeetingSummary.md'. "
                "Write a summary of all this week's meetings. Include for each meeting: "
                "title, date/time, location, and attendees. "
                "Meetings this week include: "
                f"'{meeting_a['title']}' (Monday 09:00), "
                f"seminar (Tuesday 09:00-10:30), "
                f"'Flight to SF' (Wednesday morning), "
                f"'Morning Meeting' (Wednesday afternoon), "
                f"'Keynote Speech' (Thursday 14:00), "
                f"'Team Discussion' (Thursday 19:00), "
                f"'{meeting_b['title']}' (next Monday 10:00), "
                f"'Mountain Picnic' (Sunday 10:00)."
            ),
            max_steps=30,
            context_updates={'weekly_meeting_summary_created': True},
        )
        
        # ========== W7-12: ✅ New: Weekly SMS statistics (simplified using QAtask) ==========
        # Count SMS messages received this week: 15 contacts, 16 messages
        self.add_subtask_to_day(
            day_idx=6, subtask_id=70, task_id="W7-12",
            evaluator_name="LayeredCalendarCheckMeetingAnswer",  # Generic QA evaluator
            params={
                "must_contain_keywords": ["15", "16"],  # 🔧 Fix: check specific numbers (15 contacts, 16 messages)
                "min_keywords_found": 2,
            },
            time="21:00",
            narration="Count received SMS: 15 unique senders, 16 total messages",
            user_instruction="Check my SMS messenger for this entire week. Count how many unique people sent me messages, and how many total messages I received. Tell me both numbers.",
            reset_user_instruction=(
                "Open Simple SMS Messenger. Check all received messages this entire week. "
                "Count how many unique people sent me messages, and how many total messages I received. "
                "Tell me both numbers."
            ),
            max_steps=30,
            requires_answer=True,
            context_updates={'weekly_sms_stats_reported': True},
        )
    
    # ==================== 🆕 Batch initialize method ====================
    
    def _setup_photos_for_w7_08(self, env):
        """
        🆕 Prepare photo files (for W7-08 task)
        
        Fully reuse scenario_e's _setup_photos implementation
        Create 8 photos: 4 scenery + 4 portrait (including 2 duplicates)
        """
        logging.info("   📷 Preparing W7-08 photo files...")
        
        from scendroid.env import device_constants, adb_utils
        import os
        import time
        
        try:
            base_path = device_constants.EMULATOR_DATA
            pictures_path = os.path.join(base_path, "Pictures")
            
            # Ensure the Pictures directory exists
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', pictures_path
            ], env.controller)
            
            # Get participant names (from seminar attendees)
            seminar = self.generated_params.get('seminar', {})
            seminar_attendees = seminar.get('attendees_full', [])
            friend_names = [name.split()[0] for name in seminar_attendees[:3]]  # Take the first names of the first three people
            
            # Scenic photos: time_location.png (4 images, including 1 duplicate)
            scenery_photos = [
                '1010_Mountain.png',              # 10:10 mountain view
                '1025_Lake.png',                  # 10:25 lake view
                '1025_Lake_copy.png',             # 10:25 lake view (duplicate)
                '1110_Waterfall.png',             # 11:10 waterfall
            ]
            
            # Portrait photos: time_person_name.png (4 images, including 1 duplicate)
            portrait_photos = [
                f'0930_{friend_names[0]}_and_{friend_names[1]}.png',  # 09:30 group photo of two people
                f'1200_selfie.png',                                    # 12:00 selfie
                f'1200_selfie_dup.png',                                # 12:00 selfie (duplicate)
                f'1430_lunch.png',                                     # 14:30 lunch photo
            ]
            
            all_photos = scenery_photos + portrait_photos
            
            # Create empty PNG files (simulate photos)
            for photo_name in all_photos:
                photo_path = os.path.join(pictures_path, photo_name)
                
                # Use dd to create small test files
                adb_utils.issue_generic_request([
                    'shell', 'dd', 'if=/dev/zero', f'of={photo_path}',
                    'bs=1024', 'count=1'
                ], env.controller)
                
                logging.info(f"      📸 Created: {photo_name}")
            
            time.sleep(1.0)
            logging.info(f"   ✅ W7-08 photo file preparation complete ({len(all_photos)} files)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  W7-08 photo file preparation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    # ==================== 🆕 Runtime initialization method ====================
    
    def _initialize_today_track_for_w7_07(self, env):
        """
        🆕 W7-07 Runtime initialization: fully reuse scenario_e's _initialize_today_track
        
        1. Close OpenTracks (stop any ongoing recording)
        2. Clean all tracks in the database (delete invalid data recorded in previous tasks)
        3. Add today's track data + re-add this week's historical data
        """
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime, timedelta
        import time
        import random
        
        try:
            # 1. Close the OpenTracks app (stop any ongoing recording)
            logging.info("      Step 1: stop OpenTracks and close the app...")
            adb_utils.close_app("activity tracker", env.controller)
            time.sleep(1.0)
            
            # 2. Clean all tracks in the database (delete invalid data recorded in previous tasks)
            logging.info("      Step 2: cleanup existing tracks (including invalid today's recorded tracks)...")
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ Cleared existing tracks")
            except Exception as e:
                logging.debug(f"      Clear failed: {e}")
            
            # 3. Add today's track data + re-add this week's historical data
            logging.info("      Step 3: add today's track data...")
            
            # Get the date for Day 7 (Sunday)
            day7_config = self.days.get(6)  # Day 7 (index6)
            if not day7_config:
                logging.warning("      ⚠️ Day 7 config not found")
                return
            
            base_date = day7_config.date
            if isinstance(base_date, str):
                base_date = datetime.fromisoformat(base_date)
            
            # ========== Today's track (W7-07 hiking)==========
            today_distance_m = 8500  # 8.5 km
            today_duration_ms = 150 * 60 * 1000  # 2.5 hours = 150 min
            today_start = base_date.replace(hour=9, minute=30)  # 9:30 AM start
            today_stop_ts = int(today_start.timestamp() * 1000) + today_duration_ms
            
            today_activity = sqlite_schema_utils.SportsActivity(
                name="Today's Hiking",
                category="hiking",
                activity_type="hiking",
                description="Morning hiking to West Peak",
                totaldistance=today_distance_m,
                starttime=int(today_start.timestamp() * 1000),
                stoptime=today_stop_ts,
                totaltime=today_duration_ms,
                movingtime=int(today_duration_ms * 0.85),  # 85% move time
                avgspeed=today_distance_m / (today_duration_ms / 1000),
                avgmovingspeed=today_distance_m / (today_duration_ms * 0.85 / 1000),
                elevationgain=320,
                elevationloss=180,
            )
            
            activities = [today_activity]
            logging.warning(f"         🔵 TODAY: {today_distance_m/1000:.1f}km, {today_duration_ms/60000:.0f}min")
            
            # ========== Re-add this week's historical data (from _setup_opentracks_weekly)==========
            random.seed(2026)  # Fix seed to ensure reproducibility
            
            weekly_data = [
                # (day_offset, distance_km, duration_min, hour, minute, name_suffix)
                (1, 4.2, 52, 17, 15, "Evening Trail"),        # Saturday
                (2, 6.8, 85, 7, 30, "Morning Hike"),          # Friday  
                (3, 3.5, 45, 18, 0, "Sunset Walk"),           # Thursday
                (4, 5.1, 62, 16, 45, "Afternoon Trek"),       # Wednesday
                (5, 7.3, 95, 6, 15, "Dawn Adventure"),        # Tuesday
            ]
            
            for day_offset, distance_km, duration_min, hour, minute, name_suffix in weekly_data:
                activity_date = base_date - timedelta(days=day_offset)
                
                distance_m = int(distance_km * 1000)
                duration_ms = duration_min * 60 * 1000
                
                start_ts = int(activity_date.replace(hour=hour, minute=minute).timestamp() * 1000)
                stop_ts = start_ts + duration_ms
                
                elevation_gain = random.randint(30, 180)
                elevation_loss = random.randint(20, 120)
                moving_ratio = 0.8 + random.random() * 0.15
                
                activity = sqlite_schema_utils.SportsActivity(
                    name=name_suffix,
                    category="hiking",
                    activity_type="hiking",
                    description="Hiking session",
                    totaldistance=distance_m,
                    starttime=start_ts,
                    stoptime=stop_ts,
                    totaltime=duration_ms,
                    movingtime=int(duration_ms * moving_ratio),
                    avgspeed=distance_m / (duration_ms / 1000),
                    avgmovingspeed=distance_m / (duration_ms * moving_ratio / 1000),
                    elevationgain=elevation_gain,
                    elevationloss=elevation_loss,
                )
                activities.append(activity)
                logging.info(f"         📊 Day -{day_offset}: {distance_km}km, {duration_min}min ({name_suffix})")
            
            # Add to database
            activity_app_utils._add_activities(activities, env)
            
            # Calculate totals
            total_distance_km = sum(a.totaldistance for a in activities) / 1000
            total_duration_min = sum(a.totaltime for a in activities) / (60 * 1000)
            
            logging.warning(f"      ✅ exercise data prepared ({len(activities)} records, including today's)")
            logging.warning(f"         📈 WEEKLY TOTAL: {total_distance_km:.1f}km, {total_duration_min:.0f}min")
            
        except Exception as e:
            logging.warning(f"   ⚠️ W7-07 initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    # ==================== ⚡ Reset mode: standalone initialization entry point ====================

    def _reset_initialize_subtask(self, subtask_idx: int, env):
        """
        Single-task independent scheduler initialization in Reset mode
        Dispatch to the corresponding _reset_init_WX_YY method based on task_id
        """
        from scendroid.env import adb_utils
        import time as _time

        subtask = self.seven_day_subtasks[subtask_idx]
        task_id = subtask.task_id
        params = self.generated_params
        logging.info(f"   🔧 Per-task reset initialization: {task_id} ({subtask.evaluator_name})")

        # Ensure timezone is UTC
        try:
            adb_utils.set_root_if_needed(env.controller)
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'], env.controller)
        except Exception:
            pass

        # ============ Day 1 ============
        if task_id == "W1-01":
            self._reset_init_w1_01_clock_alarm(subtask, env)
        elif task_id == "W1-02":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W1-03":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W1-04":
            self._reset_init_sms_contacts(subtask, env)
        elif task_id == "W1-05":
            self._reset_init_markor_only(subtask, env)
        elif task_id == "W1-06":
            self._reset_init_markor_only(subtask, env)
        elif task_id == "W1-07":
            self._reset_init_shopping(subtask, env)
        elif task_id == "W1-08":
            self._reset_init_expense_clear(subtask, env)
        elif task_id == "W1-09":
            self._reset_init_w1_09_sms_progress(subtask, env)
        elif task_id == "W1-10":
            self._reset_init_w1_10_markor_worklog(subtask, env)
        # ============ Day 2 ============
        elif task_id == "W2-01":
            self._reset_init_w2_01_clock_calendar(subtask, env)
        elif task_id == "W2-02":
            self._reset_init_audio_clean(subtask, env)
        elif task_id == "W2-03":
            self._reset_init_w2_03_breakfast_receipt(subtask, env)
        elif task_id == "W2-04":
            self._reset_init_audio_clean(subtask, env)
        elif task_id == "W2-05":
            self._reset_init_w2_05_calendar_seminar(subtask, env)
        elif task_id == "W2-06":
            self._reset_init_shopping(subtask, env)
        elif task_id == "W2-07":
            self._reset_init_w2_07_music_tracks(subtask, env)
        elif task_id == "W2-08":
            self._reset_init_w2_08_sms_progress(subtask, env)
        elif task_id == "W2-09":
            self._reset_init_w2_09_markor_schedule(subtask, env)
        elif task_id == "W2-10":
            self._reset_init_w2_10_markor_append(subtask, env)
        elif task_id == "W2-11":
            self._reset_init_w1_09_sms_progress(subtask, env)  # Reuse W1-09
        # ============ Day 3 ============
        elif task_id == "W3-01":
            self._reset_init_w3_01_worldclock_trip_image(subtask, env)
        elif task_id == "W3-02":
            self._reset_init_w3_02_meeting_conflict(subtask, env)
        elif task_id == "W3-03":
            self._reset_init_tasks_clear(subtask, env)
        elif task_id == "W3-04":
            self._reset_init_home_only(subtask, env)
        elif task_id == "W3-05":
            self._reset_init_shopping(subtask, env)
        elif task_id == "W3-06":
            self._reset_init_contacts_clear(subtask, env)
        elif task_id == "W3-07":
            self._reset_init_sms_contacts(subtask, env)
        elif task_id == "W3-08":
            self._reset_init_audio_clean(subtask, env)
        elif task_id == "W3-09":
            self._reset_init_w3_09_dinner_receipt(subtask, env)
        elif task_id == "W3-10":
            self._reset_init_expense_clear(subtask, env)
        elif task_id == "W3-11":
            self._reset_init_expense_with_history(subtask, env)
        # ============ Day 4 ============
        elif task_id == "W4-01":
            self._reset_init_expense_with_history(subtask, env)
        elif task_id == "W4-02":
            self._reset_init_w4_02_worklog_append(subtask, env)
        elif task_id == "W4-03":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W4-04":
            self._reset_init_w4_04_team_discussion(subtask, env)
        elif task_id == "W4-05":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W4-06":
            self._reset_init_w4_06_return_flight_image(subtask, env)
        elif task_id == "W4-07":
            self._reset_init_sms_contacts(subtask, env)
        # ============ Day 5 ============
        elif task_id == "W5-01":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W5-02":
            self._reset_init_sms_contacts(subtask, env)
        elif task_id == "W5-03":
            self._reset_init_w5_03_sms_meetingb(subtask, env)
        elif task_id == "W5-04":
            self._reset_init_home_only(subtask, env)
        elif task_id == "W5-05":
            self._reset_init_expense_with_history(subtask, env)
        elif task_id == "W5-06":
            self._reset_init_w1_01_clock_alarm(subtask, env)
        elif task_id == "W5-07":
            self._reset_init_w5_07_sms_meetinga_final(subtask, env)
        elif task_id == "W5-08":
            self._reset_init_home_only(subtask, env)
        # ============ Day 6 ============
        elif task_id == "W6-01":
            self._reset_init_w1_01_clock_alarm(subtask, env)
        elif task_id == "W6-02":
            self._reset_init_broccoli(subtask, env)
        elif task_id == "W6-03":
            self._reset_init_broccoli(subtask, env)
        elif task_id == "W6-04":
            self._reset_init_home_only(subtask, env)
        elif task_id == "W6-05":
            self._reset_init_camera_clean(subtask, env)
        elif task_id == "W6-06":
            self._reset_init_sms_contacts(subtask, env)
        elif task_id == "W6-07":
            self._reset_init_shopping(subtask, env)
        elif task_id == "W6-08":
            self._reset_init_home_only(subtask, env)
        elif task_id == "W6-09":
            self._reset_init_w6_09_opentracks_walk(subtask, env)
        elif task_id == "W6-10":
            self._reset_init_sms_contacts(subtask, env)
        elif task_id == "W6-11":
            self._reset_init_w6_11_markor_rename(subtask, env)
        # ============ Day 7 ============
        elif task_id == "W7-01":
            self._reset_init_w7_01_picnic_recipe(subtask, env)
        elif task_id == "W7-02":
            self._reset_init_w7_02_picnic_location(subtask, env)
        elif task_id == "W7-03":
            self._reset_init_retromusic_clean(subtask, env)
        elif task_id == "W7-04":
            self._reset_init_w7_04_tracks_music(subtask, env)
        elif task_id == "W7-05":
            self._reset_init_camera_clean(subtask, env)
        elif task_id == "W7-06":
            self._reset_init_shopping(subtask, env)
        elif task_id == "W7-07":
            self._reset_init_w7_07_opentracks_weekly(subtask, env)
        elif task_id == "W7-08":
            self._reset_init_w7_08_photos(subtask, env)
        elif task_id == "W7-09":
            self._reset_init_expense_with_history(subtask, env)
        elif task_id == "W7-10":
            self._reset_init_w7_10_sms_meetingb(subtask, env)
        elif task_id == "W7-11":
            self._reset_init_calendar_only(subtask, env)
        elif task_id == "W7-12":
            self._reset_init_w7_12_sms_all_week(subtask, env)
        else:
            logging.warning(f"   ⚠️  No custom reset init for {task_id}, using evaluator default")
            try:
                subtask.evaluator_instance.initialize_task(env)
            except Exception as e:
                logging.warning(f"   ⚠️  Fallback initialize_task failed: {e}")
            self._reset_press_home(env)

    # ==================== ⚡ Reset initialization utility methods ====================

    def _reset_press_home(self, env):
        """return to home screen"""
        from scendroid.env import adb_utils
        import time as _time
        try:
            adb_utils.press_home_button(env.controller)
            _time.sleep(1.0)
        except Exception:
            pass

    def _reset_ensure_utc(self, env):
        """Ensure timezone is UTC"""
        from scendroid.env import adb_utils
        try:
            adb_utils.set_root_if_needed(env.controller)
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'], env.controller)
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'], env.controller)
        except Exception:
            pass

    def _reset_init_home_only(self, subtask, env):
        """Return only to the home screen (tasks requiring no special initialization)"""
        self._reset_press_home(env)

    def _reset_init_shopping(self, subtask, env):
        """Shopping task initialization: call evaluator.initialize_task() + remain on the Shopping homepage"""
        import time as _time
        try:
            evaluator = subtask.evaluator_instance
            logging.info("      🛒 Initializing Shopping evaluator (Chrome + WebArena login)...")
            evaluator.initialize_task(env)
            logging.info("      ✅ Shopping evaluator initialized (on Shopping homepage)")
        except Exception as e:
            logging.warning(f"      ⚠️  Shopping evaluator init failed: {e}")

    def _reset_init_calendar_only(self, subtask, env):
        """Tasks requiring only that a calendar event exists"""
        try:
            self._setup_calendar_events(env)
            logging.info("      ✅ Calendar events ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Calendar setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_sms_contacts(self, subtask, env):
        """SMS tasks requiring contacts"""
        try:
            self._setup_contacts(env)
            logging.info("      ✅ Contacts ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Contacts setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_contacts_clear(self, subtask, env):
        """Tasks requiring clearing contacts (W3-06: create new contact task)"""
        from scendroid.env import adb_utils
        try:
            # Clear contact data to ensure a clean status
            adb_utils.clear_app_data('contacts', env.controller)
            import time as _time
            _time.sleep(1.0)
            logging.info("      ✅ Contacts app data cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Contacts clear failed: {e}")
        self._reset_press_home(env)

    def _reset_init_markor_only(self, subtask, env):
        """Tasks requiring clearing Markor"""
        from scendroid.env import adb_utils
        try:
            from scendroid.task_evals.single import markor
            markor.clear_markor_files(env.controller)
            logging.info("      ✅ Markor cleared")
        except Exception as e:
            try:
                adb_utils.clear_app_data('markor', env.controller)
                logging.info("      ✅ Markor data cleared (fallback)")
            except Exception as e2:
                logging.warning(f"      ⚠️  Markor clear failed: {e2}")
        self._reset_press_home(env)

    def _reset_init_audio_clean(self, subtask, env):
        """Tasks requiring clearing audio recordings"""
        try:
            self._cleanup_audiorecorder(env)
            logging.info("      ✅ Audio recorder cleaned")
        except Exception as e:
            logging.warning(f"      ⚠️  Audio clean failed: {e}")
        self._reset_press_home(env)

    def _reset_init_expense_clear(self, subtask, env):
        """Tasks requiring clearing expense data"""
        from scendroid.env import adb_utils
        try:
            adb_utils.clear_app_data('pro expense', env.controller)
            import time as _time
            _time.sleep(1.0)
            logging.info("      ✅ Expense data cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Expense clear failed: {e}")
        self._reset_press_home(env)

    def _reset_init_expense_with_history(self, subtask, env):
        """Tasks requiring historical expense data"""
        try:
            self._setup_expense(env)
            logging.info("      ✅ Expense history ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Expense setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_broccoli(self, subtask, env):
        """Tasks requiring the Broccoli recipe"""
        try:
            self._setup_broccoli_recipes(env)
            logging.info("      ✅ Broccoli recipes ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Broccoli setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_camera_clean(self, subtask, env):
        """Tasks requiring clearing camera files"""
        try:
            self._cleanup_camera_files(env)
            logging.info("      ✅ Camera files cleaned")
        except Exception as e:
            logging.warning(f"      ⚠️  Camera clean failed: {e}")
        self._reset_press_home(env)

    def _reset_init_retromusic_clean(self, subtask, env):
        """Tasks requiring clearing the RetroMusic playlist"""
        try:
            from scendroid.task_evals.single import retro_music
            retro_music._clear_playlist_dbs(env)
            logging.info("      ✅ RetroMusic playlists cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  RetroMusic clear failed: {e}")
        self._reset_press_home(env)

    def _reset_init_tasks_clear(self, subtask, env):
        """Tasks requiring clearing Tasks"""
        try:
            self._cleanup_tasks(env)
            logging.info("      ✅ Tasks cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Tasks clear failed: {e}")
        self._reset_press_home(env)

    # ============ Day 1 personalized initialization ============

    def _reset_init_w1_01_clock_alarm(self, subtask, env):
        """W1-01 / W5-06 / W6-01: Ensure initial alarm exists"""
        try:
            self._setup_clocks(env)
            logging.info("      ✅ Clocks/alarms ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Clock setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w1_09_sms_progress(self, subtask, env):
        """W1-09 / W2-11: SMS progress replies (responses from Meeting A attendees)"""
        try:
            self._setup_contacts(env)
            self._setup_sms_for_w1_09(env)
            logging.info("      ✅ SMS replies for Meeting A progress ready")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w1_10_markor_worklog(self, subtask, env):
        """W1-10: WorkLog.md already exists (containing a meeting minutes template), for the agent to append an evening summary"""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.env import device_constants
            import tempfile, os
            # First close Markor to avoid file locks
            try:
                adb_utils.close_app('markor', env.controller)
                _time.sleep(0.5)
            except Exception:
                pass
            # clear Markor
            try:
                from scendroid.task_evals.single import markor
                markor.clear_markor_files(env.controller)
            except Exception:
                adb_utils.clear_app_data('markor', env.controller)
            _time.sleep(0.5)
            params = self.generated_params
            meeting_a = params['meeting_a']
            # Create WorkLog.md: simulate the meeting minutes template created by W1-05
            # Includes sections Title/Time/Location/Attendees/Discussion, conforming to the output format of LayeredMarkorCreateOutline
            content = (
                f"# Work Log\n\n"
                f"## {meeting_a['title']}\n\n"
                f"**Time:** 9:00 AM\n"
                f"**Location:** {meeting_a['location']}\n"
                f"**Attendees:** {', '.join(meeting_a['attendees_full'])}\n\n"
                f"## Discussion\n\n"
                f"- Q4 planning and team updates discussed\n"
                f"- Action items assigned\n\n"
            )
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, prefix='WorkLog')
            tmp.write(content)
            tmp.close()
            from scendroid.utils import file_utils
            remote_path = f"{device_constants.MARKOR_DATA}/WorkLog.md"
            file_utils.copy_data_to_device(tmp.name, remote_path, env.controller)
            os.unlink(tmp.name)
            _time.sleep(0.5)
            logging.info("      ✅ WorkLog.md created for W1-10 append")
        except Exception as e:
            logging.warning(f"      ⚠️  WorkLog.md creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        self._reset_press_home(env)

    # ============ Day 2 personalized initialization ============

    def _reset_init_w2_01_clock_calendar(self, subtask, env):
        """W2-01: Clear alarms; ensure calendar has no seminar event on the current day (so the agent can create one)"""
        try:
            # Set up only the clock (do not pre-create the seminar event; let the agent create it)
            self._setup_clocks(env)
            logging.info("      ✅ Clocks ready (agent will create seminar event)")
        except Exception as e:
            logging.warning(f"      ⚠️  Clock setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w2_03_breakfast_receipt(self, subtask, env):
        """W2-03: Create breakfast receipt image"""
        try:
            self._create_breakfast_receipt(env)
            logging.info("      ✅ Breakfast receipt ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Breakfast receipt failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w2_05_calendar_seminar(self, subtask, env):
        """W2-05: Create seminar calendar event (9:00 AM), for the agent to modify"""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_schema_utils
            import calendar as cal_module
            from datetime import datetime

            params = self.generated_params
            seminar = params['seminar']

            # First close the calendar app to avoid WAL locking
            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass

            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)

            # seminar event:2026-01-20 (Day2=Tuesday)09:00 AM
            event_dt = datetime(2026, 1, 20, 9, 0, 0)
            start_ts = cal_module.timegm(event_dt.timetuple())
            end_ts = start_ts + 90 * 60  # 90minutes

            attendees_desc = "Attendees: " + ", ".join(seminar['attendees'])
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts,
                end_ts=end_ts,
                title=seminar['title'],
                description=attendees_desc,
                location=seminar['location'],
            )
            calendar_utils.add_events([event], env)
            _time.sleep(2.0)
            logging.info(f"      ✅ Seminar event created: '{seminar['title']}' at 9:00 on 2026-01-20")
        except Exception as e:
            logging.warning(f"      ⚠️  Seminar event creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())

        # Ensure contact exists (required for sending SMS)
        try:
            self._setup_contacts(env)
        except Exception:
            pass
        self._reset_press_home(env)

    def _reset_init_w2_07_music_tracks(self, subtask, env):
        """W2-07: clear RetroMusic and OpenTracks"""
        try:
            self._cleanup_retromusic(env)
            logging.info("      ✅ RetroMusic cleaned")
        except Exception as e:
            logging.warning(f"      ⚠️  RetroMusic clean failed: {e}")
        try:
            self._cleanup_opentracks(env)
            logging.info("      ✅ OpenTracks cleaned")
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks clean failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w2_08_sms_progress(self, subtask, env):
        """W2-08: Set up seminar discussion progress SMS (replies from Alice, Charlie, and Diana + distractors)"""
        try:
            self._setup_contacts(env)
            self._setup_sms_for_w2_08(env)
            logging.info("      ✅ SMS progress replies for W2-08 ready")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w2_09_markor_schedule(self, subtask, env):
        """W2-09: Ensure contact and calendar event exist (to extract seminar information into DailySchedule)"""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_schema_utils
            import calendar as cal_module
            from datetime import datetime

            params = self.generated_params
            seminar = params['seminar']

            # Create seminar event (already updated to 10:00)
            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass
            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)

            event_dt = datetime(2026, 1, 20, 10, 0, 0)  # Time already updated
            start_ts = cal_module.timegm(event_dt.timetuple())
            end_ts = start_ts + 90 * 60

            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts, end_ts=end_ts,
                title=seminar['title'], description="",
                location=seminar['location'],
            )
            calendar_utils.add_events([event], env)
            _time.sleep(1.0)

            # Create breakfast receipt image (for expenses)
            self._create_breakfast_receipt(env)

            # Clear Markor (so the agent can create it)
            try:
                from scendroid.task_evals.single import markor
                markor.clear_markor_files(env.controller)
            except Exception:
                adb_utils.clear_app_data('markor', env.controller)

            logging.info("      ✅ W2-09 init: seminar event + receipt + markor cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  W2-09 init failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w2_10_markor_append(self, subtask, env):
        """W2-10: DailySchedule.md already exists (containing seminar information), for the agent to append the audio recording file name
        
        Simulate the status after W2-09 (LayeredMarkorCreateOutline) completes correctly:
        DailySchedule.md contains the seminar schedule (time updated at 10:00) and breakfast expenses.
        The agent must append the audio recording filename 'Seminar_Tue' to this.
        """
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.env import device_constants
            import tempfile, os
            # First, close Markor to avoid file locks.
            try:
                adb_utils.close_app('markor', env.controller)
                _time.sleep(0.5)
            except Exception:
                pass
            # clear Markor file
            try:
                from scendroid.task_evals.single import markor
                markor.clear_markor_files(env.controller)
            except Exception:
                adb_utils.clear_app_data('markor', env.controller)
            _time.sleep(0.5)

            params = self.generated_params
            seminar = params['seminar']
            # Content format simulates the output of LayeredMarkorCreateOutline: includes all required_sections.
            content = (
                f"# DailySchedule - Tuesday 2026-01-20\n\n"
                f"## Schedule\n\n"
                f"- {seminar['title']}: 10:00 AM in {seminar['location']}\n\n"
                f"## Expenses\n\n"
                f"- Breakfast: $6.80\n\n"
            )
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, prefix='DailySchedule')
            tmp.write(content)
            tmp.close()
            from scendroid.utils import file_utils
            remote_path = f"{device_constants.MARKOR_DATA}/DailySchedule.md"
            file_utils.copy_data_to_device(tmp.name, remote_path, env.controller)
            os.unlink(tmp.name)
            _time.sleep(0.5)
            logging.info("      ✅ DailySchedule.md created for W2-10 append")
        except Exception as e:
            logging.warning(f"      ⚠️  DailySchedule.md creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        self._reset_press_home(env)

    # ============ Day 3 personalized initialization ============

    def _reset_init_w3_01_worldclock_trip_image(self, subtask, env):
        """W3-01: Create trip information image + clear Calendar
        
        Refer to the initialization method in scenario_d task1:
        1. Create a trip information PNG (including flight time: 9:30 AM).
        2. Clear the Calendar (to allow the agent to create a new 'Flight to SF' calendar event).
        3. return to home screen
        """
        import time as _time
        # 1. Create trip information image (_create_trip_info_image internally handles deletion of the old file).
        try:
            self._create_trip_info_image(env)
            logging.info("      ✅ Trip info image ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Trip info image failed: {e}")

        # 2. Clear the Calendar (to avoid residual old events interfering with the agent's creation of the 'Flight to SF' event).
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils

            # Close the calendar app to avoid WAL locking.
            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass

            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)
            logging.info("      ✅ Calendar cleared for W3-01")
        except Exception as e:
            logging.warning(f"      ⚠️  Calendar clear failed: {e}")

        self._reset_press_home(env)

    def _reset_init_w3_02_meeting_conflict(self, subtask, env):
        """W3-02: Create Morning Meeting (10:00) and Flight to SF (9:30) events, resulting in a conflict."""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_schema_utils
            import calendar as cal_module
            from datetime import datetime

            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass
            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)

            # Flight to SF at 9:30 (2026-01-21, Day3=Wednesday)
            flight_dt = datetime(2026, 1, 21, 9, 30, 0)
            flight_start = cal_module.timegm(flight_dt.timetuple())
            flight_end = flight_start + 3 * 3600  # 3hours
            flight_event = sqlite_schema_utils.CalendarEvent(
                start_ts=flight_start, end_ts=flight_end,
                title="Flight to SF", description="", location="Airport",
            )

            # Morning Meeting at 10:00 (conflicts with flight)
            meeting_dt = datetime(2026, 1, 21, 10, 0, 0)
            meeting_start = cal_module.timegm(meeting_dt.timetuple())
            meeting_end = meeting_start + 3600  # 1hours
            meeting_event = sqlite_schema_utils.CalendarEvent(
                start_ts=meeting_start, end_ts=meeting_end,
                title="Morning Meeting", description="", location="Conference Room",
            )

            calendar_utils.add_events([flight_event, meeting_event], env)
            _time.sleep(2.0)
            logging.info("      ✅ Flight to SF + Morning Meeting (conflict) events created")
        except Exception as e:
            logging.warning(f"      ⚠️  W3-02 event creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        self._reset_press_home(env)

    def _reset_init_w3_09_dinner_receipt(self, subtask, env):
        """W3-09: Create dinner receipt image."""
        try:
            self._create_dinner_receipt_photo(env)
            logging.info("      ✅ Dinner receipt ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Dinner receipt creation failed: {e}")
        self._reset_press_home(env)

    # ============ Day 4 personalized initialization ============

    def _reset_init_w4_02_worklog_append(self, subtask, env):
        """W4-02: WorkLog.md already exists (containing Day1 meeting notes and evening summary) + historical expense data, for the agent to append the most recent 3 days' expenses.
        
        Simulate the status after correctly completing W1-05 + W1-10:
        - WorkLog.md contains Day1 meeting notes (Title/Time/Location/Attendees/Discussion).
        - And the evening summary added by W1-10 (including 9 AM + expense amounts).
        The agent must append all expenses from the most recent 3 days (name + amount) to this.
        """
        import time as _time
        # 1. Set up historical expense data (for the agent to reference or directly use the details in the reset instruction).
        try:
            self._setup_expense(env)
            logging.info("      ✅ Expense history ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Expense setup failed: {e}")
        # 2. Create the WorkLog.md template (simulating the status after completing W1-05 + W1-10).
        try:
            from scendroid.env import adb_utils, device_constants
            import tempfile, os
            # First, close Markor to avoid file locks.
            try:
                adb_utils.close_app('markor', env.controller)
                _time.sleep(0.5)
            except Exception:
                pass
            try:
                from scendroid.task_evals.single import markor
                markor.clear_markor_files(env.controller)
            except Exception:
                adb_utils.clear_app_data('markor', env.controller)
            _time.sleep(0.5)
            params = self.generated_params
            meeting_a = params['meeting_a']
            product_table = params['products']['table']
            # Simulate the meeting notes outline created by W1-05 + the evening summary added by W1-10.
            content = (
                f"# Work Log\n\n"
                f"## {meeting_a['title']}\n\n"
                f"**Time:** 9:00 AM\n"
                f"**Location:** {meeting_a['location']}\n"
                f"**Attendees:** {', '.join(meeting_a['attendees_full'])}\n\n"
                f"## Discussion\n\n"
                f"- Q4 planning and team updates discussed\n"
                f"- Action items assigned\n\n"
                f"## Daily Summary (Monday)\n\n"
                f"Had the {meeting_a['title']} meeting at 9am in {meeting_a['location']}. "
                f"Today's expense: ${product_table['price']:.2f} (table purchase).\n\n"
                f"## Expenses (Last 3 Days)\n\n"
            )
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, prefix='WorkLog')
            tmp.write(content)
            tmp.close()
            from scendroid.utils import file_utils
            remote_path = f"{device_constants.MARKOR_DATA}/WorkLog.md"
            file_utils.copy_data_to_device(tmp.name, remote_path, env.controller)
            os.unlink(tmp.name)
            _time.sleep(0.5)
            logging.info("      ✅ WorkLog.md created for W4-02")
        except Exception as e:
            logging.warning(f"      ⚠️  WorkLog.md creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        self._reset_press_home(env)

    def _reset_init_w4_04_team_discussion(self, subtask, env):
        """W4-04: create Team Discussion (18:00) and Keynote Speech (14:00) event"""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_schema_utils
            import calendar as cal_module
            from datetime import datetime

            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass
            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)

            # Keynote Speech at 14:00 (2026-01-22, Day4=Thursday)
            keynote_dt = datetime(2026, 1, 22, 14, 0, 0)
            keynote_start = cal_module.timegm(keynote_dt.timetuple())
            keynote_end = keynote_start + 2 * 3600
            keynote_event = sqlite_schema_utils.CalendarEvent(
                start_ts=keynote_start, end_ts=keynote_end,
                title="Keynote Speech", description="", location="Main Hall",
            )

            # Team Discussion at 18:00 (conflicts with exercise 18:00-18:30)
            discussion_dt = datetime(2026, 1, 22, 18, 0, 0)
            discussion_start = cal_module.timegm(discussion_dt.timetuple())
            discussion_end = discussion_start + 3600
            discussion_event = sqlite_schema_utils.CalendarEvent(
                start_ts=discussion_start, end_ts=discussion_end,
                title="Team Discussion", description="", location="Meeting Room",
            )

            calendar_utils.add_events([keynote_event, discussion_event], env)
            _time.sleep(2.0)
            logging.info("      ✅ Keynote Speech + Team Discussion (conflict) events created")
        except Exception as e:
            logging.warning(f"      ⚠️  W4-04 event creation failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w4_06_return_flight_image(self, subtask, env):
        """W4-06: Create return flight information image."""
        try:
            self._create_return_flight_image(env)
            logging.info("      ✅ Return flight image ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Return flight image failed: {e}")
        self._reset_press_home(env)

    # ============ Day 5 personalized initialization ============

    def _reset_init_w5_03_sms_meetingb(self, subtask, env):
        """W5-03: Send SMS reply confirming Meeting B."""
        try:
            self._setup_contacts(env)
            self._setup_sms_for_w5_03(env)
            logging.info("      ✅ Meeting B confirmation SMS ready")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w5_07_sms_meetinga_final(self, subtask, env):
        """W5-07: Final status SMS for Meeting A."""
        try:
            self._setup_contacts(env)
            self._setup_sms_for_w5_07(env)
            logging.info("      ✅ Meeting A final SMS ready")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS setup failed: {e}")
        self._reset_press_home(env)

    # ============ Day 6 personalized initialization ============

    def _reset_init_w6_09_opentracks_walk(self, subtask, env):
        """W6-09: Create Saturday walking route data."""
        try:
            self._setup_opentracks_saturday(env)
            logging.info("      ✅ Saturday walk track data ready")
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks saturday setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w6_11_markor_rename(self, subtask, env):
        """W6-11: Create SaturdayBreakfast.md (for the agent to rename as weekendsummary.md and append a summary).
        
        Simulate a breakfast note file previously created by the user; the agent must:
        1. Rename SaturdayBreakfast.md to weekendsummary.md.
        2. Append a summary of today's shopping (Egg Organic $11.80) and walking (Bob Johnson, 2.5 km).
        """
        import time as _time
        try:
            from scendroid.env import adb_utils, device_constants
            import tempfile, os
            # First, close Markor to avoid file locks.
            try:
                adb_utils.close_app('markor', env.controller)
                _time.sleep(0.5)
            except Exception:
                pass
            # clear Markor file
            try:
                from scendroid.task_evals.single import markor
                markor.clear_markor_files(env.controller)
            except Exception:
                adb_utils.clear_app_data('markor', env.controller)
            _time.sleep(0.5)
            content = (
                "# Saturday Breakfast - Scrambled Eggs with Toast\n\n"
                "## Recipe: Scrambled Eggs with Toast\n"
                "**Prep Time:** 10 minutes\n\n"
                "## Ingredients\n"
                "- 3 eggs\n"
                "- 1 tbsp butter\n"
                "- Salt to taste\n"
                "- 2 slices bread\n\n"
                "## Steps\n"
                "1. Crack eggs into bowl and whisk\n"
                "2. Melt butter in pan over medium heat\n"
                "3. Pour eggs into pan and stir gently\n"
                "4. Toast bread\n"
                "5. Serve together\n"
            )
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, prefix='SaturdayBreakfast')
            tmp.write(content)
            tmp.close()
            from scendroid.utils import file_utils
            remote_path = f"{device_constants.MARKOR_DATA}/SaturdayBreakfast.md"
            file_utils.copy_data_to_device(tmp.name, remote_path, env.controller)
            os.unlink(tmp.name)
            _time.sleep(0.5)
            logging.info("      ✅ SaturdayBreakfast.md created for W6-11")
        except Exception as e:
            logging.warning(f"      ⚠️  SaturdayBreakfast.md creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        self._reset_press_home(env)

    # ============ Day 7 personalized initialization ============

    def _reset_init_w7_01_picnic_recipe(self, subtask, env):
        """W7-01: Broccoli recipe + clear Tasks"""
        try:
            self._setup_broccoli_recipes(env)
            self._cleanup_tasks(env)
            logging.info("      ✅ Broccoli recipes + Tasks cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  W7-01 init failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w7_02_picnic_location(self, subtask, env):
        """W7-02: Create Mountain Picnic calendar event (East Valley Trail), for the agent to modify the location."""
        import time as _time
        try:
            from scendroid.env import adb_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_schema_utils
            import calendar as cal_module
            from datetime import datetime

            try:
                adb_utils.close_app('simple calendar pro', env.controller)
                _time.sleep(1.0)
            except Exception:
                pass
            calendar_utils.clear_calendar_db(env)
            _time.sleep(1.0)

            # Mountain Picnic at 10:00 (2026-01-25, Day7=Sunday)
            event_dt = datetime(2026, 1, 25, 10, 0, 0)
            start_ts = cal_module.timegm(event_dt.timetuple())
            end_ts = start_ts + 3 * 3600

            attendees = ["Alice Davis", "Charlie Brown", "Diana Prince", "Frank Castle"]
            attendees_desc = "Attendees: " + ", ".join(attendees)
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts, end_ts=end_ts,
                title="Mountain Picnic",
                description=attendees_desc,
                location="East Valley Trail",
            )
            calendar_utils.add_events([event], env)
            _time.sleep(2.0)
            logging.info("      ✅ Mountain Picnic event created (East Valley Trail)")

            # Ensure the attendee contact exists.
            self._setup_contacts(env)
        except Exception as e:
            logging.warning(f"      ⚠️  W7-02 init failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w7_04_tracks_music(self, subtask, env):
        """W7-04: Clear OpenTracks + prepare music file + pre-create Mountain Hike playlist."""
        import time as _time
        try:
            self._cleanup_retromusic(env)
            self._cleanup_opentracks(env)
            logging.info("      ✅ RetroMusic + OpenTracks cleaned")
        except Exception as e:
            logging.warning(f"      ⚠️  Cleanup failed: {e}")
        # The reset_user_instruction for W7-04 includes the step to create the playlist, so it is not pre-created here.
        self._reset_press_home(env)

    def _reset_init_w7_07_opentracks_weekly(self, subtask, env):
        """W7-07: Prepare weekly exercise route data."""
        try:
            self._setup_opentracks_weekly(env)
            self._initialize_today_track_for_w7_07(env)
            logging.info("      ✅ OpenTracks weekly + today data ready")
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks weekly setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w7_08_photos(self, subtask, env):
        """W7-08: Prepare photo files for classification and deduplication."""
        try:
            self._setup_photos_for_w7_08(env)
            logging.info("      ✅ Photos for W7-08 ready")
        except Exception as e:
            logging.warning(f"      ⚠️  Photos setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w7_10_sms_meetingb(self, subtask, env):
        """W7-10: Final confirmation SMS for Meeting B."""
        try:
            self._setup_contacts(env)
            self._setup_sms_for_w7_10(env)
            logging.info("      ✅ Meeting B final SMS ready")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS setup failed: {e}")
        self._reset_press_home(env)

    def _reset_init_w7_12_sms_all_week(self, subtask, env):
        """W7-12: Ensure contact exists (for SMS statistics)."""
        try:
            self._setup_contacts(env)
            # Set up all SMS for W1-09, W2-08, W5-03, W5-07, and W7-10.
            self._setup_sms_for_w1_09(env)
            self._setup_sms_for_w2_08(env)
            self._setup_sms_for_w5_03(env)
            self._setup_sms_for_w5_07(env)
            self._setup_sms_for_w7_10(env)
            logging.info("      ✅ All week SMS ready for W7-12 stats")
        except Exception as e:
            logging.warning(f"      ⚠️  W7-12 SMS setup failed: {e}")
        self._reset_press_home(env)

    def tear_down(self, env):
        """
        Cleanup work after the 7-day scenario ends
        
        Important: 
        - The shopping container is rebuilt only once, after the final day (Day 7) of the 7-day scenario ends.
        - The container is not rebuilt every day; it is rebuilt only after the 7-day scenario ends.
        - This is because the scenario contains multiple shopping tasks (e.g., W1-07, W2-06, W3-05, etc.).
        """
        logging.info("=" * 70)
        logging.info("🧹 Scenario OmniLife (7-Day) - Cleanup")
        logging.info("=" * 70)
        
        try:
            # Rebuild the Shopping container (restore initial status after the 7-day scenario ends)
            logging.info("   🛒 rebuild Shopping container(7daysscenarioend)...")
            try:
                from scendroid.task_evals.webarena import container_manager
                
                # extract console_port to ensure correct container rebuild
                # emulator-5554 → shopping (7770)
                # emulator-5556 → shopping_5556 (7772)
                # emulator-5558 → shopping_5558 (7774)
                console_port = None
                try:
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    logging.info(f"      📱 Emulator console port: {console_port}")
                except Exception as e:
                    logging.warning(f"      ⚠️  Could not extract console_port: {e}")
                
                manager = container_manager.ShoppingContainerManager(console_port=console_port)
                success = manager.rebuild_container()
                
                if success:
                    logging.info(f"      ✅ Shopping container rebuilt")
                    logging.info(f"         Container: {manager.docker_container}")
                    logging.info(f"         Port: {manager.host_port}")
                else:
                    logging.warning(f"      ⚠️  Failed to rebuild the Shopping container")
            except Exception as e:
                logging.warning(f"      ⚠️  Shopping container rebuild failed: {e}")
                import traceback
                logging.warning(traceback.format_exc())
        
        except Exception as e:
            logging.warning(f"   ⚠️  An error occurred during cleanup: {e}")
        
        # Call the parent class's tear_down (which cleans up all subtasks)
        super().tear_down(env)
        
        logging.info("✅ Scenario OmniLife (7-Day) cleanup complete")
    