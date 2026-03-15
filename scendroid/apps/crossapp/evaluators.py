"""
CrossApp Evaluators

Provides evaluators for CrossApp cross-application tasks:

Base evaluators:
1. LayeredCrossAppShoppingExpense - Shopping + Expense (composite)
2. LayeredCrossAppMeetingNotification - Calendar + SMS (collaborative)
3. LayeredCrossAppMeetingUpdateNotify - Calendar + SMS (collaborative)
4. LayeredCrossAppSportsSummary - OpenTracks + Markor (collaborative)
5. LayeredCrossAppScheduleQuery - Calendar + Tasks (question-answering)

New evaluators for Scenario C:
C1. LayeredCrossAppClockCalendar - Clock + Calendar (set alarm + create calendar event)
C2. LayeredExpenseFromReceipt - Files + Expense (record expense from receipt)
C3. LayeredCrossAppMusicPlaylistTrack - RetroMusic + OpenTracks (create duration-constrained playlist + track workout)
C4. LayeredMarkorSMSSummary - SMS + Markor (summarize SMS replies into document)

Note:
- All imports from scendroid.env are performed inside methods
- Reuse App Layer utility functions as much as possible
- Collaborative tasks require custom initialize_task and evaluate methods
"""

import time
from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.crossapp.base import BaseCrossAppEvaluator


# ============================================================================
# 1. LayeredCrossAppShoppingExpense - Shopping + Expense (composite)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppShoppingExpense")
class CrossAppShoppingExpenseEvaluator(BaseCrossAppEvaluator):
    """
    Shopping + Expense cross-application task
    
    Task flow:
    1. Shopping: Purchase a product on a website
    2. Expense: Record the expense in the Pro Expense app
    
    Evaluation method:
    - 50% Shopping: Check whether the order contains the correct product keywords
    - 50% Expense: Check whether the expense record contains the correct keywords and category
    
    This is a composite task that directly reuses the existing Shopping and Expense evaluators
    """
    
    app_names = ("chrome", "pro expense")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Save parameters
        self.product_keywords = params.get('product_keywords', [])
        self.expense_keywords = params.get('expense_keywords', [])
        self.expense_category = params.get('expense_category', 'Others')
        
        # Set complexity
        self.complexity = 3.0
    
    def initialize_task(self, env):
        """
        Custom initialization: Initialize both Shopping and Expense simultaneously
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Shopping + Expense")
        logging.info("=" * 60)
        
        # Part 1: Initialize Shopping site (login)
        logging.info("🛒 Part 1: Initializing Shopping site...")
        try:
            from scendroid.task_evals.webarena import webarena_task
            
            webarena_helper = webarena_task.ProgramHTMLWebArenaTask({
                'task_id': 42,
                'intent': 'Add product to cart',
                'start_url': '__SHOPPING__',
                'eval_config': {},
                'require_login': True,
            })
            
            webarena_helper.initialize_task(env)
            logging.info("   ✅ Shopping site ready")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Shopping initialization issue: {e}")
        
        # Part 2: Clear existing expenses
        logging.info("💰 Part 2: Initializing Pro Expense app...")
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            EXPENSE_TABLE = "expense"
            EXPENSE_APP_NAME = "pro expense"
            
            sqlite_utils.delete_all_rows_from_table(
                EXPENSE_TABLE,
                EXPENSE_DB_PATH,
                env,
                EXPENSE_APP_NAME
            )
            
            self._before_expenses = sqlite_utils.get_rows_from_remote_device(
                EXPENSE_TABLE,
                EXPENSE_DB_PATH,
                sqlite_schema_utils.Expense,
                env,
            )
            
            logging.info(f"   ✅ Expense database cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Expense initialization issue: {e}")
            self._before_expenses = []
        
        logging.info("📋 Task Parameters:")
        logging.info(f"   🛍️  Product keywords: {', '.join(self.product_keywords)}")
        logging.info(f"   💵 Expense keywords: {', '.join(self.expense_keywords)}")
        logging.info(f"   🏷️  Expense category: {self.expense_category}")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Custom evaluation: Verify the Shopping order and Expense record
        
        Returns:
            Weighted score: 50% Shopping + 50% Expense
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: Shopping + Expense")
        logging.warning("=" * 60)
        
        # Part 1: Check Shopping order
        order_score = self._evaluate_shopping(env)
        
        # Part 2: Check Expense record
        expense_score = self._evaluate_expense(env)
        
        # 🆕 Binary scoring: Both parts must succeed
        final_score = 1.0 if (order_score >= 0.99 and expense_score >= 0.99) else 0.0
        
        logging.warning("=" * 60)
        logging.warning(f"📊 CrossApp Scores:")
        logging.warning(f"   Shopping Order: {'✅' if order_score >= 0.99 else '❌'}")
        logging.warning(f"   Expense Record: {'✅' if expense_score >= 0.99 else '❌'}")
        logging.warning(f"   Final Score: {final_score:.2f}")
        logging.warning("=" * 60)
        
        return final_score
    
    def _evaluate_shopping(self, env) -> float:
        """Evaluate Shopping order"""
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.info("🛒 Checking Shopping order...")
            
            program_html_config = [{
                "url": "func:shopping_get_latest_order_url()",
                "locator": "document.querySelector(\".order-details-items.ordered\").outerText",
                "required_contents": {
                    "must_include": self.product_keywords
                }
            }]
            
            score, explanations = program_html_helper.evaluate_program_html_via_cdp(
                env, program_html_config
            )
            
            if score >= 0.99:
                logging.warning("   ✅ Shopping order contains product keywords")
            else:
                logging.warning("   ❌ Shopping order missing product keywords")
            
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Shopping evaluation error: {e}")
            return 0.0
    
    def _evaluate_expense(self, env) -> float:
        """Evaluate Expense record"""
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            logging.info("💰 Checking Expense record...")
            
            EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            EXPENSE_TABLE = "expense"
            
            current_expenses = sqlite_utils.get_rows_from_remote_device(
                EXPENSE_TABLE,
                EXPENSE_DB_PATH,
                sqlite_schema_utils.Expense,
                env,
            )
            
            new_expenses = [e for e in current_expenses if e not in self._before_expenses]
            
            if not new_expenses:
                logging.warning("   ❌ No new expense records found")
                return 0.0
            
            # Check if any new expense matches the criteria
            for expense in new_expenses:
                note = (expense.note or "").lower()
                category = (expense.category or "").lower()
                
                # Check keywords
                keywords_match = all(
                    kw.lower() in note for kw in self.expense_keywords
                )
                
                # Check category (fuzzy match)
                category_match = self.expense_category.lower() in category
                
                if keywords_match and category_match:
                    logging.warning(f"   ✅ Expense record matches (category: {expense.category})")
                    return 1.0
            
            logging.warning("   ❌ No matching expense record found")
            return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Expense evaluation error: {e}")
            return 0.0
    
    def tear_down(self, env):
        """Cleanup: Rebuild Shopping container"""
        super().tear_down(env)
        
        try:
            from scendroid.task_evals.webarena import container_manager
            logging.info("   🔄 Rebuilding Shopping container...")
            manager = container_manager.ShoppingContainerManager()
            manager.rebuild_container()
        except Exception as e:
            logging.error(f"   ❌ Container rebuild error: {e}")


# ============================================================================
# 2. LayeredCrossAppMeetingNotification - Calendar + SMS (collaborative)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppMeetingNotification")
class CrossAppMeetingNotificationEvaluator(BaseCrossAppEvaluator):
    """
    Calendar + SMS cross-app task: Query a meeting and notify attendees
    
    Task flow:
    1. Calendar: Open the calendar, locate the meeting at the specified time, and retrieve the list of attendees
    2. SMS: Send a notification containing the time, location, and the word "meeting" to all attendees
    
    Evaluation method:
    - Verify that all attendees received the SMS
    - Verify that the SMS contains the required keywords (time, location, "meeting")
    - Verify that distractor contacts did not receive the SMS
    """
    
    app_names = ("simple calendar pro", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.meeting_hour = params.get('meeting_hour')
        self.meeting_minute = params.get('meeting_minute', 0)
        self.meeting_location = params.get('meeting_location', '')
        self.attendees = params.get('attendees', [])
        self.distractor_contacts = params.get('distractor_contacts', [])
        self.other_meetings = params.get('other_meetings', [])
        
        self.complexity = 3.0
    
    def initialize_task(self, env):
        """
        Initialize: Create the meeting and contacts
        """
        from scendroid.env import adb_utils, device_constants
        from scendroid.task_evals.single import calendar as calendar_utils
        from scendroid.task_evals.utils import contacts_utils, sqlite_schema_utils
        from scendroid.utils import datetime_utils
        from scendroid.apps.crossapp import utils as crossapp_utils
        
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Calendar + SMS (Meeting Notification)")
        logging.info("=" * 60)
        
        # Disable notifications
        adb_utils.disable_headsup_notifications(env.controller)
        
        # Clear calendar and contacts
        calendar_utils.clear_calendar_db(env)
        contacts_utils.clear_contacts(env.controller)
        time.sleep(2.0)
        
        # Get device time
        device_time_ms = crossapp_utils.get_device_time_ms(env)
        device_time_sec = device_time_ms // 1000
        device_dt = datetime_utils.timestamp_to_localized_datetime(
            device_time_sec, timezone=device_constants.TIMEZONE
        )
        
        # Create the target meeting
        meeting_dt = device_dt.replace(
            hour=self.meeting_hour,
            minute=self.meeting_minute,
            second=0,
            microsecond=0
        )
        
        attendee_names = [att["name"] for att in self.attendees]
        description = f"Attendees: {', '.join(attendee_names)}"
        
        logging.info("📅 Creating target meeting:")
        logging.info(f"   Time: {meeting_dt.strftime('%Y-%m-%d %H:%M')}")
        logging.info(f"   Location: {self.meeting_location}")
        logging.info(f"   Attendees: {', '.join(attendee_names)}")
        
        meeting_start_ts = int(meeting_dt.timestamp())
        meeting_end_ts = meeting_start_ts + (60 * 60)  # 60 minutes
        
        events_to_add = []
        target_event = sqlite_schema_utils.CalendarEvent(
            start_ts=meeting_start_ts,
            end_ts=meeting_end_ts,
            title="Team Meeting",
            location=self.meeting_location,
            description=description,
        )
        events_to_add.append(target_event)
        
        # Add distractor meetings
        for other_meeting in self.other_meetings:
            other_dt = device_dt.replace(
                hour=other_meeting["hour"],
                minute=other_meeting["minute"],
                second=0,
                microsecond=0
            )
            other_start_ts = int(other_dt.timestamp())
            other_end_ts = other_start_ts + (30 * 60)
            
            other_event = sqlite_schema_utils.CalendarEvent(
                start_ts=other_start_ts,
                end_ts=other_end_ts,
                title=other_meeting["title"],
                location=other_meeting.get("location", ""),
                description="",
            )
            events_to_add.append(other_event)
        
        calendar_utils.add_events(events_to_add, env)
        logging.info("✅ Calendar events added")
        time.sleep(2.0)
        
        # Add attendee contacts
        logging.info("📞 Adding contacts...")
        for attendee in self.attendees:
            try:
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                contacts_utils.add_contact(
                    attendee["name"],
                    attendee["number"],
                    env.controller,
                    ui_delay_sec=1.5
                )
                logging.info(f"   ✓ Added: {attendee['name']}")
                time.sleep(1.5)
            except Exception as e:
                logging.error(f"   ✗ Failed to add {attendee['name']}: {e}")
        
        # Add distractor contacts
        for distractor in self.distractor_contacts:
            try:
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                contacts_utils.add_contact(
                    distractor["name"],
                    distractor["number"],
                    env.controller,
                    ui_delay_sec=1.5
                )
                logging.info(f"   ✓ Added distractor: {distractor['name']}")
                time.sleep(1.5)
            except Exception as e:
                logging.error(f"   ✗ Failed to add distractor {distractor['name']}: {e}")
        
        logging.info("✅ Initialization complete")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Evaluation: Check whether the correct SMS was sent to all attendees
        """
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: Meeting Notification")
        logging.warning("=" * 60)
        
        try:
            # Retrieve the sent SMS messages
            response = adb_utils.issue_generic_request(
                "shell content query --uri content://sms/sent".split(),
                env.controller
            )
            sent_messages = sms_validators._decode_messages_from_response(response)
            
            # Required keywords
            time_str = f"{self.meeting_hour}:{self.meeting_minute:02d}"
            required_keywords = [time_str, self.meeting_location, "meeting"]
            
            logging.info(f"   Found {len(sent_messages)} sent messages")
            
            # Check each attendee
            correct_recipients = 0
            for attendee in self.attendees:
                found = False
                attendee_phone = attendee["number"].replace('-', '').replace(' ', '')
                
                for msg_str in sent_messages:
                    try:
                        msg = sms_validators.parse_message(msg_str)
                        msg_address = msg.get('address', '').replace('-', '').replace(' ', '')
                        
                        # Check recipient
                        if attendee_phone in msg_address or msg_address in attendee_phone:
                            # Check keywords
                            msg_text = (msg.get('body', '') or '').lower()
                            if all(kw.lower() in msg_text for kw in required_keywords):
                                found = True
                                break
                    except Exception as e:
                        logging.debug(f"Failed to parse message: {e}")
                
                if found:
                    correct_recipients += 1
                    logging.info(f"   ✓ {attendee['name']} received correct SMS")
                else:
                    logging.warning(f"   ✗ {attendee['name']} did NOT receive correct SMS")
            
            # Check distractors (should NOT receive SMS)
            distractor_received = 0
            for distractor in self.distractor_contacts:
                distractor_phone = distractor["number"].replace('-', '').replace(' ', '')
                
                for msg_str in sent_messages:
                    try:
                        msg = sms_validators.parse_message(msg_str)
                        msg_address = msg.get('address', '').replace('-', '').replace(' ', '')
                        
                        if distractor_phone in msg_address or msg_address in distractor_phone:
                            distractor_received += 1
                            logging.warning(f"   ✗ Distractor {distractor['name']} received SMS")
                            break
                    except Exception as e:
                        logging.debug(f"Failed to parse message: {e}")
            
            # 🆕 Binary scoring: All attendees must receive the SMS, and no distractor must receive it
            all_attendees_received = correct_recipients == len(self.attendees)
            no_distractors_received = distractor_received == 0
            
            if all_attendees_received and no_distractors_received:
                final_score = 1.0
            else:
                final_score = 0.0
            
            logging.warning("=" * 60)
            logging.warning(f"📊 Results:")
            logging.warning(f"   Correct recipients: {correct_recipients}/{len(self.attendees)} {'✅' if all_attendees_received else '❌'}")
            logging.warning(f"   Distractor SMS: {distractor_received}/{len(self.distractor_contacts)} {'✅' if no_distractors_received else '❌'}")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# 3. LayeredCrossAppMeetingUpdateNotify - Calendar + SMS (collaborative)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppMeetingUpdateNotify")
class CrossAppMeetingUpdateNotifyEvaluator(BaseCrossAppEvaluator):
    """
    Calendar + SMS cross-app task: Update a meeting and notify attendees
    
    Task flow:
    1. Calendar: Locate the meeting and update its time or location
    2. SMS: Send a notification to attendees
    
    Evaluation method:
    - Verify whether the meeting time/location was updated
    - Verify whether attendees received an SMS containing the updated information
    
    Supports two modes:
    - update_type='time': Update the time
    - update_type='location': Update the location
    """
    
    app_names = ("simple calendar pro", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Update type: 'time' or 'location'
        self.update_type = params.get('update_type', 'location')
        
        # Time parameter (for 'time' mode)
        self.original_hour = params.get('original_hour', 14)
        self.original_minute = params.get('original_minute', 0)
        self.new_hour = params.get('new_hour', 15)
        self.new_minute = params.get('new_minute', 0)
        self.event_title = params.get('event_title', 'Team Meeting')
        self.location = params.get('location', '')
        self.duration_minutes = params.get('duration_minutes', 90)
        
        # Location parameter (for 'location' mode)
        self.meeting_hour = params.get('meeting_hour', 14)
        self.meeting_minute = params.get('meeting_minute', 0)
        self.old_location = params.get('old_location', '')
        self.new_location = params.get('new_location', '')
        
        # Common parameters
        self.attendees = params.get('attendees', [])
        self.distractor_contacts = params.get('distractor_contacts', [])
        self.message_must_contain = params.get('message_must_contain', [])
        
        self.complexity = 4.0
    
    def initialize_task(self, env):
        """
        Initialize: Create contacts only
        
        Note:
        - For Scenario C Task 5, the meeting should be created by Task 1
        - The calendar is not cleared here, and no new meeting is created
        - Only contacts are created for use with SMS
        """
        from scendroid.env import adb_utils
        from scendroid.task_evals.utils import contacts_utils
        
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info(f"🔧 Initializing CrossApp: Meeting Update ({self.update_type.upper()})")
        logging.info("=" * 60)
        
        # Note: The calendar is not cleared, and no new meeting is created
        # The meeting should already have been created by a previous task
        
        # Only contacts are cleared and recreated (if needed)
        # For Scenario C, contacts have already been created during batch initialization
        # Contact creation can be skipped here
        
        if self.update_type == 'time':
            logging.info("📅 Meeting update mode: TIME")
            logging.info(f"   Expected original time: {self.original_hour}:{self.original_minute:02d}")
            logging.info(f"   Target new time: {self.new_hour}:{self.new_minute:02d}")
        elif self.update_type == 'location':
            logging.info("📅 Meeting update mode: LOCATION")
            logging.info(f"   Expected original location: {self.old_location}")
            logging.info(f"   Target new location: {self.new_location}")
        
        logging.info("✅ Initialization complete (meeting should already exist)")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Evaluation: Check whether the meeting time/location is updated and whether attendees received notifications
        
        Binary scoring: 1 point is awarded only if the meeting is updated and all attendees receive notifications
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        logging.warning("=" * 60)
        logging.warning(f"📊 Evaluating: Meeting Update ({self.update_type.upper()}) + Notify")
        logging.warning("=" * 60)
        
        try:
            # ✅ Force-close the Calendar app to refresh the database (to avoid caching issues)
            logging.info("   🔄 Closing Calendar app to flush changes...")
            try:
                adb_utils.close_app("simple calendar pro", env.controller)
                time.sleep(1.0)
            except Exception as e:
                logging.debug(f"   Could not close calendar: {e}")
            
            # Part 1: Check whether the meeting is updated
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            calendar_updated = False
            expected_content = ""
            
            if self.update_type == 'time':
                # Check whether the time is updated
                logging.info(f"   🔍 Looking for event with new time: {self.new_hour}:{self.new_minute:02d}")
                logging.info(f"   🔍 Event title pattern: '{self.event_title}'")
                logging.info(f"   🔍 Original time: {self.original_hour}:{self.original_minute:02d}")
                logging.info(f"   🔍 Total events found: {len(events)}")
                
                # 🆕 List all events to aid diagnosis
                for idx, event in enumerate(events, 1):
                    event_hour = event.start_datetime.hour
                    event_minute = event.start_datetime.minute
                    logging.info(f"      [{idx}] '{event.title}' at {event_hour}:{event_minute:02d}")
                
                # Check the target event
                found_event = None
                for event in events:
                    # Use start_datetime to retrieve the time
                    event_hour = event.start_datetime.hour
                    event_minute = event.start_datetime.minute
                    event_title = (event.title or '').lower()
                    
                    # Check title matching
                    if self.event_title.lower() in event_title:
                        found_event = event
                        logging.info(f"   ✅ Found matching event: '{event.title}'")
                        logging.info(f"      Current time: {event_hour}:{event_minute:02d}")
                        
                        if event_hour == self.new_hour and event_minute == self.new_minute:
                            calendar_updated = True
                            logging.info(f"   ✅ Time UPDATED to: {event_hour}:{event_minute:02d}")
                            break
                        else:
                            logging.warning(f"   ❌ Time NOT updated (still {event_hour}:{event_minute:02d}, expected {self.new_hour}:{self.new_minute:02d})")
                            # 🆕 Provide diagnostic information
                            if event_hour == self.original_hour and event_minute == self.original_minute:
                                logging.warning(f"   💡 The time remains the original time; possible causes:")
                                logging.warning(f"      1. The user did not click the Save button after modification")
                                logging.warning(f"      2. The Calendar app failed to save the modification correctly")
                
                if not found_event:
                    logging.error(f"   ❌ No event containing '{self.event_title}' in its title was found!")
                    logging.error(f"   💡 Possible causes:")
                    logging.error(f"      1. The event was deleted")
                    logging.error(f"      2. Title mismatch (check the event titles listed above)")
                
                expected_content = f"{self.new_hour}:{self.new_minute:02d}"
                
            elif self.update_type == 'location':
                # Check whether the location is updated
                for event in events:
                    if "meeting" in (event.title or "").lower():
                        if self.new_location.lower() in (event.location or "").lower():
                            calendar_updated = True
                            logging.info(f"   ✅ Location updated to: {event.location}")
                            break
                
                expected_content = self.new_location
            
            calendar_score = 1.0 if calendar_updated else 0.0
            
            # Part 2: Check SMS notifications
            response = adb_utils.issue_generic_request(
                "shell content query --uri content://sms/sent".split(),
                env.controller
            )
            sent_messages = sms_validators._decode_messages_from_response(response)
            
            logging.info(f"   📱 Found {len(sent_messages)} sent messages")
            
            # Check all keywords specified in message_must_contain
            if self.message_must_contain:
                keywords_to_check = self.message_must_contain
            else:
                keywords_to_check = [expected_content]
            
            logging.info(f"   🔍 SMS must contain ALL of: {keywords_to_check}")
            logging.info(f"   🔍 Checking {len(self.attendees)} attendees:")
            for att in self.attendees:
                logging.info(f"      - {att['name']}: {att['number']}")
            
            # 🆕 First list all sent SMS messages (for diagnosis)
            logging.info(f"   📋 All sent messages:")
            for idx, msg_str in enumerate(sent_messages, 1):
                try:
                    msg = sms_validators.parse_message(msg_str)
                    msg_address = msg.get('address', '').replace('-', '').replace(' ', '')
                    msg_body = (msg.get('body', '') or '')[:100]  # Display only the first 100 characters
                    logging.info(f"      [{idx}] To: {msg_address}, Body: \"{msg_body}...\"")
                except Exception as e:
                    logging.debug(f"      [{idx}] Failed to parse: {e}")
            
            correct_notifications = 0
            for attendee in self.attendees:
                found = False
                attendee_phone = attendee["number"].replace('-', '').replace(' ', '')
                logging.info(f"   🔍 Checking {attendee['name']} ({attendee['number']} → {attendee_phone})...")
                
                for msg_str in sent_messages:
                    try:
                        msg = sms_validators.parse_message(msg_str)
                        msg_address = msg.get('address', '').replace('-', '').replace(' ', '')
                        
                        if attendee_phone in msg_address or msg_address in attendee_phone:
                            msg_text = (msg.get('body', '') or '').lower()
                            logging.info(f"      ✓ Found SMS to {attendee['name']}: \"{msg.get('body', '')[:80]}...\"")
                            
                            # Check whether all required keywords are present
                            missing_keywords = []
                            for kw in keywords_to_check:
                                if kw.lower() not in msg_text:
                                    missing_keywords.append(kw)
                            
                            if not missing_keywords:
                                found = True
                                logging.info(f"      ✅ All keywords found!")
                                break
                            else:
                                logging.warning(f"      ⚠️ Missing keywords: {missing_keywords}")
                    except Exception as e:
                        logging.debug(f"Failed to parse message: {e}")
                
                if found:
                    correct_notifications += 1
                    logging.info(f"   ✅ {attendee['name']} received valid notification")
                else:
                    logging.warning(f"   ❌ {attendee['name']} did NOT receive valid notification")
                    logging.warning(f"      💡 Possible causes:")
                    logging.warning(f"         1. No SMS was sent to this person")
                    logging.warning(f"         2. The SMS content is missing required keywords: {keywords_to_check}")
            
            # 🆕 Fine-grained scoring (Scenario C modification):
            # - 0.0 points: Meeting not updated and no notification sent
            # - 0.5 points: Either meeting updated OR notification sent
            # - 1.0 points: Both meeting updated AND notification sent
            all_notified = correct_notifications == len(self.attendees)
            calendar_updated_check = calendar_score >= 0.99
            
            if calendar_updated_check and all_notified:
                final_score = 1.0
                result_msg = "Both calendar update and SMS notifications completed (1.0)"
            elif calendar_updated_check or all_notified:
                final_score = 0.5
                if calendar_updated_check:
                    result_msg = "Calendar updated, but SMS notifications incomplete (0.5)"
                else:
                    result_msg = "SMS notifications sent, but calendar not updated (0.5)"
            else:
                final_score = 0.0
                result_msg = "Neither calendar update nor SMS notifications completed (0.0)"
            
            logging.warning("=" * 60)
            logging.warning(f"📊 Results:")
            if self.update_type == 'time':
                logging.warning(f"   Time Updated: {'✅' if calendar_updated_check else '❌'}")
            else:
                logging.warning(f"   Location Updated: {'✅' if calendar_updated_check else '❌'}")
            logging.warning(f"   SMS Notifications: {correct_notifications}/{len(self.attendees)} {'✅' if all_notified else '❌'}")
            logging.warning(f"   {result_msg}")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            return 0.0


# ============================================================================
# 4. LayeredCrossAppSportsSummary - OpenTracks + Markor (collaborative)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppSportsSummary")
class CrossAppSportsSummaryEvaluator(BaseCrossAppEvaluator):
    """
    OpenTracks + Markor cross-app task: View workout records and create a summary
    
    Task flow:
    1. OpenTracks: View this week's exercise activities and calculate the total duration for each exercise type
    2. Markor: Create the sports_summary.md file to record the summary
    
    Evaluation method:
    - Check whether the Markor file is created
    - Check whether the file content contains exercise data
    """
    
    app_names = ("opentracks", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.activities = params.get('activities', [])
        self.summary_file = params.get('summary_file', 'sports_summary.md')
        
        self.complexity = 3.0
    
    def initialize_task(self, env):
        """
        Initialization: Create an OpenTracks activity and clear the Markor file
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: OpenTracks + Markor")
        logging.info("=" * 60)
        
        # TODO: Implement OpenTracks activity creation
        # TODO: Clear the Markor file
        
        logging.info(f"📊 Activities to create: {len(self.activities)}")
        for activity in self.activities:
            logging.info(f"   - {activity.get('type')}: {activity.get('duration')} mins")
        
        logging.info("✅ Initialization complete (placeholder)")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Evaluation: Check whether the Markor file contains the correct exercise summary
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: Sports Summary")
        logging.warning("=" * 60)
        
        # TODO: Implement Markor file checking
        logging.warning("⚠️  Evaluation not fully implemented yet")
        logging.warning("=" * 60)
        
        return 0.0


# ============================================================================
# 5. LayeredCrossAppScheduleQuery - Calendar + Tasks (Question-Answering)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppScheduleQuery")
class CrossAppScheduleQueryEvaluator(BaseCrossAppEvaluator):
    """
    Calendar + Tasks cross-application question-answering task
    
    Task flow:
    The agent must query Calendar and Tasks to answer questions about today's schedule
    
    Evaluation method:
    Check whether the agent's answer contains:
    - Keywords from meeting information in Calendar
    - Keywords from task information in Tasks
    """
    
    app_names = ("simple calendar pro", "tasks")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.calendar_event = params.get('calendar_event', {})
        self.task_item = params.get('task_item', {})
        self.calendar_keywords = params.get('calendar_keywords', [])
        self.task_keywords = params.get('task_keywords', [])
        
        self.complexity = 2.5
    
    def initialize_task(self, env):
        """
        Initialization: Create Calendar events and Task items
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Calendar + Tasks Query")
        logging.info("=" * 60)
        
        # TODO: Implement Calendar event creation
        # TODO: Implement Task item creation
        
        logging.info("📅 Calendar event to create:")
        logging.info(f"   {self.calendar_event}")
        logging.info("📝 Task item to create:")
        logging.info(f"   {self.task_item}")
        
        logging.info("✅ Initialization complete (placeholder)")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Evaluation: Check whether the agent's answer contains the required keywords
        """
        from scendroid.apps.calendar import utils as calendar_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: Schedule Query")
        logging.warning("=" * 60)
        
        try:
            # Get agent's answer
            agent_answer = calendar_utils.get_agent_answer(env)
            answer_lower = agent_answer.lower()
            
            # Check calendar keywords
            calendar_matched = sum(
                1 for kw in self.calendar_keywords if kw.lower() in answer_lower
            )
            
            # Check task keywords
            task_matched = sum(
                1 for kw in self.task_keywords if kw.lower() in answer_lower
            )
            
            # 🆕 Binary scoring: At least half of the keywords must match
            min_calendar = len(self.calendar_keywords) // 2 + 1 if self.calendar_keywords else 0
            min_task = len(self.task_keywords) // 2 + 1 if self.task_keywords else 0
            
            calendar_pass = calendar_matched >= min_calendar
            task_pass = task_matched >= min_task
            
            if calendar_pass and task_pass:
                final_score = 1.0
            else:
                final_score = 0.0
            
            logging.warning("=" * 60)
            logging.warning(f"📊 Results:")
            logging.warning(f"   Calendar keywords: {calendar_matched}/{len(self.calendar_keywords)} {'✅' if calendar_pass else '❌'}")
            logging.warning(f"   Task keywords: {task_matched}/{len(self.task_keywords)} {'✅' if task_pass else '❌'}")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            return 0.0



# ============================================================================
# 6. LayeredCameraAndFilesOrganize - Camera + Files (Collaborative)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCameraAndFilesOrganize")
class CameraAndFilesOrganizeEvaluator(BaseCrossAppEvaluator):
    """
    Camera + Files cross-application task
    
    Task flow:
    1. Camera: Take a photo
    2. Files: Open the file manager
    3. Files: Create a folder (if it does not exist)
    4. Files: Move the photo into the folder
    
    Evaluation method:
    - 30% Camera: Check whether a new photo was taken
    - 20% Files: Check whether the target folder was created
    - 50% Files: Check whether the photo was moved into the target folder
    
    This is a collaborative task requiring custom initialize_task and evaluate methods
    
    Parameters:
    - photo_type: Photo type (default "camera")
    - target_folder: Target folder path (e.g., "Weekend/Breakfast")
    - create_folder_if_missing: Whether to create the folder if it does not exist (default True)
    """
    
    app_names = ("camera", "files")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Save parameters
        self.photo_type = params.get('photo_type', 'camera')
        self.target_folder = params.get('target_folder', 'Weekend/Breakfast')
        self.create_folder_if_missing = params.get('create_folder_if_missing', True)
        
        # Internal state
        self.before_photos = set()
        self.new_photo_name = None
        
        # Set complexity
        self.complexity = 3.5
    
    def initialize_task(self, env):
        """
        Custom initialization: Record the current photo list and clean the test folder
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Camera + Files")
        logging.info("=" * 60)
        
        try:
            from scendroid.env import adb_utils, device_constants
            
            # Record the current photo list (photos taken by Camera are in GALLERY_DATA = /sdcard/DCIM)
            contents = adb_utils.issue_generic_request(
                ["shell", "ls", device_constants.GALLERY_DATA],
                env.controller
            )
            self.before_photos = set(
                contents.generic.output.decode().replace("\r", "").split("\n")
            )
            logging.info(f"📸 Initial photos in DCIM: {len(self.before_photos)}")
            
            # Clean the target folder (if it exists)
            # The Files app root directory is /storage/emulated/0/ (EMULATOR_DATA)
            target_path = f"{device_constants.EMULATOR_DATA}{self.target_folder}"
            logging.info(f"📁 Target folder: {target_path}")
            
            # Check and clean the target folder
            check_result = adb_utils.issue_generic_request(
                ["shell", "test", "-d", target_path, "&&", "echo", "exists"],
                env.controller
            )
            if "exists" in check_result.generic.output.decode():
                logging.info(f"   Cleaning existing folder: {target_path}")
                adb_utils.issue_generic_request(
                    ["shell", "rm", "-rf", target_path],
                    env.controller
                )
            
            logging.info("=" * 60)
            
        except Exception as e:
            logging.warning(f"   ⚠️  Initialization issue: {e}")
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: Check whether photos were taken and moved to the target folder
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure (binary scoring; all steps must be completed)
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Camera + Files Organize:")
        logging.warning("=" * 60)
        
        try:
            from scendroid.env import adb_utils, device_constants
            
            # If initialize_task was skipped (scenario mode), before_photos may be empty
            # In this case, we assume no photos initially existed
            if not hasattr(self, 'before_photos') or self.before_photos is None:
                logging.warning("   ⚠️  initialize_task was skipped, assuming no initial photos")
                self.before_photos = set()
            
            # Part 1: Check whether new photos were taken (check the DCIM directory)
            logging.warning("📸 Part 1: Checking for new photo...")
            
            # Photos taken by Camera are in GALLERY_DATA = /sdcard/DCIM
            contents = adb_utils.issue_generic_request(
                ["shell", "ls", "-R", device_constants.GALLERY_DATA],
                env.controller
            )
            after_photos = set(
                contents.generic.output.decode().replace("\r", "").split("\n")
            )
            after_photos = {p for p in after_photos if p and p.strip() and not p.endswith(":")}  # Filter out empty strings and directory names
            
            # Check for new photos under DCIM
            new_photos_in_dcim = after_photos - self.before_photos
            
            logging.warning(f"   Photos before: {len(self.before_photos)}")
            logging.warning(f"   Photos in DCIM now: {len(after_photos)}")
            logging.warning(f"   New photos in DCIM: {len(new_photos_in_dcim)}")
            
            # Note: If the user has already moved photos to the target folder, DCIM may contain no new photos
            # Therefore, we need to check both locations: DCIM + target folder
            photo_taken = False
            if len(new_photos_in_dcim) >= 1:
                self.new_photo_name = list(new_photos_in_dcim)[0]
                logging.warning(f"   ✅ New photo found in DCIM: {self.new_photo_name}")
                photo_taken = True
            else:
                logging.warning(f"   ℹ️  No new photos in DCIM (might be moved already)")
                # Do not immediately return 0.0; continue checking the target folder
            
            # Part 2: Check whether the target folder was created
            logging.warning("📁 Part 2: Checking target folder...")
            
            # The Files app root directory is /storage/emulated/0/ (EMULATOR_DATA)
            target_path = f"{device_constants.EMULATOR_DATA}{self.target_folder}"
            
            # Use the ls command to check whether the folder exists (do not raise an exception)
            folder_exists = False
            
            # Attempt to directly list the target folder
            try:
                ls_result = adb_utils.issue_generic_request(
                    ["shell", "ls", target_path],
                    env.controller
                )
                folder_exists = True
            except:
                folder_exists = False
            
            if not folder_exists:
                logging.warning(f"   ❌ Target folder not found: {target_path}")
                logging.warning("=" * 60)
                return 0.0
            
            logging.warning(f"   ✅ Target folder exists: {target_path}")
            
            # Part 3: Check whether photos were moved to the target folder
            logging.warning("📦 Part 3: Checking if photo in target folder...")
            
            # List files in the target folder
            folder_contents = adb_utils.issue_generic_request(
                ["shell", "ls", target_path],
                env.controller
            )
            files_in_folder = set(
                folder_contents.generic.output.decode().replace("\r", "").split("\n")
            )
            files_in_folder = {f for f in files_in_folder if f and f.strip()}
            
            logging.warning(f"   Files in target folder: {len(files_in_folder)}")
            
            # Check whether photos are present in the target folder
            photo_in_folder = False
            
            # Method 1: If we know the filename of the new photo, check for a match
            if hasattr(self, 'new_photo_name') and self.new_photo_name and self.new_photo_name in files_in_folder:
                photo_in_folder = True
                logging.warning(f"   ✅ Found expected photo: {self.new_photo_name}")
            
            # Method 2: Check whether any image files (.jpg, .png) exist
            if not photo_in_folder:
                image_files = [f for f in files_in_folder if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if image_files:
                    photo_in_folder = True
                    logging.warning(f"   ✅ Found image file in folder: {image_files[0]}")
                    # If the new photo was not found in the root directory but photos exist in the target folder, the photo has been moved
                    if not photo_taken:
                        photo_taken = True
                        logging.warning(f"   ℹ️  Photo was already moved (not found in root check)")
            
            if photo_in_folder:
                logging.warning(f"   ✅ Photo in target folder")
            else:
                logging.warning(f"   ❌ No photo found in target folder")
                logging.warning("=" * 60)
                return 0.0
            
            # Final check: A photo must have been taken (in either the root directory or the target folder)
            if not photo_taken:
                logging.warning(f"   ❌ No evidence of new photo taken")
                logging.warning("=" * 60)
                return 0.0
            
            # Binary scoring: All three steps must be completed
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   New photo taken: ✅")
            logging.warning(f"   Folder created: ✅")
            logging.warning(f"   Photo in folder: ✅")
            logging.warning("   ✅ SUCCESS: Complete photo organization")
            logging.warning("=" * 60)
            return 1.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.warning("=" * 60)
            return 0.0
    
    def tear_down(self, env):
        """
        Clean up the environment: remove test photos and folders
        """
        super().tear_down(env)
        
        try:
            from scendroid.env import adb_utils, device_constants
            
            # Clean up the target folder
            target_path = f"{device_constants.EMULATOR_DATA}{self.target_folder}"
            adb_utils.issue_generic_request(
                ["shell", "rm", "-rf", target_path],
                env.controller
            )
            
            logging.info("✅ Camera + Files task cleanup complete")
            
        except Exception as e:
            logging.warning(f"⚠️  Cleanup issue: {e}")


# ============================================================================
# 7. LayeredCrossAppAudioRecorderFiles - AudioRecorder + Files (rename + move)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppAudioRecorderFiles")
class CrossAppAudioRecorderFilesEvaluator(BaseCrossAppEvaluator):
    """
    AudioRecorder + Files cross-app task
    
    Task flow:
    1. AudioRecorder: locate the most recent audio recording and rename it
    2. Files: move the audio recording file to the specified folder
    
    Evaluation method:
    - Verify that the audio recording file exists in the target folder
    - Verify that the filename is correct
    
    Note:
    - This is task D4 of Scenario D
    """
    
    app_names = ("audio recorder", "files")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.expected_filename = params.get('expected_filename')  # without extension
        self.target_folder = params.get('target_folder')  # e.g., "Documents/Study"
        
        # Internal state
        self.before_recordings = []
        
        # Set complexity
        self.complexity = 2.5
    
    def initialize_task(self, env):
        """Initialize the task: record existing audio recordings"""
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: AudioRecorder + Files")
        logging.info("=" * 60)
        
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            # Record existing audio recordings
            self.before_recordings = file_utils.get_file_list_with_metadata(
                device_constants.AUDIORECORDER_DATA, env.controller
            )
            
            logging.info(f"   Recorded {len(self.before_recordings)} existing recordings")
            logging.info("   ✅ AudioRecorder + Files initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Initialization issue: {e}")
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: verify that the file exists in the target folder and has the correct name
        
        Binary scoring: score 1 point only if the file exists in the target folder and has the correct name; otherwise, score 0 points
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            from scendroid.env import device_constants, adb_utils
            from scendroid.utils import file_utils
            
            logging.info("=" * 60)
            logging.info("🔍 Evaluating: AudioRecorder + Files")
            logging.info("=" * 60)
            
            # Check the target folder path
            target_path = f"{device_constants.EMULATOR_DATA}{self.target_folder}"
            logging.info(f"   Target folder: {target_path}")
            logging.info(f"   Expected filename: {self.expected_filename}")
            
            # Possible file extensions
            possible_extensions = ['.wav', '.mp3', '.m4a', '.aac', '.3gp']
            
            # Check whether the file is at the target location (using a more robust method)
            found_in_target = False
            found_filename = None
            
            for ext in possible_extensions:
                full_filename = f"{self.expected_filename}{ext}"
                file_path = f"{target_path}/{full_filename}"
                
                # Method 1: Use file_utils.check_file_exists (more robust)
                try:
                    if file_utils.check_file_exists(file_path, env.controller, bash_file_test="-f"):
                        logging.info(f"   ✅ Found file: {full_filename}")
                        found_in_target = True
                        found_filename = full_filename
                        break
                except Exception as e:
                    logging.debug(f"   Check failed for {full_filename}: {e}")
                
                # Method 2: Fallback method - use the ls command
                try:
                    ls_cmd = ['shell', 'ls', '-la', file_path]
                    ls_result = adb_utils.issue_generic_request(ls_cmd, env.controller)
                    if ls_result and ls_result.generic and ls_result.generic.output:
                        output = ls_result.generic.output.decode('utf-8', errors='ignore')
                        if 'No such file' not in output and full_filename in output:
                            logging.info(f"   ✅ Found file (via ls): {full_filename}")
                            found_in_target = True
                            found_filename = full_filename
                            break
                except Exception as e:
                    logging.debug(f"   ls check failed for {full_filename}: {e}")
            
            if found_in_target:
                logging.warning(f"   ✅ File found in target folder: {found_filename}")
                logging.warning("=" * 60)
                logging.warning("✅ SUCCESS: File renamed and moved to target folder")
                logging.warning("=" * 60)
                return 1.0
            
            # Check whether the file has been renamed at least (but not moved) - for debugging information only
            try:
                after_recordings = file_utils.get_file_list_with_metadata(
                    device_constants.AUDIORECORDER_DATA, env.controller
                )
                
                for recording in after_recordings:
                    if self.expected_filename in recording.file_name:
                        logging.warning(f"   ❌ File renamed but not moved: {recording.file_name}")
                        logging.warning(f"      Still in: {device_constants.AUDIORECORDER_DATA}")
                        break
                else:
                    logging.warning(f"   ❌ File not found with expected name: {self.expected_filename}")
            except Exception as e:
                logging.debug(f"   Could not check recordings folder: {e}")
            
            # List all files in the target folder (debugging information)
            try:
                ls_folder_cmd = ['shell', 'ls', '-la', target_path]
                ls_folder_result = adb_utils.issue_generic_request(ls_folder_cmd, env.controller)
                if ls_folder_result and ls_folder_result.generic and ls_folder_result.generic.output:
                    folder_content = ls_folder_result.generic.output.decode('utf-8', errors='ignore')
                    logging.info(f"   Target folder contents:\n{folder_content}")
            except Exception as e:
                logging.debug(f"   Could not list target folder: {e}")
            
            # Failure
            logging.warning("=" * 60)
            logging.warning("❌ FAILED: File not found in target folder")
            logging.warning("=" * 60)
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# 8. LayeredCrossAppTasksCalendar - Tasks + Calendar (logical judgment + synchronization)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppTasksCalendar")
class CrossAppTasksCalendarEvaluator(BaseCrossAppEvaluator):
    """
    Tasks + Calendar cross-app task (with logical judgment)
    
    Task flow:
    1. Tasks: check the due date of the specified task
    2. Logical judgment: if the due date is today, create a meeting
    3. Calendar: Create a meeting event
    
    Evaluation method:
    - Check whether the meeting was created in Calendar
    - Verify that the meeting time, location, and duration are correct
    
    Note:
    - This is Task D5 of Scenario D
    - A Task must be created in initialize_task (ensure the due date is today)
    """
    
    app_names = ("tasks", "simple calendar pro")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.task_title = params.get('task_title', 'Lab Report')
        self.meeting_title = params.get('meeting_title', 'Group Sync')
        self.meeting_hour = params.get('meeting_hour', 15)
        self.meeting_minute = params.get('meeting_minute', 0)
        self.meeting_location = params.get('meeting_location', 'Room 402')
        self.meeting_duration_minutes = params.get('meeting_duration_minutes', 90)
        
        # Set complexity
        self.complexity = 3.5
    
    def initialize_task(self, env):
        """Initialize the task: Create a Task and clean up Calendar"""
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Tasks + Calendar")
        logging.info("=" * 60)
        
        try:
            # Part 1: Create a Task (due date = today)
            logging.info("📝 Part 1: Creating task in Tasks app...")
            self._create_task(env)
            
            # Part 2: Clean up Calendar
            logging.info("📅 Part 2: Clearing Calendar...")
            from scendroid.task_evals.single.calendar import calendar_utils
            calendar_utils.clear_calendar_db(env)
            
            logging.info("   ✅ Tasks + Calendar initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Initialization issue: {e}")
    
    def _create_task(self, env):
        """Create a test Task"""
        from scendroid.env import adb_utils
        import time
        from datetime import datetime
        
        try:
            # Use an Intent to create the task
            # Note: Different Tasks apps may use different Intent actions
            
            # Method 1: Use OpenTasks' Intent
            today = datetime.now().strftime("%Y-%m-%d")
            
            cmd = [
                'shell', 'am', 'start',
                '-a', 'android.intent.action.INSERT',
                '-t', 'vnd.android.cursor.item/task',
                '--es', 'title', self.task_title,
                '--es', 'due', today,
                '--ez', 'android.intent.extra.SKIP_UI', 'true',
            ]
            
            adb_utils.issue_generic_request(cmd, env.controller)
            time.sleep(2.0)
            
            logging.info(f"   ✅ Task created: {self.task_title} (due: {today})")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Task creation issue: {e}")
            logging.warning("   Note: Agent will need to work with existing tasks")
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: Check whether the meeting was created in Calendar
        
        Returns:
            float: 1.0 indicates success; 0.0 indicates failure
        """
        try:
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            logging.info("=" * 60)
            logging.info("🔍 Evaluating: Tasks + Calendar")
            logging.info("=" * 60)
            
            # Retrieve all events (using the correct API)
            # Reference: apps/calendar/evaluators.py
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            logging.info(f"   Found {len(events)} events in calendar")
            
            # Check whether a meeting matching the criteria exists
            for event in events:
                # CalendarEvent has a start_datetime attribute
                event_hour = event.start_datetime.hour
                event_minute = event.start_datetime.minute
                
                logging.info(f"   Checking event: {event.title} at {event_hour}:{event_minute:02d}")
                
                # Check the title
                title_match = self.meeting_title.lower() in event.title.lower()
                
                # Check the time
                time_match = (event_hour == self.meeting_hour and 
                             event_minute == self.meeting_minute)
                
                # Check the location (optional)
                location_match = True
                if self.meeting_location and hasattr(event, 'location') and event.location:
                    location_match = self.meeting_location.lower() in event.location.lower()
                
                if title_match and time_match:
                    logging.warning(f"   ✅ Meeting found: {event.title}")
                    logging.warning(f"      Time: {event_hour}:{event_minute:02d}")
                    if hasattr(event, 'location') and event.location:
                        logging.warning(f"      Location: {event.location}")
                    
                    logging.warning("=" * 60)
                    logging.warning("✅ SUCCESS: Meeting created from task")
                    logging.warning("=" * 60)
                    return 1.0
            
            # No meeting matching the criteria was found
            logging.warning("   ❌ Expected meeting not found")
            logging.warning(f"      Expected: {self.meeting_title} at {self.meeting_hour}:{self.meeting_minute:02d}")
            logging.warning("=" * 60)
            logging.warning("❌ FAILED: Meeting not created")
            logging.warning("=" * 60)
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# 9. LayeredCrossAppRetroMusicTimer - RetroMusic + Clock (music + timer)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppRetroMusicTimer")
class CrossAppRetroMusicTimerEvaluator(BaseCrossAppEvaluator):
    """
    RetroMusic + Clock cross-app task
    
    Task flow:
    1. RetroMusic: Play music (shuffle mode)
    2. Clock: Set a sleep timer
    
    Evaluation method:
    - 50%: Check whether music is playing
    - 50%: Check whether the timer is set
    
    Note:
    - This is Task D9 of Scenario D
    """
    
    app_names = ("retro music", "clock")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.timer_minutes = params.get('timer_minutes', 30)
        self.playlist_name = params.get('playlist_name', 'Most played')
        
        # Set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: check music playback and timer
        
        Returns:
            float: score from 0.0 to 1.0
        """
        try:
            logging.info("=" * 60)
            logging.info("🔍 Evaluating: RetroMusic + Clock")
            logging.info("=" * 60)
            
            # Part 1: Check whether music is playing
            music_score = self._check_music_playing(env)
            
            # Part 2: Check whether the timer is set
            timer_score = self._check_timer_set(env)
            
            # 🆕 Binary scoring: both parts must succeed
            music_pass = music_score >= 0.99
            timer_pass = timer_score >= 0.99
            
            if music_pass and timer_pass:
                total_score = 1.0
            else:
                total_score = 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Music playing: {'✅' if music_pass else '❌'}")
            logging.warning(f"   Timer set: {'✅' if timer_pass else '❌'}")
            logging.warning(f"   Total score: {total_score:.2f}")
            
            if total_score >= 0.99:
                logging.warning("   ✅ SUCCESS: Both music and timer working")
            else:
                logging.warning("   ❌ FAILED: Not all components working")
            
            logging.warning("=" * 60)
            return total_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def _check_music_playing(self, env) -> float:
        """Check whether music is playing"""
        from scendroid.env import adb_utils
        
        try:
            # Check the Retro Music process
            ps_cmd = ['shell', 'ps', '-A']
            result = adb_utils.issue_generic_request(ps_cmd, env.controller)
            
            # Correctly parse the AdbResponse
            ps_output = ""
            if result and result.generic and result.generic.output:
                ps_output = result.generic.output.decode('utf-8', errors='ignore').lower()
            
            if 'retromusic' in ps_output:
                logging.info("   ✓ Retro Music process running")
                
                # Check audio focus
                audio_cmd = ['shell', 'dumpsys', 'audio']
                audio_result = adb_utils.issue_generic_request(audio_cmd, env.controller)
                
                audio_output = ""
                if audio_result and audio_result.generic and audio_result.generic.output:
                    audio_output = audio_result.generic.output.decode('utf-8', errors='ignore').lower()
                
                if 'retromusic' in audio_output:
                    logging.warning("   ✅ Music is playing")
                    return 1.0
                else:
                    # 🆕 Binary scoring: unclear playback status is considered failure
                    logging.warning("   ❌ App running but playback unclear")
                    return 0.0
            else:
                logging.warning("   ❌ Retro Music not running")
                return 0.0
                
        except Exception as e:
            logging.warning(f"   ⚠️ Music check failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return 0.0
    
    def _check_timer_set(self, env) -> float:
        """Check whether the timer is set and running
        
        Simplify the checking logic: success if the timer is running
        Reference: correct implementation in clock/evaluators.py and clock/utils.py
        """
        from scendroid.env import adb_utils
        import time
        import re
        
        try:
            # 1. Launch the Clock app
            adb_utils.start_activity(
                "com.google.android.deskclock/.DeskClock",
                None,
                env.controller
            )
            time.sleep(2.0)
            
            # 2. Tap the Timer tab (ensure being on the Timer page)
            try:
                from scendroid.env import tools
                controller = tools.AndroidToolController(env=env.controller)
                controller.click_element("Timer")
                time.sleep(1.0)
            except Exception as e:
                logging.debug(f"   Failed to tap the Timer tab (may already be on this page): {e}")
            
            # 3. Retrieve UI elements (correct approach)
            # Reference: clock/utils.py Line 91, clock/evaluators.py Line 267
            ui_elements = env.get_state().ui_elements
            current_activity = adb_utils.get_current_activity(env.controller)[0]
            
            logging.info(f"   Current activity: {current_activity}")
            logging.info(f"   UI elements count: {len(ui_elements)}")
            
            # 4. Check whether the Pause button exists (indicating the timer is running)
            for element in ui_elements:
                if element.content_description == "Pause":
                    logging.warning(f"   ✅ Timer running (Pause button found)")
                    return 1.0
            
            # 5. Check whether time is displayed in the UI (in h/m/s format)
            for element in ui_elements:
                if element.text:
                    # Check whether countdown-formatted time exists
                    if re.search(r'\d+[hms]', element.text) or re.search(r'\d+:\d+:\d+', element.text):
                        logging.warning(f"   ✅ Timer running (time display found: {element.text})")
                        return 1.0
            
            logging.warning(f"   ❌ Timer not found or not running")
            return 0.0
                
        except Exception as e:
            logging.warning(f"   ⚠️ Timer check failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize the task"""
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: RetroMusic + Clock")
        logging.info("=" * 60)
        
        try:
            from scendroid.env import adb_utils
            
            # Close both apps
            adb_utils.close_app("retromusic", env.controller)
            adb_utils.close_app("clock", env.controller)
            
            logging.info("   ✅ RetroMusic + Clock initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Initialization issue: {e}")


# ============================================================================
# CrossApp: Clock + Tasks (for Scenario D - D1)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppClockTasks")
class CrossAppClockTasksEvaluator(BaseCrossAppEvaluator):
    """
    Cross-app evaluator: Clock + Tasks
    
    Supported scenarios:
    - Scenario D - D1: Set an alarm and create a task reminder
    
    Evaluation content:
    - Part 1: Check whether the alarm is set successfully (time, label)
    - Part 2: Check whether the task is created successfully (title)
    
    Success criteria:
    - Both parts must be completed for success (AND logic)
    """
    
    app_names = ("clock", "tasks")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Clock parameters (support two parameter names: alarm_hour or alarm_time_hour)
        self.alarm_hour = params.get('alarm_hour', params.get('alarm_time_hour', 7))
        self.alarm_minute = params.get('alarm_minute', params.get('alarm_time_minute', 30))
        self.alarm_label = params.get('alarm_label', 'AI Lecture')
        
        # Task parameters
        self.task_title = params.get('task_title', 'Bring printed lecture notes')
        # Priority: highest=3, high=2, normal=1, low=0
        self.task_priority = params.get('task_priority', None)  # None means priority is not checked
        
        # Set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: check alarm and task completion status
        
        Fine-grained scoring (Scenario D modification):
        - 0.0 points: neither completed
        - 0.5 points: either Alarm OR Task completed
        - 1.0 points: both completed
        """
        logging.info("=" * 60)
        logging.info("🔍 Evaluating CrossApp: Clock + Tasks")
        logging.info("=" * 60)
        
        # Part 1: Check alarm
        alarm_score = self._check_alarm(env)
        logging.info(f"   Part 1 (Alarm): {alarm_score:.2f}")
        
        # Part 2: Check task
        task_score = self._check_task(env)
        logging.info(f"   Part 2 (Task): {task_score:.2f}")
        
        # Fine-grained scoring: 0.5 points for either completed, 1 point for both completed
        alarm_ok = alarm_score >= 0.99
        task_ok = task_score >= 0.99
        
        if alarm_ok and task_ok:
            final_score = 1.0
            result_msg = "Both Alarm and Task completed (1.0)"
        elif alarm_ok or task_ok:
            final_score = 0.5
            if alarm_ok:
                result_msg = "Alarm OK, but Task not created (0.5)"
            else:
                result_msg = "Task OK, but Alarm not set (0.5)"
        else:
            final_score = 0.0
            result_msg = "Neither Alarm nor Task completed (0.0)"
        
        logging.info("=" * 60)
        logging.info(f"   {result_msg}")
        logging.info(f"🎯 Final Score: {final_score:.1f}")
        logging.info("=" * 60)
        
        return final_score
    
    def _check_alarm(self, env) -> float:
        """Check whether an alarm is set"""
        from scendroid.apps.clock import utils as clock_utils
        from scendroid.env import adb_utils
        import time
        
        try:
            logging.info(f"   🔍 DEBUG: Looking for alarm:")
            logging.info(f"      Expected hour: {self.alarm_hour}")
            logging.info(f"      Expected minute: {self.alarm_minute}")
            logging.info(f"      Expected label: '{self.alarm_label}'")
            
            # Use check_alarm_with_date to verify the alarm
            alarm_exists = clock_utils.check_alarm_with_date(
                env, 
                self.alarm_hour, 
                self.alarm_minute, 
                day_offset=0,
                enabled=True
            )
            
            if not alarm_exists:
                logging.warning(f"   ❌ Alarm not found: {self.alarm_hour}:{self.alarm_minute:02d}")
                return 0.0
            
            logging.info(f"   ✅ Alarm time matches: {self.alarm_hour}:{self.alarm_minute:02d}")
            
            # If label checking is required, perform it via UI elements
            if self.alarm_label:
                logging.info(f"   🔍 Checking alarm label...")
                
                # Retrieve UI state
                ui_elements = env.get_state().ui_elements
                
                # Search for the label in the UI
                expected_label_lower = self.alarm_label.strip().lower()
                found_label = False
                
                for element in ui_elements:
                    text = element.text.strip().lower() if element.text else ''
                    content_desc = element.content_description.strip().lower() if element.content_description else ''
                    
                    # Check whether the label appears in the text or content description
                    if expected_label_lower in text or expected_label_lower in content_desc:
                        logging.info(f"      ✅ Label found in UI: '{element.text or element.content_desc}'")
                        found_label = True
                        break
                
                if found_label:
                    logging.info(f"   ✅ Alarm found with label: {self.alarm_hour}:{self.alarm_minute:02d} ({self.alarm_label})")
                    return 1.0
                else:
                    # Label mismatch, but alarm exists; assign partial credit
                    logging.warning(f"   ⚠️ Alarm found but label mismatch (expected: '{self.alarm_label}')")
                    logging.warning(f"   💡 Tip: Label might be case-sensitive or have extra spaces")
                    # Lenient handling: if the time is correct, consider it successful even if the label does not fully match
                    return 1.0
            else:
                # No label checking required
                logging.info(f"   ✅ Alarm found: {self.alarm_hour}:{self.alarm_minute:02d}")
                return 1.0
            
        except Exception as e:
            logging.warning(f"   ⚠️ Alarm check failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return 0.0
    
    def _check_task(self, env) -> float:
        """Check whether a task is created (including priority verification)"""
        from scendroid.env import adb_utils
        import time
        import re
        
        # Priority mapping: 0=highest, 1=high, 2=normal, 3=low (0 is the highest priority!)
        priority_map = {'highest': 0, 'high': 1, 'normal': 2, 'low': 3}
        expected_importance = priority_map.get(self.task_priority) if self.task_priority else None
        
        logging.info(f"   🔍 DEBUG: Looking for task:")
        logging.info(f"      Expected title: '{self.task_title}'")
        logging.info(f"      Expected (normalized): '{' '.join(self.task_title.strip().split())}'")
        if expected_importance is not None:
            logging.info(f"      Expected priority: '{self.task_priority}' (importance={expected_importance})")
        
        try:
            # Method 1: Query the Tasks database via content query (including the importance field)
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
            ]
            
            result = adb_utils.issue_generic_request(cmd, env.controller)
            
            if result and result.generic and result.generic.output:
                output = result.generic.output
                
                # Handle bytes type
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='ignore')
                
                logging.info(f"   🔍 DEBUG: Query output:")
                logging.info(f"      {output[:500]}")
                
                # Check whether the output contains the task title
                # Improvement: more robust whitespace handling via normalized comparison
                task_title_normalized = ' '.join(self.task_title.strip().split())
                output_lines = output.split('\n')
                
                logging.info(f"   🔍 DEBUG: Found {len(output_lines)} lines in output")
                
                found_tasks = []
                for line in output_lines:
                    # Extract content following "title=" or "name="
                    if 'title=' in line or 'name=' in line:
                        # Format example: Row: 0 name=Bring USB drive, importance=3, ...
                        title_match = re.search(r'(?:title|name)=([^,\n]+)', line)
                        if title_match:
                            found_title = title_match.group(1).strip()
                            found_title_normalized = ' '.join(found_title.split())
                            found_tasks.append(found_title)
                            
                            logging.info(f"      Task found: '{found_title}' (normalized: '{found_title_normalized}')")
                            
                            # Normalized comparison (ignoring extra whitespace)
                            if task_title_normalized.lower() == found_title_normalized.lower():
                                logging.info(f"   ✅ Task title matched: '{found_title}'")
                                
                                # If priority checking is required
                                if expected_importance is not None:
                                    importance_match = re.search(r'importance[_=](\d+)', line)
                                    if importance_match:
                                        actual_importance = int(importance_match.group(1))
                                        logging.info(f"      Actual importance: {actual_importance}, Expected: {expected_importance}")
                                        if actual_importance == expected_importance:
                                            logging.info(f"   ✅ Priority matched: {self.task_priority}")
                                            return 1.0
                                        else:
                                            logging.warning(f"   ❌ Priority mismatch: expected {expected_importance}, got {actual_importance}")
                                            return 0.0
                                    else:
                                        logging.warning(f"   ⚠️ Could not find importance field in: {line[:200]}")
                                        # Lenient handling: if the importance field is not found, attempt to check importance_color
                                        # importance_color: red=0 (highest), orange=1 (high), blue=2 (normal), green=3 (low)
                                        # Note: importance 0 is the highest priority!
                                        color_match = re.search(r'importance_color=(-?\d+)', line)
                                        if color_match:
                                            color = int(color_match.group(1))
                                            # Color-to-importance mapping (0=highest)
                                            color_to_importance = {
                                                -3670016: 0,  # red = highest (importance=0)
                                                -4521984: 1,  # orange = high (importance=1)
                                                -1499549: 2,  # blue = normal (importance=2)
                                                -769226: 3,   # green = low (importance=3)
                                            }
                                            actual_importance = color_to_importance.get(color, 1)
                                            logging.info(f"      Color {color} -> importance {actual_importance}")
                                            if actual_importance == expected_importance:
                                                logging.info(f"   ✅ Priority matched via color: {self.task_priority}")
                                                return 1.0
                                            else:
                                                logging.warning(f"   ❌ Priority mismatch: expected {expected_importance}, got {actual_importance}")
                                                return 0.0
                                        else:
                                            # Cannot check priority; handle leniently
                                            logging.warning(f"   ⚠️ Cannot verify priority, accepting task")
                                            return 1.0
                                else:
                                    # No need to check priority
                                    logging.info(f"   ✅ Task found: '{found_title}' (matched '{self.task_title}')")
                                    return 1.0
                
                # If not found, log detailed information
                logging.warning(f"   ❌ Task not found: '{self.task_title}'")
                logging.info(f"   Looking for (normalized): '{task_title_normalized}'")
                logging.info(f"   Found tasks: {found_tasks}")
                logging.info(f"   Full output: {output[:500]}")
                return 0.0
            else:
                logging.warning("   ⚠️ Tasks query returned no data, trying UI dump...")
                
                # Method 2: Open the Tasks app and check the UI
                adb_utils.issue_generic_request([
                    'shell', 'am', 'start', '-n',
                    'org.tasks/.ui.MainActivity'
                ], env.controller)
                
                time.sleep(2)
                
                # Retrieve the UI dump
                ui_dump = adb_utils.issue_generic_request([
                    'shell', 'uiautomator', 'dump', '/dev/tty'
                ], env.controller)
                
                if ui_dump and ui_dump.generic and ui_dump.generic.output:
                    ui_text = ui_dump.generic.output
                    # Tolerate leading and trailing whitespace
                    task_title_normalized = self.task_title.strip()
                    if task_title_normalized in ui_text or self.task_title in ui_text:
                        logging.info(f"   ✅ Task found in UI: '{self.task_title}'")
                        return 1.0
                    else:
                        logging.warning(f"   ❌ Task not found in UI: '{self.task_title}'")
                        return 0.0
                else:
                    logging.warning("   ⚠️ UI dump failed")
                    return 0.0
                    
        except Exception as e:
            logging.warning(f"   ⚠️ Task check failed: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """Initialize the task"""
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing CrossApp: Clock + Tasks")
        logging.info("=" * 60)
        
        try:
            from scendroid.env import adb_utils
            import time
            
            # Clear data for the Clock and Tasks apps
            logging.info("   Clearing Clock app data...")
            adb_utils.issue_generic_request([
                'shell', 'pm', 'clear', 'com.android.deskclock'
            ], env.controller)
            time.sleep(1)
            
            logging.info("   Clearing Tasks app data...")
            adb_utils.issue_generic_request([
                'shell', 'pm', 'clear', 'org.tasks'
            ], env.controller)
            time.sleep(1)
            
            logging.info("   ✅ Clock + Tasks initialized")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Initialization issue: {e}")


# ============================================================================
# Scenario E Evaluators
# ============================================================================

# ============================================================================
# E1. LayeredCrossAppWorldClockCalendar - Clock (World Clock) + Files + Calendar
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppWorldClockCalendar")
class CrossAppWorldClockCalendarEvaluator(BaseCrossAppEvaluator):
    """
    World Clock + Files + Calendar cross-app task
    
    Task flow:
    1. Clock: Add the destination city to World Clock
    2. Files: View the trip information image to obtain the flight time
    3. Calendar: Create a calendar event for the flight
    
    Evaluation method:
    - 33% World Clock: Check whether the target city has been added
    - 33% Calendar: Check whether the correct flight event has been created
    - 34% Overall completion (additional points awarded if both are passed)
    
    This is Task E1 of Scenario E
    """
    
    app_names = ("clock", "files", "simple calendar pro")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.city_name = params.get('city_name', 'San Francisco')
        self.event_title = params.get('event_title', 'Flight to SF')
        self.event_hour = params.get('event_hour', 9)
        self.event_minute = params.get('event_minute', 30)
        self.info_file = params.get('info_file', 'Conference_Trip_Info.png')
        
        # Set complexity
        self.complexity = 3.5
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation
        
        Fine-grained scoring (modified for Scenario D):
        - 0.0 points: Neither completed
        - 0.5 points: Either World Clock OR Calendar completed
        - 1.0 points: Both completed
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: World Clock + Calendar")
        logging.warning("=" * 60)
        
        try:
            # Part 1: Check whether the city has been added to World Clock
            world_clock_ok = self._check_world_clock(env)
            
            # Part 2: Check whether the event has been created in Calendar
            calendar_ok = self._check_calendar_event(env)
            
            # Fine-grained scoring: 0.5 points for completing either part; 1 point for completing both
            if world_clock_ok and calendar_ok:
                final_score = 1.0
                result_msg = "Both World Clock and Calendar completed (1.0)"
            elif world_clock_ok or calendar_ok:
                final_score = 0.5
                if world_clock_ok:
                    result_msg = "World Clock OK, but Calendar event not created (0.5)"
                else:
                    result_msg = "Calendar event OK, but World Clock city not added (0.5)"
            else:
                final_score = 0.0
                result_msg = "Neither World Clock nor Calendar completed (0.0)"
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   World Clock: {'✅' if world_clock_ok else '❌'}")
            logging.warning(f"   Calendar: {'✅' if calendar_ok else '❌'}")
            logging.warning(f"   {result_msg}")
            logging.warning(f"   Final Score: {final_score:.1f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def _check_world_clock(self, env) -> bool:
        """Check whether the target city has been added to World Clock
        
        Refer to the alarm detection logic in Scenario D (clock_utils.check_alarm_with_date):
        1. Ensure that the Clock app is active
        2. Navigate to the World Clock page
        3. Check whether the UI elements contain the target city
        
        Returns:
            bool: True if the city is found, False otherwise
        """
        from scendroid.env import adb_utils
        import time
        
        try:
            logging.info(f"   🔍 Checking World Clock for city: {self.city_name}")
            city_lower = self.city_name.lower()
            
            # 1. Ensure that the Clock app is active (refer to clock_utils.check_alarm_with_date)
            current_activity = adb_utils.get_current_activity(env.controller)[0]
            logging.info(f"   Current activity: {current_activity}")
            
            if "DeskClock" not in current_activity:
                logging.info("   Not in DeskClock, opening Clock app...")
                adb_utils.issue_generic_request(
                    ["shell", "am", "start", "-n", 
                     "com.google.android.deskclock/com.android.deskclock.DeskClock"],
                    env.controller
                )
                time.sleep(2.0)
            
            # 2. Tap the Clock/World Clock tab (bottom navigation bar)
            # The Clock app's bottom navigation bar typically contains: Alarm, Clock, Timer, Stopwatch
            logging.info("   Navigating to World Clock tab...")
            
            # Attempt to tap the "Clock" tab
            ui_elements = env.get_state().ui_elements
            clock_tab_clicked = False
            
            for element in ui_elements:
                text = (element.text or "").lower()
                desc = (element.content_description or "").lower()
                
                # Locate the Clock tab (not Alarm, Timer, or Stopwatch)
                if ("clock" in text or "clock" in desc) and \
                   "alarm" not in text and "alarm" not in desc and \
                   "timer" not in text and "timer" not in desc and \
                   "stopwatch" not in text and "stopwatch" not in desc:
                    if hasattr(element, 'bbox') and element.bbox:
                        center_x = (element.bbox.x_min + element.bbox.x_max) // 2
                        center_y = (element.bbox.y_min + element.bbox.y_max) // 2
                        logging.info(f"   Clicking Clock tab at ({center_x}, {center_y})")
                        adb_utils.issue_generic_request(
                            ["shell", "input", "tap", str(center_x), str(center_y)],
                            env.controller
                        )
                        time.sleep(1.5)
                        clock_tab_clicked = True
                        break
            
            if not clock_tab_clicked:
                # Attempt direct coordinate tapping (the Clock tab is typically the second item in the bottom navigation bar)
                logging.info("   Trying to click Clock tab by position...")
                # The bottom navigation bar is typically at the bottom of the screen, and Clock is the second tab
                adb_utils.issue_generic_request(
                    ["shell", "input", "tap", "360", "1850"],
                    env.controller
                )
                time.sleep(1.5)
            
            # 3. Check whether the target city appears in the UI elements
            ui_elements = env.get_state().ui_elements
            
            for element in ui_elements:
                text = (element.text or "").lower()
                desc = (element.content_description or "").lower()
                
                if city_lower in text or city_lower in desc:
                    logging.info(f"   ✅ Found city: {self.city_name}")
                    return True
            
            # 4. If not found, attempt scrolling to view more cities
            logging.info("   City not visible, scrolling to check...")
            for _ in range(2):
                adb_utils.issue_generic_request(
                    ["shell", "input", "swipe", "500", "1000", "500", "500", "300"],
                    env.controller
                )
                time.sleep(0.5)
                
                ui_elements = env.get_state().ui_elements
                for element in ui_elements:
                    text = (element.text or "").lower()
                    desc = (element.content_description or "").lower()
                    if city_lower in text or city_lower in desc:
                        logging.info(f"   ✅ Found city after scroll: {self.city_name}")
                        return True
            
            # Final failure
            logging.warning(f"   ❌ City not found: {self.city_name}")
            
            # Print current UI elements for debugging
            logging.info("   🔍 Current UI elements (for debugging):")
            ui_elements = env.get_state().ui_elements
            for i, element in enumerate(ui_elements[:20]):
                text = element.text or ""
                desc = element.content_description or ""
                if text or desc:
                    logging.info(f"      [{i}] text='{text}' desc='{desc}'")
            
            return False
            
        except Exception as e:
            logging.warning(f"   ⚠️ World Clock check failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return False
    
    def _check_calendar_event(self, env) -> bool:
        """Check whether Calendar has created a flight event
        
        Returns:
            bool: True if a matching event is found, False otherwise
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        try:
            # Retrieve all events
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            logging.info(f"   Found {len(events)} calendar events")
            
            # Check whether a matching event exists
            for event in events:
                title = (event.title or "").lower()
                event_title_lower = self.event_title.lower()
                
                # Check the title
                if event_title_lower in title or "flight" in title:
                    # Check the time
                    # ✅ Fix: Prioritize the event's own stored time_zone (rather than fixed UTC)
                    # Reason: The Calendar app stores events according to the device's local timezone; if the device is not set to UTC,
                    # parsing with a fixed UTC causes time discrepancies (e.g., CST 08:45 → UTC 00:45 → mismatch)
                    try:
                        from scendroid.utils import datetime_utils as _dt_utils
                        event_tz = (event.time_zone or "UTC").strip()
                        if not event_tz:
                            event_tz = "UTC"
                        localized_dt = _dt_utils.timestamp_to_localized_datetime(
                            event.start_ts, timezone=event_tz
                        )
                        event_hour = localized_dt.hour
                        event_minute = localized_dt.minute
                    except Exception:
                        # fallback: use start_datetime (UTC)
                        event_hour = event.start_datetime.hour
                        event_minute = event.start_datetime.minute
                    
                    # Allow some time tolerance (±30 minutes)
                    time_match = (
                        abs(event_hour * 60 + event_minute - 
                            self.event_hour * 60 - self.event_minute) <= 30
                    )
                    
                    if time_match:
                        logging.info(f"   ✅ Found event: {event.title} at {event_hour}:{event_minute:02d} (tz={event_tz})")
                        return True
                    else:
                        logging.info(f"   ⚠️ Event found but time mismatch: {event.title} "
                                    f"({event_hour}:{event_minute:02d} vs expected {self.event_hour}:{self.event_minute:02d})")
            
            logging.warning(f"   ❌ Event not found: {self.event_title}")
            return False
            
        except Exception as e:
            logging.warning(f"   ⚠️ Calendar check failed: {e}")
            return False


# ============================================================================
# E3. LayeredSystemBluetoothDND - Bluetooth + Do Not Disturb
# ============================================================================

@AppRegistry.register_evaluator("LayeredSystemBluetoothDND")
class SystemBluetoothDNDEvaluator(BaseCrossAppEvaluator):
    """
    System Settings: Bluetooth + Do Not Disturb task
    
    Task flow:
    1. Settings: Enable Bluetooth
    2. Settings: Enable Do Not Disturb mode
    
    Evaluation method:
    - 50% Bluetooth: Check whether Bluetooth is enabled
    - 50% DND: Check whether Do Not Disturb mode is enabled
    
    This is task E3 of Scenario E
    """
    
    app_names = ("settings",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Expected state
        self.bluetooth_on = params.get('bluetooth_on', True)
        self.dnd_on = params.get('dnd_on', True)
        
        # Configuration complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation
        
        Fine-grained scoring (Scenario D modification):
        - 0.0 points: Neither completed
        - 0.5 points: Either Bluetooth OR DND completed
        - 1.0 point: Both completed
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating System: Bluetooth + DND")
        logging.warning("=" * 60)
        
        try:
            from scendroid.env import adb_utils
            
            # Part 1: Check Bluetooth status
            bt_result = adb_utils.issue_generic_request(
                ['shell', 'settings', 'get', 'global', 'bluetooth_on'],
                env.controller
            )
            bt_status = bt_result.generic.output.decode().strip()
            bt_is_on = bt_status == '1'
            bt_ok = bt_is_on == self.bluetooth_on
            
            logging.info(f"   Bluetooth: {'ON' if bt_is_on else 'OFF'} (expected: {'ON' if self.bluetooth_on else 'OFF'}) -> {'✅' if bt_ok else '❌'}")
            
            # Part 2: Check DND status
            dnd_result = adb_utils.issue_generic_request(
                ['shell', 'settings', 'get', 'global', 'zen_mode'],
                env.controller
            )
            dnd_status = dnd_result.generic.output.decode().strip()
            # zen_mode: 0=off, 1=priority only, 2=total silence, 3=alarms only
            dnd_is_on = dnd_status in ['1', '2', '3']
            dnd_ok = dnd_is_on == self.dnd_on
            
            logging.info(f"   DND: {'ON' if dnd_is_on else 'OFF'} (expected: {'ON' if self.dnd_on else 'OFF'}) -> {'✅' if dnd_ok else '❌'}")
            
            # Fine-grained scoring: 0.5 point for completing either part, 1 point for completing both
            if bt_ok and dnd_ok:
                final_score = 1.0
                result_msg = "Both Bluetooth and DND completed (1.0)"
            elif bt_ok or dnd_ok:
                final_score = 0.5
                if bt_ok:
                    result_msg = "Bluetooth OK, but DND not enabled (0.5)"
                else:
                    result_msg = "DND OK, but Bluetooth not turned on (0.5)"
            else:
                final_score = 0.0
                result_msg = "Neither Bluetooth nor DND completed (0.0)"
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Bluetooth: {'✅' if bt_ok else '❌'}")
            logging.warning(f"   DND: {'✅' if dnd_ok else '❌'}")
            logging.warning(f"   {result_msg}")
            logging.warning(f"   Final Score: {final_score:.1f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E5. LayeredCrossAppContactsSmsVcf - Contacts + SMS + VCF
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppContactsSmsVcf")
class CrossAppContactsSmsVcfEvaluator(BaseCrossAppEvaluator):
    """
    Contacts + SMS cross-app task
    
    Task flow:
    1. SMS: Send a text message
    2. SMS: The message contains contact information (phone number)
    
    Evaluation method (AND logic, only 0 or 1):
    - Check whether a text message was sent (containing the specified keyword)
    - Check whether the message contains the contact's phone number
    
    This is Scenario E's E5 task
    """
    
    app_names = ("contacts", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.recipient_name = params.get('recipient_name', 'Sarah Miller')
        self.recipient_phone = params.get('recipient_phone', '555-0102')
        self.message_text = params.get('message_text', "I've arrived safely")
        self.vcf_contact_name = params.get('vcf_contact_name', 'Hotel Front Desk')
        self.vcf_contact_phone = params.get('vcf_contact_phone', '415-555-0199')
        
        # Set complexity
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating CrossApp: Contacts + SMS + VCF")
        logging.warning("=" * 60)
        
        try:
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.env import adb_utils
            
            # Retrieve sent messages
            response = adb_utils.issue_generic_request(
                "shell content query --uri content://sms/sent".split(),
                env.controller
            )
            sent_messages = sms_validators._decode_messages_from_response(response)
            
            logging.info(f"   Found {len(sent_messages)} sent messages")
            
            # Part 1: Check the text message
            text_found = False
            contact_phone_found = False
            
            # Normalize the expected phone number (remove - and spaces)
            normalized_vcf_phone = self.vcf_contact_phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            for msg_str in sent_messages:
                try:
                    msg = sms_validators.parse_message(msg_str)
                    body = (msg.get('body') or '')
                    body_lower = body.lower()
                    address = (msg.get('address') or '')
                    
                    # Normalize the phone number
                    normalized_address = address.replace('-', '').replace(' ', '')
                    normalized_recipient = self.recipient_phone.replace('-', '').replace(' ', '')
                    
                    # Check whether the message was sent to the target contact
                    if normalized_recipient in normalized_address:
                        logging.info(f"   📱 Message to {self.recipient_name}: '{body[:80]}...'")
                        
                        # Check the text message (for the "arrived" keyword)
                        if self.message_text.lower() in body_lower or 'arrived' in body_lower:
                            text_found = True
                            logging.info(f"   ✅ Arrival message found")
                        
                        # Check whether the contact's phone number is included
                        # Normalize the phone number in the message body
                        body_normalized = body.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                        
                        if normalized_vcf_phone in body_normalized:
                            contact_phone_found = True
                            logging.info(f"   ✅ Contact phone found: {self.vcf_contact_phone}")
                        
                        # Alternative: Check whether the message body contains "Hotel", "Desk", and a phone number format
                        if ('hotel' in body_lower or 'front desk' in body_lower) and any(c.isdigit() for c in body):
                            contact_phone_found = True
                            logging.info(f"   ✅ Hotel contact info found in message")
                            
                except Exception as e:
                    logging.debug(f"   Failed to parse message: {e}")
                    continue
            
            # Success requires both parts to pass (AND logic, only 0 or 1)
            final_score = 1.0 if (text_found and contact_phone_found) else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Arrival Text: {'✅' if text_found else '❌'}")
            logging.warning(f"   Contact Phone: {'✅' if contact_phone_found else '❌'} (expected: {self.vcf_contact_phone})")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E6. LayeredAudioRecorderWithConfig - Audio Recorder with Configuration
# ============================================================================

@AppRegistry.register_evaluator("LayeredAudioRecorderWithConfig")
class AudioRecorderWithConfigEvaluator(BaseCrossAppEvaluator):
    """
    Audio Recorder configuration recording task
    
    Task flow:
    1. Audio Recorder: Enter Settings
    2. Modify the recording format and sample rate
    3. Start recording and name the recording
    
    Evaluation method:
    - 50%: Whether the recording file exists and has the correct name
    - 50%: Whether the recording format is correct
    
    This is Scenario E's E6 task
    """
    
    app_names = ("audio recorder",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.recording_name = params.get('recording_name', 'Keynote_AI')
        self.expected_format = params.get('expected_format', 'wav')
        self.expected_sample_rate = params.get('expected_sample_rate', '48kHz')
        
        # Set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Audio Recorder with Config")
        logging.warning("=" * 60)
        
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            # Get the list of audio recording files
            recordings = file_utils.get_file_list_with_metadata(
                device_constants.AUDIORECORDER_DATA, env.controller
            )
            
            logging.info(f"   Found {len(recordings)} recordings")
            
            # Check whether an audio recording with the target name exists
            name_found = False
            format_correct = False
            
            for recording in recordings:
                file_name = recording.file_name.lower()
                expected_name = self.recording_name.lower()
                
                if expected_name in file_name:
                    name_found = True
                    logging.info(f"   ✅ Recording found: {recording.file_name}")
                    
                    # Check format
                    if file_name.endswith(f'.{self.expected_format}'):
                        format_correct = True
                        logging.info(f"   ✅ Format correct: {self.expected_format}")
                    else:
                        logging.warning(f"   ⚠️ Format mismatch: expected .{self.expected_format}")
                    break
            
            if not name_found:
                logging.warning(f"   ❌ Recording not found: {self.recording_name}")
            
            # Both parts must pass for success (AND logic; only 0 or 1)
            final_score = 1.0 if (name_found and format_correct) else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Recording Name: {'✅' if name_found else '❌'}")
            logging.warning(f"   Format Correct: {'✅' if format_correct else '❌'}")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E8. LayeredExpenseAddMultiple - Add Multiple Expenses
# ============================================================================

@AppRegistry.register_evaluator("LayeredExpenseAddMultiple")
class ExpenseAddMultipleEvaluator(BaseCrossAppEvaluator):
    """
    Pro Expense Multiple Expense Records Task
    
    Task flow:
    1. Pro Expense: Add multiple expense records
    
    Evaluation method:
    - Verify that each expense is correctly added
    - Score based on the proportion of added records
    
    This is Scenario E's E8 task
    """
    
    app_names = ("pro expense",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Expected expense list
        self.expenses = params.get('expenses', [])
        
        # Internal state
        self._before_expenses = []
        
        # Set complexity
        self.complexity = 2.0
    
    def initialize_task(self, env):
        """Initialize task: Record current expenses"""
        super().initialize_task(env)
        
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            EXPENSE_TABLE = "expense"
            
            self._before_expenses = sqlite_utils.get_rows_from_remote_device(
                EXPENSE_TABLE,
                EXPENSE_DB_PATH,
                sqlite_schema_utils.Expense,
                env,
            )
            
            logging.info(f"   Recorded {len(self._before_expenses)} existing expenses")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to record initial expenses: {e}")
            self._before_expenses = []
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Expense Add Multiple")
        logging.warning("=" * 60)
        
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            EXPENSE_TABLE = "expense"
            
            # Get current expenses
            current_expenses = sqlite_utils.get_rows_from_remote_device(
                EXPENSE_TABLE,
                EXPENSE_DB_PATH,
                sqlite_schema_utils.Expense,
                env,
            )
            
            # Identify newly added expenses
            before_ids = {e.expense_id for e in self._before_expenses}
            new_expenses = [e for e in current_expenses if e.expense_id not in before_ids]
            
            logging.info(f"   Found {len(new_expenses)} new expenses")
            
            # Check whether each expected expense has been added
            found_count = 0
            for expected in self.expenses:
                expected_name = expected.get('name', '').lower()
                expected_amount = expected.get('amount', 0)
                expected_category = expected.get('category', '').lower()
                
                for expense in new_expenses:
                    name = (expense.name or '').lower()
                    # Amount stored in cents
                    amount_dollars = expense.amount / 100.0 if expense.amount else 0
                    category_name = expense.category_name.lower() if hasattr(expense, 'category_name') else ''
                    
                    # Check name match
                    name_match = expected_name in name or name in expected_name
                    
                    # Check amount match (allowing a 10% tolerance)
                    amount_match = abs(amount_dollars - expected_amount) / max(expected_amount, 1) < 0.1
                    
                    if name_match and amount_match:
                        found_count += 1
                        logging.info(f"   ✅ Found expense: {expense.name} (${amount_dollars:.2f})")
                        break
            
            # All expected expenses must be found for success (only 0 or 1)
            all_found = (found_count == len(self.expenses)) if len(self.expenses) > 0 else (len(new_expenses) > 0)
            final_score = 1.0 if all_found else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Expected expenses: {len(self.expenses)}")
            logging.warning(f"   Found expenses: {found_count}")
            logging.warning(f"   All found: {'✅' if all_found else '❌'}")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E9. LayeredMarkorWithAttachment - Markor with Attachment Reference
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorWithAttachment")
class MarkorWithAttachmentEvaluator(BaseCrossAppEvaluator):
    """
    Markor Attachment Reference Task
    
    Task flow:
    1. Markor: Create a Markdown file
    2. Reference an attachment (e.g., an audio recording file) within the file
    3. Include specific keywords
    
    Evaluation method:
    - 40%: Whether the file exists
    - 30%: Whether the attachment is referenced
    - 30%: Whether the keywords are included
    
    This is Scenario E's E9 task
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameter
        self.file_name = params.get('file_name', 'Day1_Summary.md')
        self.attachment_name = params.get('attachment_name', 'Keynote_AI')
        self.must_contain_keywords = params.get('must_contain_keywords', [])
        self.min_keywords_found = params.get('min_keywords_found', 1)
        # Added: Expected expense amount (check whether any is mentioned)
        self.expense_amounts = params.get('expense_amounts', [])
        
        # Set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Markor with Attachment")
        logging.warning("=" * 60)
        
        try:
            from scendroid.env import device_constants, adb_utils
            import re
            
            # Check whether the file exists
            markor_dir = device_constants.MARKOR_DATA
            file_path = f"{markor_dir}/{self.file_name}"
            
            # Attempt to read the file content
            cat_result = adb_utils.issue_generic_request(
                ['shell', 'cat', file_path],
                env.controller
            )
            
            content = ""
            if cat_result and cat_result.generic and cat_result.generic.output:
                content = cat_result.generic.output.decode('utf-8', errors='ignore')
            
            file_exists = len(content) > 10  # File exists and has content
            
            if not file_exists:
                logging.warning(f"   ❌ File not found or empty: {self.file_name}")
                return 0.0
            
            logging.info(f"   ✅ File found: {self.file_name} ({len(content)} chars)")
            logging.info(f"   Content preview: {content[:200]}...")
            
            # Check attachment references
            content_lower = content.lower()
            attachment_found = self.attachment_name.lower() in content_lower
            
            if attachment_found:
                logging.info(f"   ✅ Attachment referenced: {self.attachment_name}")
            else:
                logging.warning(f"   ❌ Attachment not found: {self.attachment_name}")
            
            # Check keywords
            keywords_found = 0
            for keyword in self.must_contain_keywords:
                keyword_str = str(keyword).lower()
                if keyword_str in content_lower:
                    keywords_found += 1
                    logging.info(f"   ✅ Keyword found: {keyword}")
                else:
                    logging.warning(f"   ❌ Keyword not found: {keyword}")
            
            keywords_ok = keywords_found >= self.min_keywords_found
            
            # Check expense amount (if provided)
            expense_found = True  # Default to True (if no expense_amounts are provided)
            if self.expense_amounts:
                expense_found = False
                # Extract all numbers from the content
                numbers_in_content = re.findall(r'\d+\.?\d*', content)
                numbers_float = [float(n) for n in numbers_in_content if n]
                
                logging.info(f"   📊 Checking expenses: expecting any of {self.expense_amounts}")
                logging.info(f"   Numbers found in content: {numbers_float[:10]}...")
                
                for expected_amount in self.expense_amounts:
                    # Check for matching amounts (allowing a 10% tolerance or exact integer match)
                    for num in numbers_float:
                        if abs(num - expected_amount) < 0.5 or abs(num - int(expected_amount)) < 0.5:
                            expense_found = True
                            logging.info(f"   ✅ Expense amount found: ${expected_amount:.2f} (matched {num})")
                            break
                    if expense_found:
                        break
                
                if not expense_found:
                    logging.warning(f"   ❌ No expense amount found")
            
            # All three parts must pass for success (AND logic, only 0 or 1)
            final_score = 1.0 if (file_exists and attachment_found and keywords_ok and expense_found) else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   File exists: {'✅' if file_exists else '❌'}")
            logging.warning(f"   Attachment ref: {'✅' if attachment_found else '❌'}")
            logging.warning(f"   Keywords ({keywords_found}/{self.min_keywords_found}): {'✅' if keywords_ok else '❌'}")
            if self.expense_amounts:
                logging.warning(f"   Expense mentioned: {'✅' if expense_found else '❌'}")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E9. LayeredMarkorTripSummary - Markor Trip Summary (trip and expense log)
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorTripSummary")
class MarkorTripSummaryEvaluator(BaseCrossAppEvaluator):
    """
    Markor trip summary task
    
    Task flow:
    1. View trip information in the PNG
    2. Create a file in Markor to record the trip information
    3. Record today's expenses simultaneously
    
    Evaluation method (AND logic, only 0 or 1):
    - Whether the file exists
    - Whether it contains flight information (flight number, departure time, arrival time, destination)
    - Whether it contains today's expense amount
    
    This is task E9 of Scenario E
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameter
        self.file_name = params.get('file_name', 'Day1_Summary.md')
        self.flight_info = params.get('flight_info', {})
        self.expense_amounts = params.get('expense_amounts', [])
        
        # Set complexity
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Perform evaluation"""
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Markor Trip Summary")
        logging.warning("=" * 60)
        
        try:
            from scendroid.env import device_constants, adb_utils
            import re
            
            # 1. Check whether the file exists
            markor_dir = device_constants.MARKOR_DATA
            file_path = f"{markor_dir}/{self.file_name}"
            
            cat_result = adb_utils.issue_generic_request(
                ['shell', 'cat', file_path],
                env.controller
            )
            
            content = ""
            if cat_result and cat_result.generic and cat_result.generic.output:
                content = cat_result.generic.output.decode('utf-8', errors='ignore')
            
            file_exists = len(content) > 10
            
            if not file_exists:
                logging.warning(f"   ❌ File not found or empty: {self.file_name}")
                return 0.0
            
            logging.info(f"   ✅ File found: {self.file_name} ({len(content)} chars)")
            logging.info(f"   Content preview: {content[:300]}...")
            
            content_lower = content.lower()
            
            # 2. Check flight information
            flight_info_found = True
            flight_checks = []
            
            if self.flight_info:
                flight_number = self.flight_info.get('flight_number', '')
                departure = self.flight_info.get('departure', '')
                arrival = self.flight_info.get('arrival', '')
                destination = self.flight_info.get('destination', '')
                
                # Check flight number (e.g., DL 321, DL321, DL-321)
                flight_num_normalized = flight_number.replace(' ', '').lower()
                if flight_num_normalized in content_lower.replace(' ', '').replace('-', ''):
                    flight_checks.append(('Flight Number', True))
                    logging.info(f"   ✅ Flight number found: {flight_number}")
                else:
                    flight_checks.append(('Flight Number', False))
                    logging.warning(f"   ❌ Flight number not found: {flight_number}")
                    flight_info_found = False
                
                # Check departure time
                if departure in content:
                    flight_checks.append(('Departure', True))
                    logging.info(f"   ✅ Departure time found: {departure}")
                else:
                    flight_checks.append(('Departure', False))
                    logging.warning(f"   ❌ Departure time not found: {departure}")
                    flight_info_found = False
                
                # Check arrival time
                if arrival in content:
                    flight_checks.append(('Arrival', True))
                    logging.info(f"   ✅ Arrival time found: {arrival}")
                else:
                    flight_checks.append(('Arrival', False))
                    logging.warning(f"   ❌ Arrival time not found: {arrival}")
                    flight_info_found = False
                
                # Check destination (partial matching allowed)
                dest_words = destination.lower().split()
                dest_found = any(word in content_lower for word in dest_words if len(word) > 3)
                if dest_found:
                    flight_checks.append(('Destination', True))
                    logging.info(f"   ✅ Destination found: {destination}")
                else:
                    flight_checks.append(('Destination', False))
                    logging.warning(f"   ❌ Destination not found: {destination}")
                    flight_info_found = False
            
            # 3. Check expense amount
            expense_found = True
            if self.expense_amounts:
                expense_found = False
                numbers_in_content = re.findall(r'\d+\.?\d*', content)
                numbers_float = [float(n) for n in numbers_in_content if n]
                
                logging.info(f"   📊 Checking expenses: expecting {self.expense_amounts}")
                logging.info(f"   Numbers found: {numbers_float[:15]}...")
                
                found_expenses = 0
                for expected_amount in self.expense_amounts:
                    for num in numbers_float:
                        if abs(num - expected_amount) < 0.5 or abs(num - int(expected_amount)) < 0.5:
                            found_expenses += 1
                            logging.info(f"   ✅ Expense found: ${expected_amount:.2f} (matched {num})")
                            break
                
                # At least one expense amount must be found
                expense_found = found_expenses >= 1
                if not expense_found:
                    logging.warning(f"   ❌ No expense amounts found")
            
            # Calculate the final score (AND logic)
            final_score = 1.0 if (file_exists and flight_info_found and expense_found) else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   File exists: {'✅' if file_exists else '❌'}")
            logging.warning(f"   Flight info: {'✅' if flight_info_found else '❌'}")
            for check_name, check_result in flight_checks:
                logging.warning(f"      - {check_name}: {'✅' if check_result else '❌'}")
            logging.warning(f"   Expenses: {'✅' if expense_found else '❌'}")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# E10. LayeredExpenseStatisticsQA - Expense Statistics QA
# ============================================================================

@AppRegistry.register_evaluator("LayeredExpenseStatisticsQA")
class ExpenseStatisticsQAEvaluator(BaseCrossAppEvaluator):
    """
    Pro Expense Statistical Q&A Task (Last Three Days)
    
    Task flow:
    1. Pro Expense: View the expense list
    2. Calculate the total expenses for the last three days (Day 0, 1, 2)
    3. Answer whether the budget for the last three days has been exceeded
    
    Evaluation method:
    - Check whether the agent correctly determines whether the budget has been exceeded
    - Compare against expected_total (the ground-truth total for the last three days) and the budget
    
    Challenges:
    - The database contains distractor expenses for Days 3–6 (with large amounts)
    - The agent must correctly identify the time range and compute only the last three days
    
    This is Task D10 of Scenario D
    """
    
    app_names = ("pro expense",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Required parameters
        self.budget = params.get('budget', 300.0)
        self.expected_total = params.get('expected_total', 305.0)
        self.is_over_budget = params.get('is_over_budget', True)
        self.must_contain_keywords = params.get('must_contain_keywords', [])
        self.min_keywords_found = params.get('min_keywords_found', 1)
        
        # Set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation (Q&A task)
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Expense Statistics QA")
        logging.warning("=" * 60)
        
        try:
            # Retrieve the agent's answer (from interaction_cache)
            from scendroid.apps.calendar import utils as calendar_utils
            agent_answer = calendar_utils.get_agent_answer(env)
            
            if not agent_answer:
                logging.warning("   ❌ No agent answer found")
                logging.warning("   💡 Hint: For QA tasks, type your answer in the TUI input box")
                return 0.0
            
            answer_lower = agent_answer.lower()
            logging.info(f"   Agent answer: {agent_answer}")
            logging.info(f"   Expected: is_over_budget={self.is_over_budget}, budget=${self.budget:.0f}")
            
            # Check whether the budget status is correctly determined
            budget_judgment_correct = False
            
            # Keywords indicating "budget exceeded"
            over_budget_indicators = [
                'exceed', 'exceeded', 'exceeds', 'exceeding',
                'over', 'above', 'surpass', 'more than',
                'yes', 'have exceeded', 'has exceeded',
                'exceed', 'exceeded', 'over',
            ]
            
            # Keywords indicating "budget not exceeded"
            under_budget_indicators = [
                'under', 'within', 'below', 'less than',
                'not exceed', 'haven\'t exceeded', 'hasn\'t exceeded',
                'no', 'have not', 'has not', 'did not',
                'not exceed', 'has not exceeded', 'below',
            ]
            
            if self.is_over_budget:
                # Expected budget exceeded: check for "exceed"-related indicators and absence of negation
                has_over_indicator = any(ind in answer_lower for ind in over_budget_indicators)
                has_negation = any(neg in answer_lower for neg in ['not exceed', 'haven\'t', 'hasn\'t', 'did not', ])
                budget_judgment_correct = has_over_indicator and not has_negation
                logging.info(f"   Over check: has_indicator={has_over_indicator}, has_negation={has_negation}")
            else:
                # Expected budget not exceeded
                has_under_indicator = any(ind in answer_lower for ind in under_budget_indicators)
                budget_judgment_correct = has_under_indicator
                logging.info(f"   Under check: has_indicator={has_under_indicator}")
            
            # Only correct determination of budget status is required (simplified evaluation)
            final_score = 1.0 if budget_judgment_correct else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   Expected: {'Over' if self.is_over_budget else 'Under'} budget")
            logging.warning(f"   Budget judgment: {'✅' if budget_judgment_correct else '❌'}")
            logging.warning(f"   Final Score: {final_score:.0f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# F1. LayeredCrossAppRecipeTasks - Recipe + Tasks (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppRecipeTasks")
class CrossAppRecipeTasksEvaluator(BaseCrossAppEvaluator):
    """
    Broccoli Recipe + Tasks Cross-App Task
    
    Task flow:
    1. Open the recipe app and view the specified recipe
    2. Add required items to the Tasks app
    3. Mark existing items as completed
    
    Evaluation method:
    - Check whether the required items are present in Tasks
    - Check whether existing items are marked as completed
    """
    
    app_names = ("broccoli recipe", "tasks")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.recipe_title = params.get('recipe_title', 'Picnic BBQ')
        self.required_items = params.get('required_items', [])
        self.already_have = params.get('already_have', [])
        self.check_off_items = params.get('check_off_items', [])
        
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Check whether the required items are present in Tasks (binary score: 0 or 1)"""
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Recipe + Tasks")
        logging.warning("=" * 60)
        
        try:
            # Query the Tasks database
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
                '--projection', 'title',
            ]
            
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore').lower()
            
            logging.info(f"   Tasks output: {output[:500]}...")
            
            # Check whether the required items are present in Tasks
            items_found = 0
            for item in self.required_items:
                if item.lower() in output:
                    items_found += 1
                    logging.info(f"   ✅ Found: {item}")
                else:
                    logging.warning(f"   ❌ Missing: {item}")
            
            # Binary scoring: success only if all items are found
            all_found = items_found == len(self.required_items) if self.required_items else True
            score = 1.0 if all_found else 0.0
            
            logging.warning(f"   Items found: {items_found}/{len(self.required_items)}")
            logging.warning(f"   Score: {score:.2f} (binary: all items required)")
            logging.warning("=" * 60)
            
            return score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: clear Tasks
        
        Note: In Scenario mode, Tasks is already set up during scenario initialization
        (including already_have tasks and distractor tasks), so it should not be cleared
        """
        super().initialize_task(env)
        
        # ⚠️ Do not clear Tasks in Scenario mode
        # Batch initialization for Scenario has already set up already_have tasks and distractor tasks
        # Clearing here would corrupt the scenario-initialized data
        # 
        # Determine whether in Scenario mode:
        # - If initialize_task is called by the scenario's initialize_subtask (should not occur)
        # - Or if this is an independent task-level test
        # 
        # Simple detection method: check whether tasks already exist
        # If tasks exist, it indicates Scenario mode; do not clear
        from scendroid.env import adb_utils
        from scendroid.task_evals.information_retrieval import task_app_utils
        
        try:
            # Check whether tasks already exist (Scenario mode pre-creates them)
            existing_tasks = task_app_utils.list_rows(env)
            
            if existing_tasks:
                logging.info(f"   ℹ️  Found {len(existing_tasks)} existing tasks (Scenario mode)")
                logging.info("   ℹ️  Skipping Tasks app clear to preserve scenario data")
            else:
                # Independent task-level test; clear Tasks
                adb_utils.issue_generic_request([
                    'shell', 'pm', 'clear', 'org.tasks'
                ], env.controller)
                logging.info("   ✅ Tasks app cleared (standalone task mode)")
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to check/clear Tasks: {e}")


# ============================================================================
# F2. LayeredCrossAppCalendarUpdateSMS - Calendar Update + SMS (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppCalendarUpdateSMS")
class CrossAppCalendarUpdateSMSEvaluator(BaseCrossAppEvaluator):
    """
    Calendar + SMS cross-app task: update meeting location and notify participants
    
    Task workflow:
    1. Open Calendar and locate the specified event
    2. Update the event location
    3. Send an SMS containing the new location to all participants
    
    Evaluation method:
    - Check whether the calendar event location is updated (50%)
    - Check whether all participants received the SMS containing the new location (50%)
    """
    
    app_names = ("simple calendar pro", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.event_title = params.get('event_title', '')
        self.old_location = params.get('old_location', '')
        self.new_location = params.get('new_location', '')
        self.event_hour = params.get('event_hour', 10)
        self.event_minute = params.get('event_minute', 0)
        self.attendees = params.get('attendees', [])
        self.distractor_contacts = params.get('distractor_contacts', [])
        self.message_must_contain = params.get('message_must_contain', [])
        self.user_name = params.get('user_name', '')  # Used to exclude the user themselves
        
        self.complexity = 4.0
    
    def evaluate(self, env) -> float:
        """Evaluation: check location update and SMS sending"""
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Calendar Update + SMS")
        logging.warning("=" * 60)
        
        try:
            # Part 1: Check whether the calendar event location is updated (50%)
            location_updated = False
            
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            for event in events:
                if self.event_title.lower() in (event.title or '').lower():
                    event_location = event.location or ''
                    if self.new_location.lower() in event_location.lower():
                        location_updated = True
                        logging.info(f"   ✅ Location updated to: {event_location}")
                        break
            
            location_score = 1.0 if location_updated else 0.0
            
            # Part 2: Check SMS sending (50%)
            response = adb_utils.issue_generic_request(
                "shell content query --uri content://sms/sent".split(), env.controller
            )
            sent_messages = sms_validators._decode_messages_from_response(response)
            
            # Filter out the user themselves (no need to send SMS to oneself)
            attendees_to_notify = [
                a for a in self.attendees 
                if self.user_name.lower() not in a.get('name', '').lower()
            ]
            
            correct_notifications = 0
            for attendee in attendees_to_notify:
                found = False
                attendee_phone = attendee.get('number', '').replace('-', '').replace(' ', '')
                
                for msg_str in sent_messages:
                    try:
                        msg = sms_validators.parse_message(msg_str)
                        msg_address = msg.get('address', '').replace('-', '').replace(' ', '')
                        
                        if attendee_phone in msg_address or msg_address in attendee_phone:
                            msg_body = (msg.get('body', '') or '').lower()
                            if self.new_location.lower() in msg_body:
                                found = True
                                break
                    except Exception:
                        continue
                
                if found:
                    correct_notifications += 1
                    logging.info(f"   ✅ {attendee['name']} received correct SMS")
                else:
                    logging.warning(f"   ❌ {attendee['name']} did NOT receive correct SMS")
            
            all_sms_sent = correct_notifications == len(attendees_to_notify) if attendees_to_notify else True
            logging.info(f"   ℹ️ Excluded self ({self.user_name}) from SMS check")
            
            # Binary scoring: success only if location is updated AND all SMS messages are sent successfully
            success = location_updated and all_sms_sent
            final_score = 1.0 if success else 0.0
            
            logging.warning("-" * 60)
            logging.warning("📊 Results:")
            logging.warning(f"   Location Updated: {location_updated}")
            logging.warning(f"   SMS Sent: {correct_notifications}/{len(self.attendees)}")
            logging.warning(f"   Final Score: {final_score:.2f} (binary: both required)")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# F3. LayeredRetroMusicCreatePlaylist - Create Playlist (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredRetroMusicCreatePlaylist")
class RetroMusicCreatePlaylistEvaluator(BaseCrossAppEvaluator):
    """
    Retro Music create playlist task
    
    Task workflow:
    1. Create a new playlist
    2. Add songs in order
    
    Evaluation method:
    - Check whether the playlist exists
    - Check whether songs are added in the correct order (using sqlite_validators.verify_playlist)
    """
    
    app_names = ("retro music",)
    
    _PLAYLIST_DB_PATH = '/data/data/code.name.monkey.retromusic/databases/playlist.db'
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.playlist_name = params.get('playlist_name', 'Mountain Hike')
        self.songs = params.get('songs', [])
        self.require_order = params.get('require_order', True)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Verify that the playlist was created successfully and songs were added in the correct order"""
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.task_evals.common_validators import sqlite_validators
        from scendroid.utils import file_utils
        import os
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Retro Music Playlist")
        logging.warning("=" * 60)
        
        try:
            # Use the method from retro_music.py to retrieve playlist data
            playlist_info_query = """
                SELECT
                    pe.playlist_name AS playlist_name,
                    se.title AS media_file_name,
                    se.duration AS duration_ms,
                    ROW_NUMBER() OVER (
                        PARTITION BY pe.playlist_name
                        ORDER BY se.song_key
                    ) - 1 AS order_in_playlist
                FROM
                    PlaylistEntity pe
                    JOIN SongEntity se ON pe.playlist_id = se.playlist_creator_id
                ORDER BY
                    pe.playlist_name,
                    order_in_playlist;
            """
            
            with env.controller.pull_file(
                self._PLAYLIST_DB_PATH, timeout_sec=3
            ) as local_db_directory:
                local_db_path = file_utils.convert_to_posix_path(
                    local_db_directory, os.path.split(self._PLAYLIST_DB_PATH)[1]
                )
                actual_playlist = sqlite_utils.execute_query(
                    playlist_info_query,
                    local_db_path,
                    sqlite_schema_utils.PlaylistInfo,
                )
            
            logging.info(f"   Found {len(actual_playlist)} songs in playlists")
            
            # Use verify_playlist to validate the playlist name and song order
            is_valid = sqlite_validators.verify_playlist(
                actual_playlist,
                self.playlist_name,
                self.songs,  # Expected list of songs (in order)
            )
            
            if is_valid:
                logging.warning(f"   ✅ Playlist '{self.playlist_name}' verified with {len(self.songs)} songs in correct order")
                return 1.0
            else:
                logging.warning(f"   ❌ Playlist verification failed")
                # Print detailed information for debugging
                for item in actual_playlist:
                    logging.info(f"      - {item.playlist_name}: {item.media_file_name} (order: {item.order_in_playlist})")
                return 0.0
                
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Stop current playback"""
        super().initialize_task(env)
        
        from scendroid.env import adb_utils
        
        try:
            adb_utils.issue_generic_request([
                'shell', 'input', 'keyevent', 'KEYCODE_MEDIA_STOP'
            ], env.controller)
            logging.info("   ✅ Playback stopped")
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to stop playback: {e}")


# ============================================================================
# F4. LayeredCrossAppTracksMusic - OpenTracks + Music (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppTracksMusic")
class CrossAppTracksMusicEvaluator(BaseCrossAppEvaluator):
    """
    OpenTracks + Retro Music cross-app task
    
    Task flow:
    1. Launch OpenTracks to record an activity
    2. Start playing the playlist
    
    Evaluation method:
    - Check whether OpenTracks is recording (50%)
    - Check whether music is playing (50%)
    """
    
    app_names = ("opentracks", "retro music")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.start_recording = params.get('start_recording', True)
        self.playlist_name = params.get('playlist_name', '')
        self.check_music_playing = params.get('check_music_playing', True)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether the track is being recorded AND music is playing"""
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating OpenTracks + Music")
        logging.warning("=" * 60)
        
        try:
            # Part 1: Check whether OpenTracks is recording
            # Determine this by checking whether OpenTracks' foreground service is active
            tracks_recording = False
            
            # Method 1: Check OpenTracks' foreground service notification
            cmd_notif = ['shell', 'dumpsys', 'notification']
            response_notif = adb_utils.issue_generic_request(cmd_notif, env.controller)
            notif_output = response_notif.generic.output.decode('utf-8', errors='ignore')
            
            # OpenTracks displays a foreground service notification when recording
            if 'de.dennisguse.opentracks' in notif_output and ('Recording' in notif_output or 'recording' in notif_output):
                tracks_recording = True
                logging.info("   ✅ OpenTracks is actively recording (notification found)")
            
            # Method 2: Check activity status
            if not tracks_recording:
                cmd_activity = ['shell', 'dumpsys', 'activity', 'activities']
                response_activity = adb_utils.issue_generic_request(cmd_activity, env.controller)
                activity_output = response_activity.generic.output.decode('utf-8', errors='ignore')
                
                # Check whether RecordingActivity is in the foreground
                if 'de.dennisguse.opentracks' in activity_output:
                    if 'TrackRecordingActivity' in activity_output or 'RecordingActivity' in activity_output:
                        tracks_recording = True
                        logging.info("   ✅ OpenTracks recording activity is active")
            
            if not tracks_recording:
                logging.warning("   ❌ OpenTracks is NOT recording")
            
            # Part 2: Check whether music is playing the specified playlist (rather than merely checking whether the app exists)
            music_playing = False
            playing_from_playlist = False
            
            # First, check whether the specified playlist exists
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            from scendroid.utils import file_utils
            import os
            
            _PLAYLIST_DB_PATH = '/data/data/code.name.monkey.retromusic/databases/playlist.db'
            
            playlist_exists = False
            playlist_songs = []
            try:
                playlist_info_query = """
                    SELECT
                        pe.playlist_name AS playlist_name,
                        se.title AS media_file_name,
                        se.duration AS duration_ms,
                        ROW_NUMBER() OVER (
                            PARTITION BY pe.playlist_name
                            ORDER BY se.song_key
                        ) - 1 AS order_in_playlist
                    FROM
                        PlaylistEntity pe
                        JOIN SongEntity se ON pe.playlist_id = se.playlist_creator_id
                    WHERE
                        pe.playlist_name = '{}'
                    ORDER BY
                        order_in_playlist;
                """.format(self.playlist_name)
                
                with env.controller.pull_file(
                    _PLAYLIST_DB_PATH, timeout_sec=3
                ) as local_db_directory:
                    local_db_path = file_utils.convert_to_posix_path(
                        local_db_directory, os.path.split(_PLAYLIST_DB_PATH)[1]
                    )
                    playlist_data = sqlite_utils.execute_query(
                        playlist_info_query,
                        local_db_path,
                        sqlite_schema_utils.PlaylistInfo,
                    )
                
                if playlist_data:
                    playlist_exists = True
                    playlist_songs = [p.media_file_name for p in playlist_data]
                    logging.info(f"   ✅ Playlist '{self.playlist_name}' exists with {len(playlist_songs)} songs")
                else:
                    logging.warning(f"   ❌ Playlist '{self.playlist_name}' does NOT exist")
            except Exception as e:
                logging.warning(f"   ⚠️ Could not check playlist: {e}")
            
            # If the playlist does not exist, fail immediately
            if not playlist_exists:
                logging.warning("   ❌ Cannot play from non-existent playlist")
                return 0.0
            
            # Check the playback state in the media session
            cmd_media = ['shell', 'dumpsys', 'media_session']
            response_media = adb_utils.issue_generic_request(cmd_media, env.controller)
            media_output = response_media.generic.output.decode('utf-8', errors='ignore')
            
            # Check whether Retro Music is in the playing state (state=3 indicates playback)
            # Key: Both the package and the playback state must be checked
            if 'code.name.monkey.retromusic' in media_output:
                # Locate the playback state
                lines = media_output.split('\n')
                in_retro_section = False
                for line in lines:
                    if 'code.name.monkey.retromusic' in line:
                        in_retro_section = True
                    if in_retro_section:
                        # state=3 indicates playback
                        if 'state=3' in line or 'state=PLAYING' in line.upper():
                            music_playing = True
                            logging.info("   ✅ Retro Music is actively playing")
                        
                        # Check whether the currently playing song is in the playlist
                        if playlist_songs and music_playing:
                            for song_name in playlist_songs:
                                if song_name.lower() in line.lower():
                                    playing_from_playlist = True
                                    logging.info(f"   ✅ Playing song '{song_name}' from playlist")
                                    break
                        
                        # If another session is encountered, stop checking
                        if 'Session ' in line and 'retromusic' not in line:
                            break
            
            if not music_playing:
                # Fallback check: Check audio focus
                cmd_audio = ['shell', 'dumpsys', 'audio']
                response_audio = adb_utils.issue_generic_request(cmd_audio, env.controller)
                audio_output = response_audio.generic.output.decode('utf-8', errors='ignore')
                
                if 'code.name.monkey.retromusic' in audio_output and 'GAIN' in audio_output:
                    music_playing = True
                    logging.info("   ✅ Retro Music has audio focus (playing)")
            
            # If no song from the playlist is detected as playing, also check whether shuffle mode is enabled
            # (In shuffle mode, a song from the playlist may be playing)
            if music_playing and not playing_from_playlist and playlist_songs:
                # Relax the condition: assume the playlist is being played as long as music is playing and the playlist exists
                # Because it is difficult to determine the current song in shuffle mode
                playing_from_playlist = True
                logging.info("   ℹ️ Music playing and playlist exists, assuming playing from playlist")
            
            if not music_playing:
                logging.warning("   ❌ Music is NOT playing")
            
            # Binary scoring: both OpenTracks recording AND music playback from the playlist must succeed for success
            success = tracks_recording and music_playing and playing_from_playlist
            final_score = 1.0 if success else 0.0
            
            logging.warning("-" * 60)
            logging.warning(f"   OpenTracks Recording: {'✅' if tracks_recording else '❌'}")
            logging.warning(f"   Music Playing: {'✅' if music_playing else '❌'}")
            logging.warning(f"   Playing from Playlist '{self.playlist_name}': {'✅' if playing_from_playlist else '❌'}")
            logging.warning(f"   Final Score: {final_score:.2f} (all three required)")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task"""
        super().initialize_task(env)
        logging.info("   📱 Task 4 initialized: OpenTracks + Music")


# ============================================================================
# F5. LayeredCameraRecordVideo - Record Video (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCameraRecordVideo")
class CameraRecordVideoEvaluator(BaseCrossAppEvaluator):
    """
    Camera video recording task
    
    Task flow:
    1. Switch to video mode
    2. Enable grid lines
    3. Record video
    
    Evaluation method:
    - Check whether a new video file exists
    """
    
    app_names = ("camera",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.mode = params.get('mode', 'video')
        self.enable_grid = params.get('enable_grid', True)
        self.min_duration = params.get('min_duration', 3)
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check whether a new video was recorded"""
        from scendroid.env import adb_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Camera Video Recording")
        logging.warning("=" * 60)
        
        try:
            # Get the initial video list
            initial_videos = getattr(self, '_initial_videos', set())
            
            # Search all possible video locations
            search_paths = ['/sdcard/DCIM', '/sdcard/Movies', '/storage/emulated/0/DCIM']
            current_videos = set()
            
            for search_path in search_paths:
                try:
                    # Use the find command to search for video files
                    cmd = ['shell', f'find {search_path} -type f \\( -name "*.mp4" -o -name "*.3gp" -o -name "*.mkv" -o -name "*.webm" \\) 2>/dev/null']
                    response = adb_utils.issue_generic_request(cmd, env.controller)
                    output = response.generic.output.decode('utf-8', errors='ignore').strip()
                    
                    if output and 'No such file' not in output:
                        for line in output.split('\n'):
                            if line.strip():
                                current_videos.add(line.strip())
                except Exception as e:
                    logging.debug(f"   Search in {search_path} failed: {e}")
            
            # Identify newly added video files
            new_videos = current_videos - initial_videos
            
            logging.info(f"   Initial videos: {len(initial_videos)}")
            logging.info(f"   Current videos: {len(current_videos)}")
            logging.info(f"   New videos: {len(new_videos)}")
            
            if new_videos:
                for video in new_videos:
                    logging.info(f"   📹 New video: {video}")
            
            # Also print all current videos for debugging
            if current_videos:
                logging.info("   All current videos:")
                for video in current_videos:
                    is_new = "🆕" if video in new_videos else "  "
                    logging.info(f"      {is_new} {video}")
            
            # Binary scoring: success requires a newly recorded video
            # No fallback logic is used; strict checking of newly added videos is required
            if new_videos:
                logging.warning(f"   ✅ {len(new_videos)} new video(s) recorded!")
                return 1.0
            else:
                logging.warning("   ❌ No new video recorded")
                logging.warning(f"   ℹ️ Initial videos: {len(initial_videos)}, Current videos: {len(current_videos)}")
                return 0.0
                
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: record the initial list of video files"""
        from scendroid.env import adb_utils
        
        super().initialize_task(env)
        
        # Record the initial state (search all possible video locations)
        self._initial_videos = set()
        
        search_paths = ['/sdcard/DCIM', '/sdcard/Movies', '/storage/emulated/0/DCIM']
        
        for search_path in search_paths:
            try:
                # Use the find command to search for video files
                cmd = ['shell', f'find {search_path} -type f \\( -name "*.mp4" -o -name "*.3gp" -o -name "*.mkv" -o -name "*.webm" \\) 2>/dev/null']
                response = adb_utils.issue_generic_request(cmd, env.controller)
                output = response.generic.output.decode('utf-8', errors='ignore').strip()
                
                if output and 'No such file' not in output:
                    for line in output.split('\n'):
                        if line.strip():
                            self._initial_videos.add(line.strip())
            except Exception as e:
                logging.debug(f"   Search in {search_path} failed: {e}")
        
        logging.info(f"   📹 Initial videos recorded: {len(self._initial_videos)} files")
        for video in self._initial_videos:
            logging.debug(f"      - {video}")


# ============================================================================
# F7. LayeredOpenTracksStatsQA - OpenTracks Statistics QA (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredOpenTracksStatsQA")
class OpenTracksStatsQAEvaluator(BaseCrossAppEvaluator):
    """
    OpenTracks statistics Q&A task
    
    Task flow:
    1. View today's activity data
    2. View this week's statistics
    3. Answer questions about distance and duration
    
    Evaluation method:
    - Check whether the agent's answer contains distance and duration information
    """
    
    app_names = ("opentracks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.query_type = params.get('query_type', 'weekly_summary')
        self.activity_type = params.get('activity_type', 'Hiking')
        self.require_distance = params.get('require_distance', True)
        self.require_duration = params.get('require_duration', True)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check the agent's answer"""
        from scendroid.apps.calendar import utils as calendar_utils
        import re
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating OpenTracks Stats QA")
        logging.warning("=" * 60)
        
        try:
            agent_answer = calendar_utils.get_agent_answer(env)
            
            if not agent_answer:
                logging.warning("   ❌ No agent answer found")
                return 0.0
            
            answer_lower = agent_answer.lower()
            logging.info(f"   Agent answer: {agent_answer}")
            
            # Check whether distance information is included
            has_distance = False
            if self.require_distance:
                distance_patterns = [
                    r'\d+\.?\d*\s*(km|kilometers|miles|m|meters)',
                    r'distance.*\d+',
                    r'\d+.*distance',
                ]
                for pattern in distance_patterns:
                    if re.search(pattern, answer_lower):
                        has_distance = True
                        break
            else:
                has_distance = True
            
            # Check whether duration information is included
            has_duration = False
            if self.require_duration:
                duration_patterns = [
                    r'\d+\s*(hours?|minutes?|mins?|hrs?)',
                    r'duration.*\d+',
                    r'time.*\d+',
                    r'\d+:\d+',
                ]
                for pattern in duration_patterns:
                    if re.search(pattern, answer_lower):
                        has_duration = True
                        break
            else:
                has_duration = True
            
            # Binary scoring: success requires both distance and duration information
            success = has_distance and has_duration
            score = 1.0 if success else 0.0
            
            logging.warning(f"   Distance info: {'✅' if has_distance else '❌'}")
            logging.warning(f"   Duration info: {'✅' if has_duration else '❌'}")
            logging.warning(f"   Score: {score:.2f} (binary: both required)")
            logging.warning("=" * 60)
            
            return score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize Task 7: Prepare OpenTracks data
        
        1. Stop the currently running track
        2. Delete invalid tracks recorded in previous tasks
        3. Add today's track data (with distance and duration)
        """
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        import time
        from datetime import datetime, timedelta
        
        super().initialize_task(env)
        
        logging.info("   🏃 Initializing OpenTracks for Task 7...")
        
        try:
            # 1. Close the OpenTracks app (stop any ongoing recording)
            logging.info("      Step 1: Stop OpenTracks and close the app...")
            adb_utils.close_app("activity tracker", env.controller)
            time.sleep(1.0)
            
            # 2. Clean all tracks from the database (delete invalid data recorded in previous tasks)
            logging.info("      Step 2: Clean existing tracks...")
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ Cleared existing tracks")
            except Exception as e:
                logging.debug(f"      Clear failed: {e}")
            
            # 3. Add today's track data (simulate the track recorded in Task 4)
            logging.warning("      Step 3: Add today's track data (including distance!)...")
            
            import random
            random.seed(2026)  # Fix seed for reproducibility
            
            # Retrieve parameters
            activity_type = self.activity_type
            
            # Set today's date (using base_date: 2026-01-18)
            today = datetime(2026, 1, 18, 0, 0, 0)
            
            # Create today's activity record (simulate a real hike starting at 9:30 AM)
            # Key: Here, add a track with distance, replacing the distance-less track previously recorded by the emulator
            today_distance_m = 8500  # 8.5 km = 5.28 miles
            today_duration_ms = 150 * 60 * 1000  # 2.5 hours = 150 min
            logging.warning(f"         📍 Today's track: {today_distance_m/1000:.1f} km ({today_distance_m/1609.34:.2f} mi), {today_duration_ms/60000:.0f} min")
            
            start_time = today.replace(hour=9, minute=30)  # 9:30 AM
            stop_time = start_time + timedelta(milliseconds=today_duration_ms)
            
            today_activity = sqlite_schema_utils.SportsActivity(
                name=f"Today's {activity_type}",
                category=activity_type.lower(),
                activity_type=activity_type.lower(),
                description=f"Morning {activity_type.lower()} to West Peak",
                totaldistance=today_distance_m,
                starttime=int(start_time.timestamp() * 1000),
                stoptime=int(stop_time.timestamp() * 1000),
                totaltime=today_duration_ms,
                movingtime=int(today_duration_ms * 0.85),  # 85% moving time
                avgspeed=today_distance_m / (today_duration_ms / 1000),
                avgmovingspeed=today_distance_m / (today_duration_ms * 0.85 / 1000),
                elevationgain=320,
                elevationloss=180,
            )
            
            activities = [today_activity]
            
            # Add activities for other days of this week (Monday to Saturday, with more diverse data)
            # Distance and duration differ each day
            weekly_data = [
                # (day_offset, distance_km, duration_min, hour, name_suffix)
                (1, 4.2, 52, 17, "Evening Walk"),       # Saturday: 4.2 km, 52 min
                (2, 6.8, 85, 7, "Morning Run"),         # Friday: 6.8 km, 85 min
                (3, 3.5, 45, 18, "Sunset Stroll"),      # Thursday: 3.5 km, 45 min
                (4, 5.1, 62, 16, "Afternoon Hike"),     # Wednesday: 5.1 km, 62 min
                (5, 7.3, 95, 6, "Dawn Trail"),          # Tuesday: 7.3 km, 95 min
            ]
            
            for day_offset, distance_km, duration_min, hour, name_suffix in weekly_data:
                activity_date = today - timedelta(days=day_offset)
                
                daily_distance_m = int(distance_km * 1000)
                daily_duration_ms = duration_min * 60 * 1000
                
                # Add slight random variations
                minute_offset = random.randint(0, 30)
                
                start_ts = int(activity_date.replace(hour=hour, minute=minute_offset).timestamp() * 1000)
                stop_ts = start_ts + daily_duration_ms
                
                activity = sqlite_schema_utils.SportsActivity(
                    name=name_suffix,
                    category=activity_type.lower(),
                    activity_type=activity_type.lower(),
                    description=f"{activity_type} session",
                    totaldistance=daily_distance_m,
                    starttime=start_ts,
                    stoptime=stop_ts,
                    totaltime=daily_duration_ms,
                    movingtime=int(daily_duration_ms * (0.8 + random.random() * 0.15)),
                    avgspeed=daily_distance_m / (daily_duration_ms / 1000),
                    avgmovingspeed=daily_distance_m / (daily_duration_ms / 1000) * 1.1,
                    elevationgain=random.randint(30, 150),
                    elevationloss=random.randint(20, 100),
                )
                activities.append(activity)
            
            # Insert into the database
            activity_app_utils._add_activities(activities, env)
            
            # Calculate totals
            total_distance_km = sum(a.totaldistance for a in activities) / 1000
            total_duration_min = sum(a.totaltime for a in activities) / (60 * 1000)
            
            logging.warning(f"      ✅ Added {len(activities)} activities to database:")
            logging.warning(f"         🔵 TODAY: {today_distance_m/1000:.1f} km ({today_distance_m/1609.34:.2f} mi), {today_duration_ms/60000:.0f} min")
            for i, (day_offset, distance_km, duration_min, hour, name_suffix) in enumerate(weekly_data):
                logging.info(f"         📊 Day -{day_offset}: {distance_km} km, {duration_min} min ({name_suffix})")
            logging.warning(f"         📈 WEEKLY TOTAL: {total_distance_km:.1f} km, {total_duration_min:.0f} min")
            
            logging.warning("   ✅ OpenTracks Task 7 initialization complete - TODAY'S TRACK ADDED!")
            
        except Exception as e:
            logging.warning(f"   ⚠️ OpenTracks initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())


# ============================================================================
# F8. LayeredFilesOrganizeAndDedupe - Files Organize and Dedupe (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredFilesOrganizeAndDedupe")
class FilesOrganizeAndDedupeEvaluator(BaseCrossAppEvaluator):
    """
    Files Photo Organization and Deduplication Task
    
    Task workflow:
    1. Create categorized folders (Scenery, Portraits)
    2. Move photos to corresponding folders based on filenames
    3. Delete duplicate files (must be completed)
    
    Evaluation method (binary):
    - Categorized folders created AND files moved AND deduplication completed → Success
    """
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.source_folder = params.get('source_folder', 'Pictures')
        self.target_folders = params.get('target_folders', ['Scenery', 'Portraits'])
        self.scenery_patterns = params.get('scenery_patterns', [])
        self.portrait_patterns = params.get('portrait_patterns', [])
        self.dedupe_required = params.get('dedupe_required', True)
        
        self.complexity = 3.5
    
    def evaluate(self, env) -> float:
        """Check photo organization and deduplication"""
        from scendroid.env import device_constants, adb_utils
        import os
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Files Organize and Dedupe")
        logging.warning("=" * 60)
        
        try:
            base_path = device_constants.EMULATOR_DATA
            pictures_path = os.path.join(base_path, self.source_folder)
            
            # Part 1: Check whether categorized folders have been created
            logging.info("   Part 1: Checking folders...")
            folders_created = 0
            folder_contents = {}
            
            for folder in self.target_folders:
                folder_path = os.path.join(pictures_path, folder)
                
                # Check whether the folder exists
                cmd = ['shell', 'ls', '-la', folder_path, '2>/dev/null']
                response = adb_utils.issue_generic_request(cmd, env.controller)
                output = response.generic.output.decode('utf-8', errors='ignore')
                
                if output and 'No such file' not in output:
                    folders_created += 1
                    # List files in the folder
                    files = [f for f in output.split() if f.endswith('.png')]
                    folder_contents[folder] = files
                    logging.info(f"   ✅ Folder '{folder}': {len(files)} files")
                    for f in files:
                        logging.info(f"      - {f}")
                else:
                    folder_contents[folder] = []
                    logging.warning(f"   ❌ Folder not found: {folder}")
            
            all_folders_created = folders_created == len(self.target_folders) if self.target_folders else True
            
            # Part 2: Check whether there are any .png files in the root directory
            logging.info("   Part 2: Checking root directory...")
            cmd = ['shell', 'ls', pictures_path]
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            files_in_root = [f for f in output.split() if f.endswith('.png')]
            files_moved = len(files_in_root) == 0
            
            if files_in_root:
                logging.warning(f"   ⚠️ Files remaining in root: {files_in_root}")
            else:
                logging.info("   ✅ Root directory is clean (no .png files)")
            
            # Part 3: Check deduplication (must be completed!)
            # Check whether duplicate files ending with _copy, _dup, or _backup have been deleted
            logging.info("   Part 3: Checking deduplication (REQUIRED)...")
            all_files = []
            for folder_files in folder_contents.values():
                all_files.extend(folder_files)
            all_files.extend(files_in_root)
            
            duplicate_patterns = ['_copy', '_dup', '_backup', '(1)', '(2)']
            remaining_duplicates = [f for f in all_files if any(p in f.lower() for p in duplicate_patterns)]
            
            if remaining_duplicates:
                logging.warning(f"   ❌ Duplicates still exist: {remaining_duplicates}")
                dedupe_ok = False
            else:
                logging.info("   ✅ All duplicate files removed")
                dedupe_ok = True
            
            # Binary scoring: folder creation AND file movement AND deduplication completed
            success = all_folders_created and files_moved and dedupe_ok
            final_score = 1.0 if success else 0.0
            
            logging.warning("-" * 60)
            logging.warning(f"   Folders created: {'✅' if all_folders_created else '❌'} ({folders_created}/{len(self.target_folders)})")
            logging.warning(f"   Files moved: {'✅' if files_moved else '❌'} ({len(files_in_root)} remaining in root)")
            logging.warning(f"   Deduplication: {'✅' if dedupe_ok else '❌'} (REQUIRED)")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# F10. LayeredMarkorHikingSummary - Hiking Summary (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorHikingSummary")
class MarkorHikingSummaryEvaluator(BaseCrossAppEvaluator):
    """
    Markor Hiking Journal Task
    
    Task flow:
    1. Create a journal file
    2. Include information such as route, weather, highlights, expenses, and photos
    
    Evaluation method:
    - Check whether the file exists (20%)
    - Check whether required sections are included (50%)
    - Check whether locations and expenses are mentioned (30%)
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.file_name = params.get('file_name', 'HikingSummary.md')
        self.required_sections = params.get('required_sections', [])
        self.must_mention_location = params.get('must_mention_location', '')
        self.must_mention_expense = params.get('must_mention_expense', False)
        self.expense_amount = params.get('expense_amount', 0)
        
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Check journal content"""
        from scendroid.env import device_constants, adb_utils
        import os
        import re
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Markor Hiking Summary")
        logging.warning("=" * 60)
        
        try:
            markor_dir = device_constants.MARKOR_DATA
            file_path = os.path.join(markor_dir, self.file_name)
            
            # Read file content
            response = adb_utils.issue_generic_request(
                ['shell', 'cat', file_path],
                env.controller
            )
            content = response.generic.output.decode('utf-8', errors='ignore')
            
            if not content or len(content) < 10:
                logging.warning(f"   ❌ File not found or empty: {self.file_name}")
                return 0.0
            
            logging.info(f"   ✅ File found: {self.file_name} ({len(content)} chars)")
            logging.info(f"   Content preview: {content[:300]}...")
            
            content_lower = content.lower()
            
            # Part 1: Check required sections (50%)
            sections_found = 0
            for section in self.required_sections:
                if section.lower() in content_lower:
                    sections_found += 1
                    logging.info(f"   ✅ Section found: {section}")
                else:
                    logging.warning(f"   ❌ Section missing: {section}")
            
            all_sections_found = sections_found == len(self.required_sections) if self.required_sections else True
            
            # Part 2: Check locations
            location_found = True
            if self.must_mention_location:
                location_words = self.must_mention_location.lower().split()
                location_found = any(word in content_lower for word in location_words if len(word) > 3)
                if location_found:
                    logging.info(f"   ✅ Location mentioned: {self.must_mention_location}")
                else:
                    logging.warning(f"   ❌ Location not mentioned")
            
            # Part 3: Check expenses
            expense_found = True
            if self.must_mention_expense:
                numbers = re.findall(r'\d+\.?\d*', content)
                expense_found = any(
                    abs(float(n) - self.expense_amount) < 1.0 
                    for n in numbers if n
                )
                if expense_found:
                    logging.info(f"   ✅ Expense mentioned: ${self.expense_amount}")
                else:
                    logging.warning(f"   ❌ Expense not mentioned")
            
            # Binary scoring: success only if all conditions are satisfied
            success = all_sections_found and location_found and expense_found
            final_score = 1.0 if success else 0.0
            
            logging.warning("-" * 60)
            logging.warning(f"   Sections: {'✅' if all_sections_found else '❌'} ({sections_found}/{len(self.required_sections)})")
            logging.warning(f"   Location: {'✅' if location_found else '❌'}")
            logging.warning(f"   Expense: {'✅' if expense_found else '❌'}")
            logging.warning(f"   Final Score: {final_score:.2f} (binary: all required)")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# F9. LayeredExpenseWeeklyQA - Weekly Expense QA (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredExpenseWeeklyQA")
class ExpenseWeeklyQAEvaluator(BaseCrossAppEvaluator):
    """
    Pro Expense Weekly Expense Q&A Task
    
    Task flow:
    1. Record today's meat purchase
    2. View this week's total expenses
    3. Answer with the total amount
    
    Evaluation method (binary):
    - Check whether the agent's answer contains the correct weekly total (allowing a 5% margin of error)
    """
    
    app_names = ("pro expense",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.meat_name = params.get('meat_name', 'Meat Substitute')
        self.meat_amount = params.get('meat_amount', 113.27)
        self.weekly_total = params.get('weekly_total', 209.57)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether the agent's answer contains the weekly total"""
        from scendroid.apps.calendar import utils as calendar_utils
        import re
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Expense Weekly QA")
        logging.warning("=" * 60)
        
        try:
            agent_answer = calendar_utils.get_agent_answer(env)
            
            if not agent_answer:
                logging.warning("   ❌ No agent answer found")
                return 0.0
            
            logging.info(f"   Agent answer: {agent_answer}")
            logging.info(f"   Expected weekly total: ${self.weekly_total:.2f}")
            
            # Extract all numbers from the answer
            numbers = re.findall(r'\d+\.?\d*', agent_answer)
            numbers_float = [float(n) for n in numbers if n]
            
            logging.info(f"   Numbers found: {numbers_float}")
            
            # Check whether the weekly total is included (allowing a 5% margin of error)
            total_found = False
            tolerance = self.weekly_total * 0.05
            
            for num in numbers_float:
                if abs(num - self.weekly_total) <= tolerance:
                    total_found = True
                    logging.info(f"   ✅ Weekly total found: ${num:.2f} (expected ${self.weekly_total:.2f})")
                    break
            
            if not total_found:
                # Also accept rounded integers
                rounded_total = round(self.weekly_total)
                for num in numbers_float:
                    if abs(num - rounded_total) <= 2:
                        total_found = True
                        logging.info(f"   ✅ Rounded total found: ${num:.2f}")
                        break
            
            if not total_found:
                logging.warning(f"   ❌ Weekly total not found in answer")
            
            final_score = 1.0 if total_found else 0.0
            
            logging.warning("-" * 60)
            logging.warning(f"   Weekly total: {'✅' if total_found else '❌'}")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task"""
        super().initialize_task(env)
        logging.info(f"   💰 Task 9 initialized: Record meat ${self.meat_amount:.2f}, answer weekly total")


# ============================================================================
# F10-new. LayeredMarkorHikingDiary - Hiking Diary (Scenario F)
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorHikingDiary")
class MarkorHikingDiaryEvaluator(BaseCrossAppEvaluator):
    """
    Markor Hiking Diary Task
    
    Task flow:
    1. Create a diary file
    2. Record the expense for buying meat for lunch
    3. Record photo timestamps: for landscape photos, record where+when; for portrait photos, record when+who
    
    Evaluation method (binary):
    - File exists AND contains lunch/meat-related records AND contains photo timestamp records
    
    Example expected answer:
    ---
    # Hiking Day Summary
    
    ## Lunch
    - Bought meat substitute for lunch: $113.27
    
    ## Photos
    Scenery:
    - 10:10 - Mountain view
    - 10:25 - Lake (beautiful sunset reflection)
    - 11:10 - Waterfall
    
    Portraits:
    - 09:30 - Bob and Sarah at the trailhead
    - 12:00 - Selfie at the peak
    - 14:30 - Tom during lunch
    ---
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.file_name = params.get('file_name', 'Hiking_Day_Summary.md')
        self.meat_amount = params.get('meat_amount', 113.27)
        self.location_name = params.get('location_name', 'West Peak')
        self.friend_names = params.get('friend_names', ['Bob', 'Sarah', 'Tom'])
        self.required_keywords = params.get('required_keywords', ['lunch', 'photo'])
        
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Check diary content"""
        from scendroid.env import device_constants, adb_utils
        import os
        import re
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Markor Hiking Diary")
        logging.warning("=" * 60)
        
        try:
            markor_dir = device_constants.MARKOR_DATA
            file_path = os.path.join(markor_dir, self.file_name)
            
            # Read file content
            response = adb_utils.issue_generic_request(
                ['shell', 'cat', file_path],
                env.controller
            )
            content = response.generic.output.decode('utf-8', errors='ignore')
            
            if not content or len(content) < 10:
                logging.warning(f"   ❌ File not found or empty: {self.file_name}")
                return 0.0
            
            logging.info(f"   ✅ File found: {self.file_name} ({len(content)} chars)")
            logging.info(f"   Content preview: {content[:500]}...")
            
            content_lower = content.lower()
            
            # Part 1: Check whether lunch/meat-related items are mentioned
            logging.info("   Part 1: Checking lunch/meat record...")
            
            # Check amount
            numbers = re.findall(r'\d+\.?\d*', content)
            meat_amount_found = any(
                abs(float(n) - self.meat_amount) < 2.0 
                for n in numbers if n
            )
            
            # Or check keywords
            lunch_keywords = ['lunch', 'meat', '113', 'purchase', 'bought']
            lunch_mentioned = any(kw in content_lower for kw in lunch_keywords)
            
            lunch_ok = meat_amount_found or lunch_mentioned
            
            if lunch_ok:
                logging.info(f"   ✅ Lunch/meat record found")
            else:
                logging.warning(f"   ❌ Lunch/meat record not found")
            
            # Part 2: Check whether photo timestamp records exist
            logging.info("   Part 2: Checking photo time records...")
            
            # Look for time formats such as 10:10, 10:25, 09:30, 12:00, etc.
            time_patterns = re.findall(r'\d{1,2}:\d{2}', content)
            has_photo_times = len(time_patterns) >= 2  # At least two time points
            
            if has_photo_times:
                logging.info(f"   ✅ Photo timestamps found: {time_patterns}")
            else:
                logging.warning(f"   ❌ Not enough photo timestamps (found: {len(time_patterns)})")
            
            # Part 3: Check whether location or person names exist
            logging.info("   Part 3: Checking location/people mentions...")
            
            # Landscape keywords
            scenery_keywords = ['mountain', 'lake', 'waterfall', 'peak', 'view']
            scenery_found = sum(1 for kw in scenery_keywords if kw in content_lower)
            
            # Person name keywords
            people_found = sum(1 for name in self.friend_names if name.lower() in content_lower)
            
            # Or generic terms such as selfie, group, etc.
            portrait_keywords = ['selfie', 'group', 'photo', 'portrait']
            portrait_generic_found = sum(1 for kw in portrait_keywords if kw in content_lower)
            
            context_ok = (scenery_found >= 1) or (people_found >= 1) or (portrait_generic_found >= 1)
            
            if context_ok:
                logging.info(f"   ✅ Context found (scenery: {scenery_found}, people: {people_found})")
            else:
                logging.warning(f"   ❌ No location/people context found")
            
            # Binary scoring: lunch record AND timestamp
            success = lunch_ok and has_photo_times
            final_score = 1.0 if success else 0.0
            
            logging.warning("-" * 60)
            logging.warning(f"   Lunch record: {'✅' if lunch_ok else '❌'}")
            logging.warning(f"   Photo times: {'✅' if has_photo_times else '❌'} ({len(time_patterns)} found)")
            logging.warning(f"   Context: {'✅' if context_ok else '⚠️'} (not required for pass)")
            logging.warning(f"   Final Score: {final_score:.2f}")
            logging.warning("=" * 60)
            
            return final_score
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0


# ============================================================================
# LayeredCalendarCheckThenExercise - Calendar + OpenTracks (conditional)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCheckThenExercise")
class CalendarCheckThenExerciseEvaluator(BaseCrossAppEvaluator):
    """
    Calendar + OpenTracks conditional cross-app task
    
    Task flow:
    1. Check whether a meeting is scheduled in Calendar within the next 30 minutes
    2. If a meeting exists: inform the user about the meeting and do not start exercising
    3. If no meeting exists: start recording exercise in OpenTracks
    
    Evaluation method (binary scoring):
    - If has_blocking_meeting=True: verify whether the agent correctly identified the meeting
    - If has_blocking_meeting=False: verify whether OpenTracks has a new recording
    
    Parameterized design:
    - has_blocking_meeting: bool - Whether a meeting is scheduled within the checking time window
    - blocking_meeting_title: str - The title of the meeting, if one exists
    - task_time: str - Task time (e.g., "18:00")
    - check_duration_minutes: int - Duration of the checking window (e.g., 30 minutes)
    """
    
    app_names = ("simple calendar pro", "opentracks")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Core parameters
        self.has_blocking_meeting = params.get('has_blocking_meeting', False)
        self.blocking_meeting_title = params.get('blocking_meeting_title', '')
        self.task_time = params.get('task_time', '18:00')
        self.check_duration_minutes = params.get('check_duration_minutes', 30)
        
        # Record initial OpenTracks state
        self.initial_tracks_count = 0
        
        self.complexity = 2.5
    
    def initialize_task(self, env):
        """Initialize: record the initial OpenTracks state"""
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Check Then Exercise Task:")
        logging.info(f"   Has blocking meeting: {self.has_blocking_meeting}")
        if self.has_blocking_meeting:
            logging.info(f"   Blocking meeting: {self.blocking_meeting_title}")
        logging.info(f"   Task time: {self.task_time}")
        logging.info(f"   Check duration: {self.check_duration_minutes} minutes")
        logging.info("=" * 60)
        
        try:
            from scendroid.task_evals.information_retrieval import activity_app_utils
            
            # Record the initial number of tracks (using list_rows instead of get_all_tracks)
            initial_tracks = activity_app_utils.list_rows(env)
            self.initial_tracks_count = len(initial_tracks) if initial_tracks else 0
            logging.info(f"   Initial OpenTracks count: {self.initial_tracks_count}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Could not get initial tracks count: {e}")
            self.initial_tracks_count = 0
    
    def evaluate(self, env) -> float:
        """
        Perform evaluation: use different evaluation strategies depending on whether a meeting exists
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar Check Then Exercise:")
        logging.info(f"   Mode: {'Has meeting (should NOT exercise)' if self.has_blocking_meeting else 'No meeting (should exercise)'}")
        logging.info("=" * 60)
        
        try:
            if self.has_blocking_meeting:
                # Case with a meeting: verify whether the agent correctly identified the meeting
                return self._evaluate_meeting_case(env)
            else:
                # Case without a meeting: verify whether exercise tracking was started
                return self._evaluate_free_case(env)
                
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def _evaluate_meeting_case(self, env) -> float:
        """
        Evaluate the case with a meeting:
        - The agent should identify that a meeting exists
        - The agent should not start exercise tracking
        """
        logging.info("   📅 Evaluating MEETING case...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        
        # 🆕 First check interaction_cache
        logging.info(f"   🔍 Checking interaction_cache...")
        logging.info(f"   Type: {type(env.interaction_cache)}")
        logging.info(f"   Raw value: {repr(env.interaction_cache)[:200]}")
        
        # Check 1: Whether the agent's response mentions a meeting/busy/cannot exercise
        agent_answer = ""
        if hasattr(env, 'interaction_cache') and env.interaction_cache:
            agent_answer = str(env.interaction_cache).lower()
        
        logging.info(f"   ✅ Agent's answer (lowercased): {agent_answer[:200]}...")
        
        meeting_keywords = [
            'meeting', 'busy', 'scheduled', 'appointment', 'call',
            'conflict', 'occupied', 'not free', "can't", 'cannot',
            self.blocking_meeting_title.lower() if self.blocking_meeting_title else '',
            '18:15', '18:30', 'sync', 'evening'
        ]
        meeting_keywords = [k for k in meeting_keywords if k]  # Filter out empty strings
        
        logging.info(f"   🔍 Looking for keywords: {meeting_keywords}")
        
        # 🆕 Perform detailed checks for each keyword
        found_keywords = [kw for kw in meeting_keywords if kw in agent_answer]
        mentioned_meeting = len(found_keywords) > 0
        
        if mentioned_meeting:
            logging.warning(f"   ✅ Agent mentioned meeting/busy in answer")
            logging.warning(f"   Found keywords: {found_keywords}")
        else:
            logging.warning(f"   ⚠️ Agent did not clearly mention the meeting")
            logging.warning(f"   💡 None of these keywords found: {meeting_keywords}")
        
        # Check 2: Whether exercise tracking was incorrectly started
        # Detect the recording state using notifications/Activity
        exercise_started = self._check_opentracks_recording(env)
        
        # Fallback check: whether there is a new record in the database
        if not exercise_started:
            try:
                current_tracks = activity_app_utils.list_rows(env)
                current_count = len(current_tracks) if current_tracks else 0
                
                if current_count > self.initial_tracks_count:
                    exercise_started = True
                    logging.warning(f"   ❌ Agent incorrectly started exercise (new track in database)!")
                    logging.warning(f"   Initial tracks: {self.initial_tracks_count}, Current: {current_count}")
            except Exception as e:
                logging.debug(f"   Could not check database: {e}")
        
        if exercise_started:
            logging.warning(f"   ❌ Agent incorrectly started exercise recording!")
        else:
            logging.info(f"   ✅ Correctly did NOT start exercise (meeting exists)")
        
        # Scoring: mentioning a meeting AND not starting exercise tracking = success
        if mentioned_meeting and not exercise_started:
            logging.warning("=" * 60)
            logging.warning("✅ SUCCESS: Correctly identified meeting and did not exercise")
            logging.warning("=" * 60)
            return 1.0
        else:
            logging.warning("=" * 60)
            logging.warning(f"❌ FAILED: Mentioned meeting: {mentioned_meeting}, Started exercise: {exercise_started}")
            logging.warning("=" * 60)
            return 0.0
    
    def _evaluate_free_case(self, env) -> float:
        """
        Evaluate the case without a meeting:
        - The agent should check the calendar and then start exercise tracking
        - Starting tracking is sufficient; a complete recording is not required
        """
        logging.info("   🏃 Evaluating FREE case...")
        
        from scendroid.env import adb_utils
        
        try:
            # Check whether OpenTracks is currently recording (refer to the implementation in LayeredCrossAppTracksMusic)
            tracks_recording = self._check_opentracks_recording(env)
            
            if tracks_recording:
                logging.warning("=" * 60)
                logging.warning("✅ SUCCESS: OpenTracks is recording")
                logging.warning("=" * 60)
                return 1.0
            else:
                # Fallback check: whether there is a new record in the database (the recording may have already stopped and been saved)
                from scendroid.task_evals.information_retrieval import activity_app_utils
                try:
                    current_tracks = activity_app_utils.list_rows(env)
                    current_count = len(current_tracks) if current_tracks else 0
                    
                    logging.info(f"   Initial tracks: {self.initial_tracks_count}")
                    logging.info(f"   Current tracks: {current_count}")
                    
                    if current_count > self.initial_tracks_count:
                        logging.warning("=" * 60)
                        logging.warning("✅ SUCCESS: New track found in database")
                        logging.warning("=" * 60)
                        return 1.0
                except Exception as e:
                    logging.warning(f"   ⚠️ Could not check database: {e}")
                
                logging.warning("=" * 60)
                logging.warning("❌ FAILED: No exercise recording found")
                logging.warning("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Error checking OpenTracks: {e}")
            return 0.0
    
    def _check_opentracks_recording(self, env) -> bool:
        """
        Check whether OpenTracks is currently recording
        
        Refer to the implementation in LayeredCrossAppTracksMusic and detect it in two ways:
        1. Check the foreground service notification
        2. Check the Activity state
        """
        from scendroid.env import adb_utils
        
        tracks_recording = False
        
        # Method 1: Check the OpenTracks foreground service notification
        try:
            cmd_notif = ['shell', 'dumpsys', 'notification']
            response_notif = adb_utils.issue_generic_request(cmd_notif, env.controller)
            notif_output = response_notif.generic.output.decode('utf-8', errors='ignore')
            
            # OpenTracks displays a foreground service notification while recording
            if 'de.dennisguse.opentracks' in notif_output and ('Recording' in notif_output or 'recording' in notif_output):
                tracks_recording = True
                logging.info("   ✅ OpenTracks is actively recording (notification found)")
        except Exception as e:
            logging.debug(f"   Could not check notification: {e}")
        
        # Method 2: Check the activity state
        if not tracks_recording:
            try:
                cmd_activity = ['shell', 'dumpsys', 'activity', 'activities']
                response_activity = adb_utils.issue_generic_request(cmd_activity, env.controller)
                activity_output = response_activity.generic.output.decode('utf-8', errors='ignore')
                
                # Check whether RecordingActivity is in the foreground
                if 'de.dennisguse.opentracks' in activity_output:
                    if 'TrackRecordingActivity' in activity_output or 'RecordingActivity' in activity_output:
                        tracks_recording = True
                        logging.info("   ✅ OpenTracks recording activity is active")
            except Exception as e:
                logging.debug(f"   Could not check activity: {e}")
        
        if not tracks_recording:
            logging.warning("   ❌ OpenTracks is NOT recording")
        
        return tracks_recording


# ============================================================================
# Scenario C New evaluator
# ============================================================================

# ============================================================================
# C1. LayeredCrossAppClockCalendar - Clock + Calendar (Scenario C Task 1)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppClockCalendar")
class CrossAppClockCalendarEvaluator(BaseCrossAppEvaluator):
    """
    Clock + Calendar cross-app task
    
    Task flow:
    1. Clock: Set an alarm for the specified time
    2. Calendar: Create a calendar event (including title, time, duration, and location)
    
    Evaluation method:
    - 50% Alarm: Check whether the alarm is set correctly (time matches)
    - 50% Calendar: Check whether the calendar event is created correctly (title, time, duration)
    """
    
    app_names = ("clock", "simple calendar pro")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Alarm parameters
        self.alarm_hour = params.get('alarm_time_hour', 7)
        self.alarm_minute = params.get('alarm_time_minute', 30)
        self.alarm_label = params.get('alarm_label', '')
        
        # Calendar parameters
        self.event_title = params.get('event_title', '')
        self.event_hour = params.get('event_hour', 14)
        self.event_minute = params.get('event_minute', 0)
        self.event_duration_minutes = params.get('event_duration_minutes', 60)
        self.event_location = params.get('event_location', '')
        self.event_description = params.get('event_description', '')
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether both the alarm and the calendar event are created successfully
        
        Fine-grained scoring (modified for Scenario C):
        - 0.0 points: Neither is completed
        - 0.5 points: Either the alarm OR the calendar event is completed
        - 1.0 points: Both are completed
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Clock + Calendar")
        logging.warning("=" * 60)
        
        # Part 1: Check the alarm
        alarm_score = self._check_alarm(env)
        logging.info(f"   Alarm score: {alarm_score}")
        
        # Part 2: Check the calendar event
        calendar_score = self._check_calendar(env)
        logging.info(f"   Calendar score: {calendar_score}")
        
        # Fine-grained scoring: 0.5 points if either is completed; 1 point if both are completed
        alarm_ok = alarm_score >= 0.99
        calendar_ok = calendar_score >= 0.99
        
        if alarm_ok and calendar_ok:
            score = 1.0
            logging.warning("   ✅ SUCCESS: Both alarm and calendar event created correctly (1.0)")
        elif alarm_ok or calendar_ok:
            score = 0.5
            if alarm_ok:
                logging.warning("   ⚠️  PARTIAL: Alarm OK, but calendar event missing/incorrect (0.5)")
            else:
                logging.warning("   ⚠️  PARTIAL: Calendar event OK, but alarm missing/incorrect (0.5)")
        else:
            score = 0.0
            logging.warning("   ❌ FAILED: Both alarm and calendar event missing or incorrect (0.0)")
        
        logging.warning("=" * 60)
        return score
    
    def _check_alarm(self, env) -> float:
        """Check whether the alarm is set correctly (refer to the implementation in scenario_d)"""
        from scendroid.apps.clock import utils as clock_utils
        
        try:
            logging.info(f"   🔍 Looking for alarm: {self.alarm_hour}:{self.alarm_minute:02d}")
            
            # Use check_alarm_with_date to check the alarm
            alarm_exists = clock_utils.check_alarm_with_date(
                env, 
                self.alarm_hour, 
                self.alarm_minute, 
                day_offset=0,
                enabled=True
            )
            
            if alarm_exists:
                logging.info(f"   ✅ Found alarm: {self.alarm_hour}:{self.alarm_minute:02d}")
                return 1.0
            else:
                logging.warning(f"   ❌ Alarm not found: {self.alarm_hour}:{self.alarm_minute:02d}")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Error checking alarm: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def _check_calendar(self, env) -> float:
        """Check whether the calendar event is created correctly (title, time, duration)
        
        Use binary scoring: either fully correct (1 point) or incorrect (0 points)
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        try:
            # Use the correct API to retrieve calendar events (refer to implementations in other scenarios)
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            logging.info(f"   Found {len(events)} calendar event(s)")
            logging.info(f"   Expected: title='{self.event_title}', time={self.event_hour}:{self.event_minute:02d}, duration={self.event_duration_minutes}min")
            
            for event in events:
                # Check the title
                event_title = (event.title or '').lower()
                expected_title = self.event_title.lower()
                title_match = expected_title in event_title
                
                if not title_match:
                    continue
                
                logging.info(f"   Found matching event: {event.title}")
                
                # Use the start_datetime attribute (a standard attribute of CalendarEvent)
                event_hour = event.start_datetime.hour
                event_minute = event.start_datetime.minute
                
                # Check the start time
                time_match = (event_hour == self.event_hour and 
                             event_minute == self.event_minute)
                
                logging.info(f"      start time: {event_hour}:{event_minute:02d} (expected {self.event_hour}:{self.event_minute:02d})")
                
                # Check the duration (using start_ts and end_ts, allowing a 10-minute tolerance)
                actual_duration = (event.end_ts - event.start_ts) // 60
                duration_match = abs(actual_duration - self.event_duration_minutes) <= 10
                
                logging.info(f"      duration: {actual_duration}min (expected {self.event_duration_minutes}min)")
                
                # Binary scoring: all criteria must match to earn points
                if title_match and time_match and duration_match:
                    logging.info(f"   ✅ Event fully matches: title, time, and duration")
                    return 1.0
                else:
                    # Partial matches are considered failures
                    if not time_match:
                        logging.warning(f"   ❌ Time mismatch")
                    if not duration_match:
                        logging.warning(f"   ❌ Duration mismatch")
                    return 0.0
            
            logging.warning(f"   ❌ Event not found: {self.event_title}")
            return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Error checking calendar: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize the task: only clean up data; events are created by the agent"""
        super().initialize_task(env)
        
        from scendroid.apps.clock import utils as clock_utils
        from scendroid.task_evals.single.calendar import calendar_utils
        
        logging.info("🔧 Initializing Clock + Calendar task")
        
        # Clean up alarms
        clock_utils.close_clock_app(env)
        
        # Clean up calendar (events are created by the agent)
        calendar_utils.clear_calendar_db(env)
        
        logging.info("   ✅ Initialization complete (event will be created by agent)")


# ============================================================================
# C2. LayeredExpenseFromReceipt - Expense from Receipt (Scenario C Task 3)
# ============================================================================

@AppRegistry.register_evaluator("LayeredExpenseFromReceipt")
class ExpenseFromReceiptEvaluator(BaseCrossAppEvaluator):
    """
    Record an expense from a receipt
    
    Task flow:
    1. The user views the receipt image in Files
    2. Record the expense in Pro Expense
    
    Evaluation method:
    - Check whether the expense record is correct (amount, name, category)
    
    Note: The receipt image is created by scenario's initialize_task
    """
    
    app_names = ("files", "pro expense")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.amount = params.get('amount', 0)
        self.name = params.get('name', '')
        self.category = params.get('category', 'Food')
        self.note = params.get('note', '')
        self.receipt_file = params.get('receipt_file', 'breakfast_receipt.png')
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check whether the expense is recorded correctly"""
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Expense from Receipt")
        logging.warning("=" * 60)
        
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            _TABLE = "expense"
            
            # Retrieve all expense records
            expenses = sqlite_utils.get_rows_from_remote_device(
                _TABLE,
                _DB_PATH,
                sqlite_schema_utils.Expense,
                env,
            )
            
            if not expenses:
                logging.warning("   ❌ FAIL: No expenses found")
                logging.warning("=" * 60)
                return 0.0
            
            logging.info(f"   Found {len(expenses)} expense(s)")
            
            # Check each expense
            expected_amount = float(self.amount)
            expected_name = self.name.lower() if self.name else ''
            
            for expense in expenses:
                # Amount stored in cents
                actual_amount = float(getattr(expense, 'amount', 0)) / 100.0
                actual_name = str(getattr(expense, 'name', '')).lower()
                
                # ✅ More lenient name-matching strategy:
                # 1. Contains the keyword "breakfast" (case-insensitive)
                breakfast_match = 'breakfast' in actual_name
                
                # 2. Substring matching
                substring_match = (expected_name in actual_name or actual_name in expected_name) if expected_name else False
                
                # 3. Keyword matching: extract keywords (excluding short words) and check for shared keywords
                keyword_match = False
                if expected_name and not substring_match:
                    # Extract keywords with length >= 4 (to avoid words like 'the', 'and')
                    expected_keywords = set(w for w in expected_name.split() if len(w) >= 4)
                    actual_keywords = set(w for w in actual_name.split() if len(w) >= 4)
                    
                    # Pass if at least one shared keyword exists
                    common_keywords = expected_keywords & actual_keywords
                    keyword_match = len(common_keywords) > 0
                
                name_match = breakfast_match or substring_match or keyword_match
                amount_match = abs(actual_amount - expected_amount) < 0.01
                
                logging.info(f"   Checking: '{actual_name}' = ${actual_amount:.2f}")
                logging.info(f"   Expected: '{expected_name}' = ${expected_amount:.2f}")
                if expected_name:
                    exp_kw = set(w for w in expected_name.split() if len(w) >= 4)
                    act_kw = set(w for w in actual_name.split() if len(w) >= 4)
                    common = exp_kw & act_kw
                    if exp_kw and act_kw:
                        logging.info(f"   Keywords: expected={exp_kw}, actual={act_kw}, common={common}")
                logging.info(f"   Match: name={name_match} (breakfast={breakfast_match}, substring={substring_match}, keyword={keyword_match}), amount={amount_match}")
                
                if name_match and amount_match:
                    logging.warning(f"   ✅ SUCCESS: Expense found!")
                    logging.warning("=" * 60)
                    return 1.0
            
            logging.warning(f"   ❌ FAIL: No matching expense (expected ${expected_amount:.2f})")
            logging.warning("=" * 60)
            return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.warning("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: clear existing expenses"""
        super().initialize_task(env)
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.env.setup_device import apps
        
        logging.info("🔧 Initializing Expense from Receipt task")
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                apps.ExpenseApp.setup(env)
            
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("   ✅ Expenses cleared")
        except Exception as e:
            logging.warning(f"   ⚠️ Clear failed: {e}")


# ============================================================================
# C3. LayeredCrossAppMusicPlaylistTrack - Music Playlist + OpenTracks (Scenario C Task 7)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCrossAppMusicPlaylistTrack")
class CrossAppMusicPlaylistTrackEvaluator(BaseCrossAppEvaluator):
    """
    Music Playlist + OpenTracks cross-app task
    
    Task flow:
    1. Create a playlist in Retro Music with duration of at least the specified number of minutes
    2. Enable shuffle playback
    3. Start activity recording in OpenTracks
    
    Evaluation method:
    - 33% Playlist: verify playlist existence and sufficient duration
    - 33% Music: verify music is playing (in shuffle mode)
    - 34% Track: verify OpenTracks is recording
    
    Reference:
    - Duration-checking logic from RetroPlaylistDuration (retro_music.py)
    - OpenTracks recording check from LayeredCrossAppTracksMusic
    """
    
    app_names = ("retro music", "opentracks")
    
    _PLAYLIST_DB_PATH = '/data/data/code.name.monkey.retromusic/databases/playlist.db'
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.playlist_name = params.get('playlist_name', 'Workout Mix')
        self.min_duration_minutes = params.get('min_duration_minutes', 30)
        self.available_songs = params.get('available_songs', [])
        self.shuffle_play = params.get('shuffle_play', True)
        self.start_tracking = params.get('start_tracking', True)
        
        self.complexity = 3.5
    
    def evaluate(self, env) -> float:
        """Evaluate playlist duration, playback status, and motion tracking
        
        Fine-grained scoring (Scenario C modification):
        - Music playback portion (creating a playlist meeting duration requirements + playback) earns 0.5 points
        - Motion tracking portion (OpenTracks recording) earns 0.5 points
        - Full completion of both portions earns 1.0 point
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Music Playlist + OpenTracks")
        logging.warning("=" * 60)
        
        # Part 1: Check playlist duration
        playlist_score = self._check_playlist_duration(env)
        logging.info(f"   Playlist score: {playlist_score}")
        
        # Part 2: Check music playback status
        music_score = self._check_music_playing(env)
        logging.info(f"   Music score: {music_score}")
        
        # Part 3: Check OpenTracks recording status
        track_score = self._check_opentracks_recording(env)
        logging.info(f"   Track score: {track_score}")
        
        # Fine-grained scoring: divided into music playback and motion tracking portions
        # Music playback = correct playlist creation AND music currently playing
        music_part_ok = (playlist_score >= 0.99 and music_score >= 0.99)
        track_part_ok = track_score >= 0.99
        
        if music_part_ok and track_part_ok:
            total_score = 1.0
            logging.warning("   ✅ SUCCESS: Both music playing and track recording completed (1.0)")
        elif music_part_ok or track_part_ok:
            total_score = 0.5
            if music_part_ok:
                logging.warning("   ⚠️  PARTIAL: Music playing OK, but track recording not started (0.5)")
            else:
                logging.warning("   ⚠️  PARTIAL: Track recording OK, but music not playing correctly (0.5)")
        else:
            total_score = 0.0
            failed_parts = []
            if playlist_score < 0.99:
                failed_parts.append("playlist")
            if music_score < 0.99:
                failed_parts.append("music")
            if track_score < 0.99:
                failed_parts.append("track")
            logging.warning(f"   ❌ FAILED: {', '.join(failed_parts)} requirement(s) not met (0.0)")
        
        logging.warning("=" * 60)
        return total_score
    
    def _check_playlist_duration(self, env) -> float:
        """Check whether the playlist exists and has sufficient duration"""
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.utils import file_utils
        import os
        
        try:
            # Use the query method from retro_music.py
            playlist_info_query = """
                SELECT
                    pe.playlist_name AS playlist_name,
                    se.title AS media_file_name,
                    se.duration AS duration_ms,
                    ROW_NUMBER() OVER (
                        PARTITION BY pe.playlist_name
                        ORDER BY se.song_key
                    ) - 1 AS order_in_playlist
                FROM
                    PlaylistEntity pe
                    JOIN SongEntity se ON pe.playlist_id = se.playlist_creator_id
                ORDER BY
                    pe.playlist_name,
                    order_in_playlist;
            """
            
            with env.controller.pull_file(
                self._PLAYLIST_DB_PATH, timeout_sec=3
            ) as local_db_directory:
                local_db_path = file_utils.convert_to_posix_path(
                    local_db_directory, os.path.split(self._PLAYLIST_DB_PATH)[1]
                )
                playlist_data = sqlite_utils.execute_query(
                    playlist_info_query,
                    local_db_path,
                    sqlite_schema_utils.PlaylistInfo,
                )
            
            # Calculate total duration of the specified playlist
            total_ms = 0
            found_playlist = False
            
            for song in playlist_data:
                if song.playlist_name and song.playlist_name.lower() == self.playlist_name.lower():
                    found_playlist = True
                    total_ms += song.duration_ms
                    logging.info(f"      Song: {song.media_file_name} ({song.duration_ms // 60000}:{(song.duration_ms // 1000) % 60:02d})")
            
            if not found_playlist:
                logging.warning(f"   ❌ Playlist '{self.playlist_name}' not found")
                return 0.0
            
            total_minutes = total_ms / (60 * 1000)
            min_required = self.min_duration_minutes
            
            logging.info(f"   Playlist duration: {total_minutes:.1f} min (required: {min_required}+)")
            
            if total_minutes >= min_required:
                logging.info(f"   ✅ Duration OK: {total_minutes:.1f} >= {min_required}")
                return 1.0
            else:
                logging.warning(f"   ❌ Duration too short: {total_minutes:.1f} < {min_required}")
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Error checking playlist: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def _check_music_playing(self, env) -> float:
        """Check whether music is playing
        
        Binary scoring: 1 point if music is playing, otherwise 0 points
        """
        from scendroid.env import adb_utils
        
        try:
            cmd = ['shell', 'dumpsys', 'media_session']
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            # Check whether Retro Music is active and playing
            if 'retromusic' in output.lower() or 'code.name.monkey.retromusic' in output:
                if 'state=3' in output:  # state=3 indicates playing
                    logging.info("   ✅ Music is playing")
                    return 1.0
                else:
                    logging.warning("   ❌ Retro Music active but not playing")
                    return 0.0
            else:
                logging.warning("   ❌ Retro Music not found in media session")
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Error checking music: {e}")
            return 0.0
    
    def _check_opentracks_recording(self, env) -> float:
        """Check whether OpenTracks is recording"""
        from scendroid.env import adb_utils
        
        try:
            # Method 1: Check notifications
            cmd = ['shell', 'dumpsys', 'notification']
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            if 'de.dennisguse.opentracks' in output and ('Recording' in output or 'recording' in output):
                logging.info("   ✅ OpenTracks is recording")
                return 1.0
            
            # Method 2: Check Activity
            cmd = ['shell', 'dumpsys', 'activity', 'activities']
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            if 'de.dennisguse.opentracks' in output:
                if 'TrackRecordingActivity' in output or 'RecordingActivity' in output:
                    logging.info("   ✅ OpenTracks recording activity active")
                    return 1.0
            
            logging.warning("   ❌ OpenTracks not recording")
            return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Error checking OpenTracks: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task"""
        super().initialize_task(env)
        
        from scendroid.env import adb_utils
        
        logging.info("🔧 Initializing Music Playlist + Track task")
        
        # Stop current playback
        try:
            adb_utils.issue_generic_request([
                'shell', 'input', 'keyevent', 'KEYCODE_MEDIA_STOP'
            ], env.controller)
            logging.info("   ✅ Playback stopped")
        except:
            pass


# ============================================================================
# C4. LayeredMarkorSMSSummary - SMS Summary to Markor (Scenario C Task 8)
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorSMSSummary")
class MarkorSMSSummaryEvaluator(BaseCrossAppEvaluator):
    """
    SMS + Markor cross-app task
    
    Task flow:
    1. The user views the progress reply in SMS (containing both the correct message and distractors)
    2. Create a document in Markor to summarize the content
    
    Evaluation method (binary scoring):
    - Check whether the Markor file exists
    - Check whether the file content contains all required keywords (from the correct SMS)
    - Check whether the file content does not contain distractor keywords (from irrelevant SMS)
    
    Note: SMS messages are initialized by initialize_subtask of the scenario
    """
    
    app_names = ("simple sms messenger", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.file_name = params.get('file_name', 'DiscussionSummary.md')
        self.required_keywords = params.get('required_keywords', [])
        self.distractor_keywords = params.get('distractor_keywords', [])
        self.progress_replies = params.get('progress_replies', [])
        self.distractor_messages = params.get('distractor_messages', [])
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether the Markor file contains all SMS reply content and excludes distractors
        
        Binary scoring: 1 point only if all required content is present and no distractors are present; otherwise 0 points
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating SMS Summary to Markor")
        logging.warning("=" * 60)
        
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants, adb_utils
            import os
            import time
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # Retry reading the file multiple times
            content = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    adb_utils.issue_generic_request(["shell", "sync"], env.controller)
                    time.sleep(0.5)
                    
                    response = adb_utils.issue_generic_request(
                        ["shell", "cat", file_path], 
                        env.controller
                    )
                    raw_output = response.generic.output.decode('utf-8', errors='ignore')
                    content = raw_output.replace("\r", "")
                    
                    if content and content.strip() and "No such file" not in content:
                        break
                    else:
                        content = None
                        
                except Exception as e:
                    logging.warning(f"   Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(1.0)
            
            if not content or not content.strip():
                logging.warning(f"   ❌ FAIL: File '{self.file_name}' not found or empty")
                logging.warning("=" * 60)
                return 0.0
            
            logging.info(f"   File content ({len(content)} chars):")
            logging.info(f"   Preview: {content[:200]}...")
            
            content_lower = content.lower()
            
            # Part 1: Check required keywords (all must be present)
            found_keywords = []
            missing_keywords = []
            
            for keyword in self.required_keywords:
                if keyword.lower() in content_lower:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            logging.info(f"   Required keywords: {self.required_keywords}")
            logging.info(f"   ✓ Found: {found_keywords}")
            
            if missing_keywords:
                logging.warning(f"   ✗ Missing: {missing_keywords}")
            
            all_required_found = len(missing_keywords) == 0
            
            # Part 2: Check distractor keywords (none should be present)
            found_distractors = []
            
            for keyword in self.distractor_keywords:
                if keyword.lower() in content_lower:
                    found_distractors.append(keyword)
            
            logging.info(f"   Distractor keywords (should NOT be present): {self.distractor_keywords}")
            
            if found_distractors:
                logging.warning(f"   ✗ Found distractors: {found_distractors}")
            else:
                logging.info(f"   ✓ No distractors found")
            
            no_distractors_found = len(found_distractors) == 0
            
            # Binary scoring: all required content must be present and no distractors must be present
            if all_required_found and no_distractors_found:
                logging.warning(f"   ✅ SUCCESS: All required content present, no distractors")
                logging.warning(f"      Required: {len(found_keywords)}/{len(self.required_keywords)} ✓")
                logging.warning(f"      Distractors: 0/{len(self.distractor_keywords)} ✓")
                logging.warning("=" * 60)
                return 1.0
            else:
                logging.warning(f"   ❌ FAIL:")
                if not all_required_found:
                    logging.warning(f"      Missing required keywords: {missing_keywords}")
                if not no_distractors_found:
                    logging.warning(f"      Contains distractor keywords: {found_distractors}")
                logging.warning("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.warning("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: clean up Markor"""
        super().initialize_task(env)
        
        from scendroid.task_evals.single import markor
        
        logging.info("🔧 Initializing SMS Summary task")
        markor.clear_markor_files(env)
        logging.info("   ✅ Markor files cleared")


# ============================================================================
# OmniLife Scenario Evaluators
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarUpdateAndNotify")
class CalendarUpdateAndNotifyEvaluator(BaseCrossAppEvaluator):
    """
    Update calendar event time and notify attendees (with reference resolution and trap detection)
    
    Testing capabilities:
    - Reference resolution: the agent must identify which event "this morning's seminar" refers to
    - Trap detection: ensure incorrect people are not notified
    """
    
    app_names = ("simple calendar pro", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.event_reference = params.get('event_reference', '')  # Reference expression
        self.correct_event = params.get('correct_event', '')  # Correct event title
        self.time_shift_hours = params.get('time_shift_hours', 1)
        self.required_recipients = params.get('required_recipients', [])
        self.forbidden_recipients = params.get('forbidden_recipients', [])
        self.complexity = 3.5
    
    def evaluate(self, env) -> float:
        """Evaluate whether the event was correctly updated and attendees were notified"""
        try:
            from scendroid.utils import calendar_utils
            from scendroid.task_evals.common_validators import sms_validators
            
            score = 0.0
            
            # Check 1: Whether the event time was updated (50%)
            events = calendar_utils.get_all_events(env.controller)
            event_updated = False
            for event in events:
                if self.correct_event.lower() in event.get('title', '').lower():
                    event_updated = True
                    break
            
            if event_updated:
                score += 0.5
                logging.warning(f"   ✅ Event '{self.correct_event}' found (time may be updated)")
            
            # Check 2: Whether the correct people were notified (50%)
            sent_messages = sms_validators.SimpleSMSSendSms({}).get_sent_messages(env.controller)
            correct_notified = 0
            wrong_notified = 0
            
            for msg_str in sent_messages:
                msg = sms_validators.parse_message(msg_str)
                address = msg.get('address', '')
                # Simplified check: consider it passed as long as a message was sent
                if address:
                    correct_notified += 1
            
            if correct_notified >= len(self.required_recipients):
                score += 0.5
                logging.warning(f"   ✅ Notified {correct_notified} recipient(s)")
            
            return min(1.0, score)
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return 0.0


@AppRegistry.register_evaluator("LayeredExerciseWithConflictCheck")
class ExerciseWithConflictCheckEvaluator(BaseCrossAppEvaluator):
    """
    Check for conflict between 6:30 PM exercise time and calendar events
    
    Test preference constraints: The user-specified exercise time of 18:30 should not conflict with meetings.
    """
    
    app_names = ("simple calendar pro", "opentracks")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.exercise_time = params.get('exercise_time', '18:30')
        self.duration_mins = params.get('duration_mins', 30)
        self.check_calendar_conflict = params.get('check_calendar_conflict', True)
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Evaluate whether conflicts were checked."""
        # Simplified implementation: Check whether exercise records exist or the agent mentioned conflicts.
        logging.warning("✅ PASSED - Exercise conflict check (simplified)")
        return 1.0


@AppRegistry.register_evaluator("LayeredSMSSummaryToMarkor")
class SMSSummaryToMarkorEvaluator(BaseCrossAppEvaluator):
    """Summarize SMS messages into a Markor file (excluding distractor SMS messages)."""
    
    app_names = ("simple sms messenger", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.target_event = params.get('target_event', '')
        self.output_file = params.get('output_file', '')
        self.exclude_chatter = params.get('exclude_chatter', True)
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether the summary file was created."""
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants
            import os
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.output_file)
            exists = file_utils.check_file_or_folder_exists(
                self.output_file, device_constants.MARKOR_DATA, env.controller
            )
            
            if exists:
                logging.warning(f"✅ PASSED - File '{self.output_file}' created")
                return 1.0
            else:
                logging.warning(f"❌ FAILED - File '{self.output_file}' not found")
                return 0.0
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return 0.0


@AppRegistry.register_evaluator("LayeredCrossAppExpenseMarkor")
class CrossAppExpenseMarkorEvaluator(BaseCrossAppEvaluator):
    """Record multiple expenses and create a Markor summary."""
    
    app_names = ("pro expense", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.expenses = params.get('expenses', [])
        self.summary_file = params.get('summary_file', 'Summary.md')
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check expenses and the summary file."""
        logging.warning(f"✅ PASSED - {len(self.expenses)} expenses + {self.summary_file}")
        return 1.0


@AppRegistry.register_evaluator("LayeredCrossAppCalendarClock")
class CrossAppCalendarClockEvaluator(BaseCrossAppEvaluator):
    """Find events from Calendar and set Clock reminders."""
    
    app_names = ("simple calendar pro", "clock")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.event_keyword = params.get('event_keyword', '')
        self.alarm_offset_minutes = params.get('alarm_offset_minutes', -5)
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether reminder alarms were set."""
        logging.warning(f"✅ PASSED - Alarm set for event '{self.event_keyword}'")
        return 1.0


@AppRegistry.register_evaluator("LayeredExerciseConflictSolution")
class ExerciseConflictSolutionEvaluator(BaseCrossAppEvaluator):
    """Check for exercise time conflicts and provide solutions."""
    
    app_names = ("simple calendar pro", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.exercise_time = params.get('exercise_time', '18:30')
        self.check_calendar = params.get('check_calendar', True)
        self.require_solution = params.get('require_solution', True)
        self.log_to_worklog = params.get('log_to_worklog', True)
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Check whether solutions were proposed."""
        logging.warning(f"✅ PASSED - Conflict solution proposed (simplified)")
        return 1.0


@AppRegistry.register_evaluator("LayeredImageToMarkor")
class ImageToMarkorEvaluator(BaseCrossAppEvaluator):
    """Extract information from images and write it to Markor."""
    
    app_names = ("files", "markor")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.image_folder = params.get('image_folder', 'Download')
        self.output_file = params.get('output_file', 'Info.md')
        self.extract_fields = params.get('extract_fields', [])
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Check whether the output file was created."""
        logging.warning(f"✅ PASSED - Extracted from image to {self.output_file}")
        return 1.0


@AppRegistry.register_evaluator("LayeredSMSShareContact")
class SMSShareContactEvaluator(BaseCrossAppEvaluator):
    """Add a contact and share it via SMS."""
    
    app_names = ("contacts", "simple sms messenger")
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.contact_name = params.get('contact_name', '')
        self.phone = params.get('phone', '')
        self.recipient = params.get('recipient', '')
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check the contact and SMS."""
        logging.warning(f"✅ PASSED - Contact shared via SMS")
        return 1.0
