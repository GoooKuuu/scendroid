"""
Clock App Utility Functions

Provides helper functions related to the Clock app for initialization and evaluation.  
These functions are reused from scendroid.task_evals.single.layered_tasks
"""

import datetime
import re
import time
from absl import logging

from scendroid.env import adb_utils
from scendroid.env import interface
from scendroid.env import representation_utils


def get_device_time_ms(env: interface.AsyncEnv) -> int:
    """
    Get device current time in milliseconds since epoch.
    
    Args:
        env: The environment interface
        
    Returns:
        Current device time in milliseconds
    """
    adb_output = adb_utils.issue_generic_request(
        ["shell", "date", "+%s"], env.controller
    )
    return int(adb_output.generic.output.strip()) * 1000


def close_clock_app(env: interface.AsyncEnv):
    """
    Closes the clock app and clears its data.
    
    Args:
        env: The environment interface
    """
    adb_utils.clear_app_data(
        adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
        env.controller,
    )


def set_alarm_via_intent(
    env: interface.AsyncEnv,
    hour: int,
    minute: int,
    skip_ui: bool = True,
) -> None:
    """
    Set an alarm using Android Intent.
    
    Args:
        env: The environment interface
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
        skip_ui: If True, skip UI interaction (alarm is set directly)
    """
    # Use Android's SET_ALARM intent
    extras = {
        'android.intent.extra.alarm.HOUR': ('int', hour),
        'android.intent.extra.alarm.MINUTES': ('int', minute),
        'android.intent.extra.alarm.SKIP_UI': ('bool', skip_ui),
    }
    
    adb_utils.send_android_intent(
        command='start',
        action='android.intent.action.SET_ALARM',
        env=env.controller,
        extras=extras,
    )
    time.sleep(1.0)  # Wait for alarm to be set


def check_all_alarms_disabled(env: interface.AsyncEnv) -> bool:
    """
    Check if all alarms are disabled (off) in the Clock app.
    
    The key indicator of an enabled alarm is a Switch control with is_checked=True.
    We look for Switch widgets in the alarm list and check their checked state.
    
    Args:
        env: The environment interface
    
    Returns:
        True if all alarms are disabled or no alarms exist
    """
    ui_elements = env.get_state().ui_elements
    current_activity = adb_utils.get_current_activity(env.controller)[0]
    
    if "DeskClock" not in current_activity:
        logging.warning("Not in DeskClock activity: %s", current_activity)
        return False
    
    # Look for enabled alarms by finding Switch controls that are checked
    # In Clock app, each alarm has a Switch widget to enable/disable it
    enabled_alarms = []
    disabled_alarms = []
    
    logging.warning("🔍 Scanning UI for alarm switches...")
    
    for i, element in enumerate(ui_elements):
        # Check if this is a Switch control (the toggle for alarms)
        class_name = element.class_name or ""
        
        # Switches in Clock app are typically android.widget.Switch
        if "Switch" in class_name:
            is_on = element.is_checked
            desc = element.content_description or ""
            
            logging.warning("  [%d] Found Switch: is_checked=%s, desc='%s', class='%s'",
                          i, is_on, desc, class_name)
            
            if is_on:
                enabled_alarms.append((i, desc))
                logging.warning("      ⚠️  This alarm is ENABLED")
            else:
                disabled_alarms.append((i, desc))
                logging.warning("      ✓ This alarm is disabled")
    
    logging.warning("📊 Alarm Summary:")
    logging.warning("   - Total switches found: %d", len(enabled_alarms) + len(disabled_alarms))
    logging.warning("   - Enabled alarms: %d", len(enabled_alarms))
    logging.warning("   - Disabled alarms: %d", len(disabled_alarms))
    
    if enabled_alarms:
        logging.warning("❌ Found %d enabled alarm(s):", len(enabled_alarms))
        for idx, desc in enabled_alarms:
            logging.warning("   - Element [%d]: %s", idx, desc or "(no description)")
        return False
    else:
        if disabled_alarms:
            logging.warning("✅ All %d alarm(s) are disabled", len(disabled_alarms))
        else:
            logging.warning("✅ No alarm switches found (possibly no alarms exist)")
        return True


def is_timer_running(
    ui_elements: list[representation_utils.UIElement],
    current_activity: str,
    *,
    hours: int,
    minutes: int,
    seconds: int,
) -> bool:
    """
    Determines if a timer is running with the specified duration.
    
    When a timer is running, the UI typically shows:
    - A "Pause" button (content_description="Pause")
    - The remaining time counting down
    
    Args:
        ui_elements: UI elements from the current screen
        current_activity: Current activity name
        hours: Expected hours
        minutes: Expected minutes  
        seconds: Expected seconds
        
    Returns:
        True if timer is running with approximately the correct time
    """
    if "DeskClock" not in current_activity:
        logging.debug("Not in DeskClock activity: %s", current_activity)
        return False
    
    # Check for Pause button (indicates timer is running)
    has_pause_button = False
    for element in ui_elements:
        if element.content_description == "Pause":
            has_pause_button = True
            break
    
    if not has_pause_button:
        logging.debug("No Pause button found - timer not running")
        return False
    
    # Timer is running, now check if time is approximately correct
    # Since timer is counting down, we allow some tolerance (within 10 seconds)
    total_seconds_expected = hours * 3600 + minutes * 60 + seconds
    
    # Look for time display in various formats
    for element in ui_elements:
        # Check text like "00h 18m 30s" or "18m 30s"
        if element.text and ('m' in element.text or 'h' in element.text):
            try:
                # Parse time from text
                time_text = element.text
                h_match = re.search(r'(\d+)h', time_text)
                m_match = re.search(r'(\d+)m', time_text)
                s_match = re.search(r'(\d+)s', time_text)
                
                found_hours = int(h_match.group(1)) if h_match else 0
                found_minutes = int(m_match.group(1)) if m_match else 0
                found_seconds = int(s_match.group(1)) if s_match else 0
                
                total_seconds_found = found_hours * 3600 + found_minutes * 60 + found_seconds
                
                # Allow tolerance of 10 seconds (timer is counting down)
                time_diff = abs(total_seconds_expected - total_seconds_found)
                if time_diff <= 10:
                    logging.info("✅ Timer running with correct time: %dh %dm %ds (expected: %dh %dm %ds, diff: %ds)",
                                found_hours, found_minutes, found_seconds,
                                hours, minutes, seconds, time_diff)
                    return True
                else:
                    logging.debug("Timer time mismatch: found %ds, expected %ds, diff %ds",
                                 total_seconds_found, total_seconds_expected, time_diff)
            except (ValueError, AttributeError) as e:
                logging.debug("Failed to parse timer text '%s': %s", element.text, e)
                continue
    
    logging.debug("Timer is running but time doesn't match")
    return False


def check_alarm_with_date(
    env: interface.AsyncEnv,
    hour: int,
    minute: int,
    day_offset: int = 0,
    enabled: bool = True
) -> bool:
    """
    Check if an alarm exists with specified time via UI.
    
    This function scrolls to the top of the alarm list before checking,
    to ensure all alarms are visible, addressing the issue where clicking
    on one alarm causes others to scroll out of view.
    
    Args:
        env: The environment interface
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
        day_offset: Days from today (0=today, 1=tomorrow, etc.)
        enabled: Whether alarm should be enabled (checks Switch is_checked state)
        
    Returns:
        True if alarm exists with matching time, date, and enabled state
    """
    logging.info("📱 Checking alarm: %02d:%02d, day_offset=%d, enabled=%s", 
                 hour, minute, day_offset, enabled)
    
    # Ensure we're in Clock app
    current_activity = adb_utils.get_current_activity(env.controller)[0]
    
    if "DeskClock" not in current_activity:
        logging.info("Not in DeskClock, opening Clock app...")
        adb_utils.issue_generic_request(
            ["shell", "am", "start", "-a", "android.intent.action.SHOW_ALARMS"],
            env.controller
        )
        time.sleep(2.0)
    
    # Scroll to top to see all alarms (addresses issue where clicking one alarm 
    # causes the target alarm to scroll out of view)
    logging.info("Scrolling to top to ensure all alarms are visible...")
    for i in range(2):  # Scroll content up multiple times to reach the top
        # swipe format: x1 y1 x2 y2
        # Swipe finger from top to bottom (300 -> 1000) to scroll content UP
        adb_utils.issue_generic_request(
            ["shell", "input", "swipe", "500", "300", "500", "1000"],
            env.controller
        )
        time.sleep(0.3)
    
    # Wait a bit for UI to settle
    time.sleep(1.0)
    
    # Now check UI (this will call env.get_state() internally)
    return _check_alarm_ui_with_date(env, hour, minute, day_offset, enabled)


def _check_alarm_ui_with_date(
    env: interface.AsyncEnv,
    hour: int,
    minute: int,
    day_offset: int = 0,
    enabled: bool = True
) -> bool:
    """
    Check if an alarm exists by UI, trying to verify date from UI text.
    
    Args:
        env: The environment interface
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
        day_offset: Days from today (0=today, 1=tomorrow, etc.)
        enabled: Whether alarm should be enabled (checks Switch is_checked state)
        
    Returns:
        True if alarm with matching time, date, and enabled state found in UI
    """
    current_activity = adb_utils.get_current_activity(env.controller)[0]
    
    # If not in Clock app main screen, navigate back to it
    if "DeskClock" not in current_activity:
        logging.info("Not in DeskClock activity: %s, navigating to main screen", current_activity)
        # Press back button to return to main Clock screen
        adb_utils.issue_generic_request(
            ["shell", "input", "keyevent", "KEYCODE_BACK"],
            env.controller
        )
        time.sleep(1.0)
        
        # Try to open Clock app if still not there
        current_activity = adb_utils.get_current_activity(env.controller)[0]
        if "DeskClock" not in current_activity:
            logging.info("Opening Clock app...")
            adb_utils.start_activity(
                adb_utils.get_adb_activity("clock"),
                None,
                env.controller
            )
            time.sleep(2.0)
    
    # Get UI elements after ensuring we're in the right activity
    ui_elements = env.get_state().ui_elements
    
    # Convert to 12-hour format
    if hour == 0:
        display_hour = 12
        period = "AM"
    elif hour < 12:
        display_hour = hour
        period = "AM"
    elif hour == 12:
        display_hour = 12
        period = "PM"
    else:
        display_hour = hour - 12
        period = "PM"
    
    # Possible time strings to match
    time_str_24 = f"{hour:02d}:{minute:02d}"
    time_str_24_no_leading = f"{hour}:{minute:02d}"
    time_str_12 = f"{display_hour}:{minute:02d}"
    time_str_12_with_period = f"{display_hour}:{minute:02d} {period}"
    time_str_12_space = f"{display_hour} {minute:02d}"
    
    # Expected date indicators based on day_offset
    date_indicators = []
    if day_offset == 0:
        date_indicators = ["today", "Today"]
    elif day_offset == 1:
        date_indicators = ["tomorrow", "Tomorrow", "tmrw", "Tmrw"]
    elif day_offset >= 2 and day_offset <= 7:
        # Get device time to calculate target weekday
        device_time_ms = get_device_time_ms(env)
        device_dt = datetime.datetime.fromtimestamp(device_time_ms / 1000.0)
        target_dt = device_dt + datetime.timedelta(days=day_offset)
        weekday_full = target_dt.strftime("%A")  # "Monday"
        weekday_short = target_dt.strftime("%a")  # "Mon"
        date_indicators = [weekday_full, weekday_short]
    
    logging.info("Looking for alarm time: %s (or variants)", time_str_12_with_period)
    if day_offset > 0:
        logging.info("Expected date indicators: %s", date_indicators)
    
    # Log all UI elements for debugging (only in verbose mode)
    logging.debug("=== All UI Elements ===")
    for i, element in enumerate(ui_elements):
        if element.text or element.content_description:
            logging.debug("  [%d] text='%s', desc='%s'", i, element.text, element.content_description)
    logging.debug("======================")
    
    # Search for alarm time in UI elements
    found_time_elements = []
    for i, element in enumerate(ui_elements):
        element_text = element.text or ""
        element_desc = element.content_description or ""
        
        # Check if this element contains the time
        if (time_str_24 in element_text or
            time_str_24_no_leading in element_text or
            time_str_12 in element_text or
            time_str_12_with_period in element_text or
            time_str_12_space in element_text or
            time_str_24 in element_desc or
            time_str_12_with_period in element_desc):
            
            logging.info("✓ Found time match at element [%d]: text='%s', desc='%s'",
                        i, element_text, element_desc)
            found_time_elements.append((i, element_text, element_desc))
    
    if not found_time_elements:
        logging.info("❌ Alarm time not found in UI")
        return False
    
    # Helper function to check if a Switch near a given element matches the desired enabled state
    def check_switch_state_near_element(element_idx: int, required_enabled: bool) -> bool:
        """Check if there's a Switch near the given element with the required enabled state.
        
        Note: In Android Clock app, the Switch is typically to the right of the time text
        (i.e., has a higher index in the UI tree), so we prioritize checking forward first.
        """
        # 🔧 FIX: Check FORWARD first (time element -> Switch is typical layout)
        # Then check backward as fallback
        search_order = list(range(1, 11)) + [0] + list(range(-1, -11, -1))
        
        found_switches = []  # Store all found switches with their distance
        
        for offset in search_order:
            check_idx = element_idx + offset
            if 0 <= check_idx < len(ui_elements):
                nearby_elem = ui_elements[check_idx]
                class_name = nearby_elem.class_name or ""
                
                # Found a Switch control
                if "Switch" in class_name:
                    is_checked = nearby_elem.is_checked
                    distance = abs(offset)
                    found_switches.append((check_idx, is_checked, distance))
                    logging.info("   Found Switch at element [%d] (offset=%+d): is_checked=%s",
                               check_idx, offset, is_checked)
        
        if not found_switches:
            # No Switch found nearby
            if not required_enabled:
                logging.info("   No Switch found near element [%d], assuming disabled", element_idx)
                return True
            logging.info("   ❌ No Switch found near element [%d]", element_idx)
            return False
        
        # 🔧 FIX: Use the CLOSEST Switch (smallest distance)
        found_switches.sort(key=lambda x: x[2])  # Sort by distance
        closest_idx, closest_checked, closest_dist = found_switches[0]
        
        logging.info("   Using CLOSEST Switch at element [%d] (distance=%d): is_checked=%s (required: %s)",
                   closest_idx, closest_dist, closest_checked, required_enabled)
        
        # Check if the closest switch state matches what we're looking for
        if closest_checked == required_enabled:
            logging.info("   ✓ Switch state matches!")
            return True
        else:
            logging.info("   ✗ Switch state mismatch (is_checked=%s, need %s)",
                       closest_checked, required_enabled)
            return False
    
    # If day_offset == 0, check time and enabled state
    if day_offset == 0:
        logging.warning("✅ Found alarm time (day_offset=0, checking enabled state...)")
        
        # Check each found time element for matching switch state
        for time_idx, time_text, time_desc in found_time_elements:
            if check_switch_state_near_element(time_idx, enabled):
                logging.warning("✅ Alarm found with correct time and enabled state!")
                return True
        
        logging.warning("❌ Alarm time found but enabled state mismatch (required: %s)", enabled)
        return False
    
    # For day_offset > 0, try to verify date and enabled state
    # Check nearby elements for date indicators
    for time_idx, time_text, time_desc in found_time_elements:
        logging.info("Checking date for alarm at element [%d]", time_idx)
        
        date_found = False
        
        # Check in same element
        for indicator in date_indicators:
            if indicator in time_text or indicator in time_desc:
                logging.info("✅ Found date indicator '%s' in same element!", indicator)
                date_found = True
                break
        
        # Check surrounding elements (±5 positions) if not found in same element
        if not date_found:
            for offset in range(-5, 6):
                check_idx = time_idx + offset
                if 0 <= check_idx < len(ui_elements):
                    nearby_elem = ui_elements[check_idx]
                    nearby_text = nearby_elem.text or ""
                    nearby_desc = nearby_elem.content_description or ""
                    
                    for indicator in date_indicators:
                        if indicator in nearby_text or indicator in nearby_desc:
                            logging.warning("✅ Found date indicator '%s' at element [%d]", indicator, check_idx)
                            logging.debug("   text='%s', desc='%s'", nearby_text, nearby_desc)
                            date_found = True
                            break
                    
                    if date_found:
                        break
        
        # If date matches, also check enabled state
        if date_found:
            logging.info("Date verified, now checking enabled state...")
            if check_switch_state_near_element(time_idx, enabled):
                logging.warning("✅ Alarm found with correct time, date, and enabled state!")
                return True
            else:
                logging.warning("❌ Date matches but enabled state mismatch (required: %s)", enabled)
    
    # Found time but no date indicator or wrong enabled state
    logging.warning("❌ Alarm not found with all required criteria (day_offset=%d, enabled=%s)", 
                   day_offset, enabled)
    return False

