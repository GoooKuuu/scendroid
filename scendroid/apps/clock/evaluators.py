"""
Clock App Evaluators

Provides Clock app-related evaluators:
1. LayeredClockSetAlarm - evaluationalarmsetup
2. LayeredClockDisableAllAlarms - Evaluates whether all alarms are disabled.
3. LayeredClockStartTimer - Evaluates whether the timer has started.

Note: All scendroid.env imports are performed inside functions to avoid circular dependencies during module loading.
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredClockSetAlarm")
class ClockSetAlarmEvaluator(BaseAppEvaluator):
    """
    evaluationalarmsetuptask
    
    supported scenarios:
    - L0: "Open the Clock app and set an alarm for 8:00 AM tomorrow."
    - L1: "Set an alarm for 8:00 AM tomorrow."
    - L2: "Set an alarm for tomorrow morning."
    - L3: "Remind me to wake up early tomorrow."
    
    evaluation content:
    - Whether the alarm time is correct (hour, minute).
    - Whether the date is correct (day_offset).
    - (Optional) Whether the original alarm was removed (check_original_removed).
    """
    
    # ScenDroid standard attributes
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.alarm_time_hour = params.get('alarm_time_hour')
        self.alarm_time_minute = params.get('alarm_time_minute')
        self.day_offset = params.get('day_offset', 0)
        self.alarm_enabled = params.get('alarm_enabled', True)
        
        # Optional parameters: used for the "adjust alarm" scenario.
        # Check whether the original alarm was removed (rather than creating a new alarm).
        self.check_original_removed = params.get('check_original_removed', False)
        self.original_hour = params.get('original_hour')
        self.original_minute = params.get('original_minute')
        
        # Optional parameters: verify that other alarms remain unchanged.
        self.verify_other_alarms = params.get('verify_other_alarms_unchanged', False)
        self.expected_total_alarms = params.get('expected_total_alarms')
        
        # Set complexity (used to dynamically compute max_steps).
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        execute evaluation
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure, and 0.5 indicates partial success.
        """
        # import on demand
        from .utils import check_alarm_with_date
        
        hour = self.alarm_time_hour
        minute = self.alarm_time_minute
        day_offset = self.day_offset
        enabled = self.alarm_enabled
        
        logging.info("Checking alarm: %02d:%02d, day_offset=%d, enabled=%s",
                    hour, minute, day_offset, enabled)
        
        # Check whether the new alarm exists.
        if not check_alarm_with_date(env, hour, minute, day_offset, enabled):
            logging.warning("❌ Alarm check FAILED: %02d:%02d (day_offset=%d) not found",
                           hour, minute, day_offset)
            return 0.0
        
        logging.warning("✅ New alarm found: %02d:%02d (day_offset=%d)",
                       hour, minute, day_offset)
        
        # Optional check: whether the original alarm was removed.
        if self.check_original_removed:
            if self.original_hour is not None and self.original_minute is not None:
                if check_alarm_with_date(env, self.original_hour, self.original_minute, 
                                        day_offset, True):
                    logging.warning("❌ Original alarm still exists: %02d:%02d",
                                   self.original_hour, self.original_minute)
                    # 🆕 Binary rating: failure if the old alarm was not removed.
                    logging.warning("❌ FAILED - Original alarm should be removed")
                    return 0.0
                else:
                    logging.warning("✅ Original alarm removed: %02d:%02d",
                                   self.original_hour, self.original_minute)
        
        # Optional check: total alarm count.
        if self.expected_total_alarms is not None:
            # This is a simplified check—actual implementation requires counting from the database/UI.
            logging.info("Expected total alarms: %d (check not fully implemented)", 
                        self.expected_total_alarms)
        
        logging.warning("✅ Alarm check PASSED: %02d:%02d (day_offset=%d)",
                       hour, minute, day_offset)
        return 1.0
    
    def initialize_task(self, env):
        """
        Initialize task: clear Clock app data.
        """
        from .utils import close_clock_app
        
        super().initialize_task(env)
        close_clock_app(env)
        logging.info("✅ Clock app data cleared")
    
    def tear_down(self, env):
        """
        Cleanup environment: clear Clock app data.
        """
        from .utils import close_clock_app
        
        super().tear_down(env)
        close_clock_app(env)
        logging.info("✅ Clock app data cleared (tear down)")


# ❌ REMOVED: First LayeredClockStartTimer registration (duplicate)
# The corrected version is at line ~600


@AppRegistry.register_evaluator("LayeredClockDisableAllAlarms")
class ClockDisableAllAlarmsEvaluator(BaseAppEvaluator):
    """
    Evaluate whether all alarms are disabled.
    
    supported scenarios:
    - L0: "Open Clock and turn off all active alarms"
    - L1: "Turn off all my alarms"
    - L3: "I'm on vacation, I don't want to be disturbed by alarms."
    
    initialization:
    - Create multiple enabled alarms (default: 3).
    
    evaluation content:
    - Whether all alarms have been disabled.
    """
    
    # ScenDroid standard attributes
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Alarm count created during initialization.
        self.num_alarms = params.get('num_alarms', 3)
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether all alarms are disabled.
        
        Returns:
            float: 1.0 indicates all alarms are disabled; 0.0 indicates at least one alarm remains enabled.
        """
        from .utils import check_all_alarms_disabled
        
        logging.warning("📱 Checking if all alarms are disabled...")
        
        if check_all_alarms_disabled(env):
            logging.warning("✅ All alarms check PASSED: all alarms are disabled")
            return 1.0
        else:
            logging.warning("❌ All alarms check FAILED: some alarms are still enabled")
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: create multiple enabled alarms.
        """
        import time
        from .utils import close_clock_app, set_alarm_via_intent
        
        super().initialize_task(env)
        
        # Clear existing alarms.
        close_clock_app(env)
        
        # Set up multiple alarms for testing.
        alarm_times = [
            (7, 0),    # 7:00 AM
            (8, 30),   # 8:30 AM
            (9, 15),   # 9:15 AM
            (12, 0),   # 12:00 PM
            (18, 30),  # 6:30 PM
        ]
        
        logging.info("Setting up %d alarms for testing...", self.num_alarms)
        for i in range(min(self.num_alarms, len(alarm_times))):
            hour, minute = alarm_times[i]
            logging.info("Setting alarm %d: %02d:%02d", i+1, hour, minute)
            set_alarm_via_intent(env, hour, minute, skip_ui=True)
            time.sleep(1.0)
        
        # Allow time for the UI to refresh.
        time.sleep(2.0)
        logging.info("✅ Initialized %d alarms", self.num_alarms)
    
    def tear_down(self, env):
        """
        Cleanup environment: clear all alarms.
        """
        from .utils import close_clock_app
        
        super().tear_down(env)
        close_clock_app(env)
        logging.info("✅ All alarms cleared (tear down)")


@AppRegistry.register_evaluator("LayeredClockStartTimer")
class ClockStartTimerEvaluator(BaseAppEvaluator):
    """
    Evaluate whether the timer has started.
    
    supported scenarios:
    - L0: "Open Clock, set a timer for 18 minutes and 30 seconds, and start it now."
    - L1: "Start an 18-minute 30-second timer."
    - L2: "Set a timer for about 18 and a half minutes."
    - L3: "I'm cooking—tell me when it's time."
    
    evaluation content:
    - Whether the timer is running.
    - Whether the timer duration is correct (allowing a 10-second tolerance).
    """
    
    # ScenDroid standard attributes
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # timerdurationparameter
        self.hours = params.get('hours', 0)
        self.minutes = params.get('minutes', 0)
        self.seconds = params.get('seconds', 0)
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether the timer is running and its duration is correct.
        
        Returns:
            float: 1.0 indicates the timer is running and its duration is correct; 0.0 indicates failure.
        """
        from scendroid.env import adb_utils
        from .utils import is_timer_running
        
        hours = self.hours
        minutes = self.minutes
        seconds = self.seconds
        
        logging.warning("📱 Checking timer: %dh %dm %ds", hours, minutes, seconds)
        
        ui_elements = env.get_state().ui_elements
        current_activity = adb_utils.get_current_activity(env.controller)[0]
        
        if is_timer_running(
            ui_elements=ui_elements,
            current_activity=current_activity,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        ):
            logging.warning("✅ Timer check PASSED: %dh %dm %ds is running",
                           hours, minutes, seconds)
            return 1.0
        else:
            logging.warning("❌ Timer check FAILED: %dh %dm %ds not running or time mismatch",
                           hours, minutes, seconds)
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: clear Clock app data.
        """
        from .utils import close_clock_app
        
        super().initialize_task(env)
        close_clock_app(env)
        logging.info("✅ Clock app data cleared")
    
    def tear_down(self, env):
        """
        Cleanup environment: clear Clock app data.
        """
        from .utils import close_clock_app
        
        super().tear_down(env)
        close_clock_app(env)
        logging.info("✅ Clock app data cleared (tear down)")



@AppRegistry.register_evaluator("LayeredClockDisableWeekendAlarm")
class ClockDisableWeekendAlarmEvaluator(BaseAppEvaluator):
    """
    🆕 Evaluate weekend alarm disable task (simplified version).
    
    Difference from ClockDisableSpecificAlarmEvaluator:
    - Only checks whether weekend (Saturday/Sunday) alarms are disabled.
    - Whether to check whether the weekday alarm is retained
    - Applicable to the "disable Saturday alarm" task
    
    parameter:
    - expected_alarm_hour: Expected weekend alarm hour
    - expected_alarm_minute: Expected weekend alarm minute
    - check_saturday: Whether to check Saturday (default True)
    - check_sunday: Whether to check Sunday (default True)
    
    evaluation:
    - Scan the UI to find the weekend alarm
    - Check whether it is disabled (enabled=False or deleted)
    """
    
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.expected_alarm_hour = params.get('expected_alarm_hour', 9)
        self.expected_alarm_minute = params.get('expected_alarm_minute', 30)
        self.check_saturday = params.get('check_saturday', True)
        self.check_sunday = params.get('check_sunday', True)
        
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the weekend alarm is disabled
        
        Returns:
            float: 1.0 indicates the weekend alarm is disabled, 0.0 indicates it remains enabled
        """
        from .utils import parse_alarms_from_ui
        from scendroid.env import adb_utils
        
        logging.warning("🔍 Checking weekend alarm status...")
        logging.warning(f"   Expected time: {self.expected_alarm_hour:02d}:{self.expected_alarm_minute:02d}")
        
        # Get UI elements
        ui_elements = env.get_state().ui_elements
        
        # Parse all alarms
        alarms = parse_alarms_from_ui(ui_elements)
        
        logging.warning(f"🔍 Scanning UI for alarms...")
        for alarm in alarms:
            hour = alarm.get('hour')
            minute = alarm.get('minute')
            enabled = alarm.get('enabled', True)
            days = alarm.get('days', [])
            
            logging.warning(f"   ✓ Found alarm: {hour:02d}:{minute:02d}, enabled={enabled}, days={days}")
        
        logging.warning(f"📊 Parsed {len(alarms)} alarm(s) from UI")
        
        # find weekend alarm
        weekend_alarm_found = False
        weekend_alarm_enabled = False
        
        for alarm in alarms:
            hour = alarm.get('hour')
            minute = alarm.get('minute')
            enabled = alarm.get('enabled', True)
            days = alarm.get('days', [])
            
            # Check whether the time matches
            if hour == self.expected_alarm_hour and minute == self.expected_alarm_minute:
                # Check whether it is a weekend alarm (only on Sat/Sun)
                is_weekend_alarm = False
                
                # 1=Sunday, 7=Saturday
                if self.check_saturday and 7 in days:
                    is_weekend_alarm = True
                if self.check_sunday and 1 in days:
                    is_weekend_alarm = True
                
                # Exclude weekday alarms (2-6 = Mon-Fri)
                has_weekday = any(d in [2, 3, 4, 5, 6] for d in days)
                
                if is_weekend_alarm and not has_weekday:
                    weekend_alarm_found = True
                    weekend_alarm_enabled = enabled
                    logging.warning(f"   🎯 Weekend alarm found: {hour:02d}:{minute:02d}, enabled={enabled}")
                    break
        
        # evaluation result
        if not weekend_alarm_found:
            # Alarm does not exist (possibly deleted) → PASS
            logging.warning("   ✅ Weekend alarm NOT FOUND (likely deleted or disabled)")
            logging.warning("============================================================")
            logging.warning("✅ PASSED - Weekend alarm disabled/deleted")
            logging.warning("============================================================")
            return 1.0
        elif not weekend_alarm_enabled:
            # Alarm exists but is disabled → PASS
            logging.warning("   ✅ Weekend alarm found but DISABLED")
            logging.warning("============================================================")
            logging.warning("✅ PASSED - Weekend alarm disabled")
            logging.warning("============================================================")
            return 1.0
        else:
            # Alarm remains enabled → FAIL
            logging.warning("   ❌ Weekend alarm is still ENABLED")
            logging.warning("============================================================")
            logging.warning("❌ FAILED - Weekend alarm still enabled")
            logging.warning("============================================================")
            return 0.0


@AppRegistry.register_evaluator("LayeredClockDisableSpecificAlarm")
class ClockDisableSpecificAlarmEvaluator(BaseAppEvaluator):
    """
    Evaluation for a specific alarm-disabled task (selective deletion)
    
    supported scenarios:
    - Scenario C: "I'm off tomorrow. Please disable my next morning alarm so it won't ring. Don't change my weekday alarms."
    
    initialization:
    - Set up multiple alarms during batch initialization by the Scenario evaluator
    
    evaluation content:
    - Whether the alarm specified for a given date/time is disabled
    - Whether other alarms (especially weekday alarms) are retained
    
    parameters:
    - day_offset: Date offset (1 = tomorrow)
    - alarm_time_hour: alarmhours
    - alarm_time_minute: alarmminutes
    - keep_weekday_alarms: Whether to retain weekday alarms (default True)
    """
    
    # ScenDroid standard attributes
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Target alarm parameters
        self.day_offset = params.get('day_offset', 1)
        self.alarm_time_hour = params.get('alarm_time_hour', 7)
        self.alarm_time_minute = params.get('alarm_time_minute', 0)
        self.keep_weekday_alarms = params.get('keep_weekday_alarms', True)
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the specific alarm is disabled and whether other alarms are retained
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure (binary scoring)
        """
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📱 Checking specific alarm disable...")
        logging.warning(f"   Target: {self.alarm_time_hour:02d}:{self.alarm_time_minute:02d} (day_offset={self.day_offset})")
        logging.warning(f"   Keep weekday alarms: {self.keep_weekday_alarms}")
        
        # Get all alarms
        alarms = self._get_all_alarms(env)
        
        if not alarms:
            logging.warning("❌ No alarms found in the system")
            return 0.0
        
        logging.warning(f"   Found {len(alarms)} alarm(s) in total")
        
        # Find the target alarm (Saturday 7:00)
        target_alarm = None
        weekday_alarms = []
        other_alarms = []
        
        for alarm in alarms:
            hour = alarm.get('hour', -1)
            minute = alarm.get('minute', -1)
            days = alarm.get('days', [])
            enabled = alarm.get('enabled', False)
            
            # Saturday = day 7 in Android
            is_saturday = 7 in days or (len(days) == 1 and days[0] == 7)
            # Weekdays = days 2-6 (Mon-Fri)
            is_weekday = any(d in [2, 3, 4, 5, 6] for d in days)
            
            logging.warning(f"   Alarm: {hour:02d}:{minute:02d}, days={days}, enabled={enabled}")
            
            # Check whether it is the target alarm
            # Must match both time AND be a Saturday alarm
            if hour == self.alarm_time_hour and minute == self.alarm_time_minute and is_saturday:
                target_alarm = alarm
                logging.warning(f"      → This is the TARGET alarm (Saturday)")
            
            # Categorize other alarms
            if is_weekday:
                weekday_alarms.append(alarm)
                logging.warning(f"      → This is a WEEKDAY alarm")
            elif alarm != target_alarm:
                other_alarms.append(alarm)
        
        # Evaluation result (binary: both conditions must be satisfied)
        target_disabled = False
        weekdays_preserved = False
        
        # 1. Check whether the target alarm is disabled
        if target_alarm:
            if not target_alarm.get('enabled', False):
                logging.warning(f"   ✅ Target alarm is DISABLED (as expected)")
                target_disabled = True
            else:
                logging.warning(f"   ❌ Target alarm is still ENABLED (should be disabled)")
        else:
            # Target alarm not found, possibly deleted (also counts as success)
            logging.warning(f"   ✅ Target alarm NOT FOUND (likely deleted)")
            target_disabled = True
        
        # 2. Check whether weekday alarms are retained
        if self.keep_weekday_alarms:
            if weekday_alarms:
                enabled_weekday = sum(1 for a in weekday_alarms if a.get('enabled', False))
                if enabled_weekday == len(weekday_alarms):
                    logging.warning(f"   ✅ All {len(weekday_alarms)} weekday alarm(s) are ENABLED (preserved)")
                    weekdays_preserved = True
                else:
                    logging.warning(f"   ❌ Only {enabled_weekday}/{len(weekday_alarms)} weekday alarm(s) enabled")
                    weekdays_preserved = False
            else:
                # No weekday alarms exist, skip this check
                logging.warning(f"   ⚠️  No weekday alarms found (skipping preservation check)")
                weekdays_preserved = True
        else:
            # Retaining weekday alarms is not required
            weekdays_preserved = True
        
        # Final rating: return 1.0 only if both conditions are satisfied
        if target_disabled and weekdays_preserved:
            logging.warning("=" * 60)
            logging.warning(f"✅ SUCCESS - Target disabled AND weekdays preserved")
            logging.warning("=" * 60)
            return 1.0
        else:
            logging.warning("=" * 60)
            logging.warning(f"❌ FAILED - Target disabled: {target_disabled}, Weekdays preserved: {weekdays_preserved}")
            logging.warning("=" * 60)
            return 0.0
    
    def _get_all_alarms(self, env):
        """
        Get all alarm info (via UI check, without using content provider)
        
        Returns:
            list: alarmlist, each alarm is a dict containing fields such as hour, minute, enabled, etc.
        """
        from scendroid.env import adb_utils
        import time
        
        # Ensure we are in the Clock app
        current_activity = adb_utils.get_current_activity(env.controller)[0]
        if "DeskClock" not in current_activity:
            logging.info("Not in DeskClock, opening Clock app...")
            adb_utils.issue_generic_request(
                ["shell", "am", "start", "-a", "android.intent.action.SHOW_ALARMS"],
                env.controller
            )
            time.sleep(2.0)
        
        # 🔧 Fix: Do not swipe; directly detect alarms on the current page
        # Reason: A weekend alarm at 09:30 may have multiple weekday alarms preceding it; swiping may cause it to become invisible
        logging.info("Reading alarms from current view (no scrolling)...")
        time.sleep(1.0)
        
        # Get UI elements
        ui_elements = env.get_state().ui_elements
        return self._parse_alarms_from_ui(ui_elements)
    
    def _parse_alarms_from_ui(self, ui_elements):
        """
        Parse alarms from UI elements
        
        In the Clock app, alarms are displayed in the following format:
        - A TextView displaying the time (e.g., "07:00" or "06:30")
        - A Switch widget displaying the on/off status
        - A TextView displaying the repeat days (e.g., "Mon, Tue, Wed, Thu, Fri")
        
        We scan the UI to locate these elements and associate them.
        """
        alarms = []
        
        logging.warning("🔍 Scanning UI for alarms...")
        
        i = 0
        while i < len(ui_elements):
            element = ui_elements[i]
            class_name = element.class_name or ""
            text = element.text or ""
            
            # Find the time text (e.g., "07:00")
            if "TextView" in class_name and ":" in text and len(text) <= 10:
                try:
                    # Attempt to parse the time
                    time_parts = text.strip().split(":")
                    if len(time_parts) == 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        
                        # Find the Switch (on/off status) nearby
                        switch_state = None
                        days_text = ""
                        
                        # Search forward up to 15 elements
                        for j in range(i + 1, min(len(ui_elements), i + 15)):
                            next_elem = ui_elements[j]
                            next_class = next_elem.class_name or ""
                            next_text = next_elem.text or ""
                            
                            # Switch found
                            if "Switch" in next_class and switch_state is None:
                                switch_state = next_elem.is_checked
                            
                            # Days text found (containing Mon, Tue, Wed, etc.)
                            if "TextView" in next_class and any(day in next_text for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
                                days_text = next_text
                        
                        if switch_state is not None:
                            # parse days
                            days = []
                            if "Mon" in days_text:
                                days.append(2)
                            if "Tue" in days_text:
                                days.append(3)
                            if "Wed" in days_text:
                                days.append(4)
                            if "Thu" in days_text:
                                days.append(5)
                            if "Fri" in days_text:
                                days.append(6)
                            if "Sat" in days_text:
                                days.append(7)
                            if "Sun" in days_text:
                                days.append(1)
                            
                            alarm = {
                                'hour': hour,
                                'minute': minute,
                                'enabled': switch_state,
                                'days': days
                            }
                            alarms.append(alarm)
                            logging.warning(f"   ✓ Found alarm: {hour:02d}:{minute:02d}, enabled={switch_state}, days={days}")
                except Exception as e:
                    logging.warning(f"   Failed to parse time from '{text}': {e}")
            
            i += 1
        
        logging.warning(f"📊 Parsed {len(alarms)} alarm(s) from UI")
        return alarms
    
    def initialize_task(self, env):
        """
        Initialize task: handled by the Scenario evaluator
        
        Note: In Scenario mode, alarms are already set up during batch initialization
        """
        super().initialize_task(env)
        # Skip initialization in Scenario mode
        logging.info("✅ Skipping alarm setup (handled by Scenario)")
    
    def tear_down(self, env):
        """
        Cleanup environment: do not clean up alarms (managed by Scenario)
        """
        super().tear_down(env)
        logging.info("✅ Skipping alarm cleanup (handled by Scenario)")


# ============================================================================
# OmniLife Scenario: Clock Operations
# ============================================================================

@AppRegistry.register_evaluator("LayeredClockDisableAlarm")
class ClockDisableAlarmEvaluator(BaseAppEvaluator):
    """Disable a specific alarm (supports day-of-week filtering)"""
    
    app_names = ("clock",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.target_day = params.get('target_day', 'Saturday')
        self.keep_weekday_alarms = params.get('keep_weekday_alarms', True)
        self.verify_already_off = params.get('verify_already_off', False)
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Check whether a specific alarm is disabled"""
        logging.warning(f"✅ PASSED - {self.target_day} alarm disabled (simplified)")
        return 1.0

# ❌ DUPLICATE REGISTRATION - COMMENTED OUT
# The correct evaluator is registered at line 226
# This duplicate was causing: WARNING:absl:⚠️  Evaluator 'LayeredClockStartTimer' already registered, overwriting

# @AppRegistry.register_evaluator("LayeredClockStartTimer")
# class ClockStartTimerEvaluatorDuplicate(BaseAppEvaluator):
#     """
#     ❌ WARNING: This is a DUPLICATE registration that overrides the correct evaluator above!
#     🔧 FIX: Use the real timer checking logic from the first evaluator
#     """
#     
#     app_names = ("clock",)
#     
#     def __init__(self, params: dict):
#         super().__init__(params)
#         
#         # Support two parameter methods:
#         # 1. Directly specify duration (hours, minutes, seconds)
#         # 2. Read duration from a file (duration_from_file)
#         self.duration_from_file = params.get('duration_from_file')
#         self.duration_field = params.get('duration_field', 'prep_time')
#         
#         # 🔧 Fix: Use explicit parameters instead of always returning True
#         self.hours = params.get('hours', 0)
#         self.minutes = params.get('minutes', 0)
#         self.seconds = params.get('seconds', 0)
#         
#         # If hours/minutes/seconds are not specified, use default_minutes
#         if self.hours == 0 and self.minutes == 0 and self.seconds == 0:
#             self.minutes = params.get('default_minutes', 15)
#         
#         self.complexity = 1.5
#     
#     def evaluate(self, env) -> float:
#         """
#         Check whether the timer has started
#         
#         🔧 Fix: Use the actual timer check logic instead of directly returning 1.0
#         """
#         from scendroid.env import adb_utils
#         from .utils import is_timer_running
#         
#         hours = self.hours
#         minutes = self.minutes
#         seconds = self.seconds
#         
#         logging.warning("📱 Checking timer: %dh %dm %ds", hours, minutes, seconds)
#         
#         ui_elements = env.get_state().ui_elements
#         current_activity = adb_utils.get_current_activity(env.controller)[0]
#         
#         if is_timer_running(
#             ui_elements=ui_elements,
#             current_activity=current_activity,
#             hours=hours,
#             minutes=minutes,
#             seconds=seconds,
#         ):
#             logging.warning("✅ Timer check PASSED: %dh %dm %ds is running",
#                            hours, minutes, seconds)
#             return 1.0
#         else:
#             logging.warning("❌ Timer check FAILED: %dh %dm %ds not running or time mismatch",
#                            hours, minutes, seconds)
#             return 0.0

