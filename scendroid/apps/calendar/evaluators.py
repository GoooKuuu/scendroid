"""
Calendar App Evaluators

Provides evaluators related to the Simple Calendar Pro app (8 evaluators): 

1. LayeredCalendarCreateMeeting - Create a calendar meeting/event
2. LayeredCalendarCreateRecurringEvent - Create a recurring event
3. LayeredCalendarDeleteEventsOnDate - Delete all events on a specific date
4. LayeredCalendarGetNextEvent - Get the next event (information retrieval)
5. LayeredCalendarDeleteEventByTime - Delete a specific event by time
6. LayeredCalendarEditNote - Edit an event note
7. LayeredCalendarCheckMeetingAnswer - Check the meeting response (information retrieval)
8. LayeredCalendarExtractAttendees - Extract the attendees list (information retrieval)

Note: All scendroid.env imports are performed inside functions to avoid circular dependencies during module loading.
"""

import datetime
import time
from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# 1. LayeredCalendarCreateMeeting - Create a calendar meeting/event
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCreateMeeting")
class CalendarCreateMeetingEvaluator(BaseAppEvaluator):
    """
    Evaluation calendar meeting/event creation task
    
    supported scenarios:
    - L0: "Open the Calendar app and create a meeting for 10:00 AM tomorrow, 
           location 'Building B, 3rd Floor', duration 60 minutes."
    - L1: "Add a meeting at 10:00 AM tomorrow to my calendar 
           (Building B, 3rd Floor, 1 hour)."
    - L2: "Add my 10:00 AM meeting tomorrow to the calendar."
    - L3: "Schedule my meeting tomorrow morning in my calendar."
    
    evaluation content:
    - Whether the event title is correct
    - Whether the time is correct (allowing a 1-hour tolerance)
    - Whether the location matches (fuzzy match)
    - Whether the duration is correct (allowing a 15-minute tolerance)
    """
    
    # ScenDroid standard attributes
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.title = params.get('title')
        self.hour = params.get('hour')
        self.day_offset = params.get('day_offset')
        self.location = params.get('location', '')
        self.duration_mins = params.get('duration_mins')
        
        # set complexity
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the calendar event was created successfully
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.env import device_constants
            from scendroid.task_evals.single.calendar import calendar_utils
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            from scendroid.utils import datetime_utils
            from .utils import get_device_time_ms
            
            # Compute the target date (using timezone-aware datetime)
            device_time_ms = get_device_time_ms(env)
            device_time_sec = device_time_ms // 1000
            device_dt = datetime_utils.timestamp_to_localized_datetime(
                device_time_sec, timezone=device_constants.TIMEZONE
            )
            target_dt = device_dt + datetime.timedelta(days=self.day_offset)
            target_dt = target_dt.replace(
                hour=self.hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            # Read the calendar event
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            logging.warning("📊 Calendar Evaluation:")
            logging.warning("   Looking for: '%s' at %s", self.title, target_dt.strftime("%Y-%m-%d %H:%M"))
            logging.warning("   Location: '%s' | Duration: %d mins", self.location, self.duration_mins)
            logging.warning("   Found %d event(s) in calendar", len(events))
            
            # Check whether a matching event exists
            for event in events:
                # Safely handle fields that might be None
                event_duration = event.duration_mins if event.duration_mins is not None else 0
                
                # check title
                title_match = event.title.lower() == self.title.lower()
                
                # Check the time (allowing a 1-hour tolerance)
                time_diff = abs((event.start_datetime - target_dt).total_seconds())
                time_match = time_diff < 3600
                
                # Check the location (fuzzy match)
                location_match = True
                if self.location:
                    event_location = event.location or ""
                    location_match = self.location.lower() in event_location.lower()
                
                # Check the duration (allowing a 15-minute tolerance)
                duration_match = abs(event_duration - self.duration_mins) <= 15
                
                logging.debug("   checkevent: '%s'", event.title)
                logging.debug("     - Title match: %s (expected: '%s', actual: '%s')", 
                             title_match, self.title, event.title)
                logging.debug("     - Time match: %s (difference: %.1f seconds)", time_match, time_diff)
                logging.debug("     - Location match: %s", location_match)
                logging.debug("     - durationmatch: %s", duration_match)
                
                if title_match and time_match and location_match and duration_match:
                    logging.warning("✅ PASSED - Found matching event:")
                    logging.warning("   Title: %s", event.title)
                    logging.warning("   Time: %s", event.start_datetime)
                    logging.warning("   Location: %s", event.location)
                    logging.warning("   Duration: %d mins", event_duration)
                    return 1.0
            
            logging.warning("❌ FAILED - No matching calendar event found")
            return 0.0
        
        except Exception as e:
            logging.error("❌ error occurred during evaluation: %s", e)
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        initialize task: clearcalendardatabase
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().initialize_task(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("Calendar database cleared")
    
    def tear_down(self, env):
        """
        clean environment: clear calendar database
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().tear_down(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared (tear down)")


# ============================================================================
# 2. LayeredCalendarCreateRecurringEvent - Create a recurring event
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCreateRecurringEvent")
class CalendarCreateRecurringEventEvaluator(BaseAppEvaluator):
    """
    Evaluation of recurring calendar event creation task
    
    supported scenarios:
    - L0: "Open Simple Calendar Pro and create a recurring event titled 'Gym' 
           starting next Monday at 6:30 PM, repeating weekly, lasting 90 minutes, 
           description 'Leg day'."
    - L1: "Set up a weekly 'Gym' event starting next Monday at 6:30 PM for 90 minutes."
    - L2: "Add a repeating gym plan to my calendar."
    
    evaluation content:
    - Event title, time, and duration
    - Recurrence rule (daily/weekly)
    - Description (if provided)
    """
    
    # ScenDroid standard attributes
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.title = params.get('title')
        self.hour = params.get('hour')
        self.minute = params.get('minute')
        self.day_of_week = params.get('day_of_week')  # 1=Monday, 7=Sunday
        self.duration_mins = params.get('duration_mins')
        self.description = params.get('description', '')
        self.repeat_type = params.get('repeat_type')  # 'daily' or 'weekly'
        
        # set complexity
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the recurring event was created successfully
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        # import on demand
        from scendroid.env import device_constants
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.utils import datetime_utils
        from .utils import get_device_time_ms
        
        # Compute the target start time (next occurrence of the specified weekday)
        device_time_ms = get_device_time_ms(env)
        device_time_sec = device_time_ms // 1000
        device_dt = datetime_utils.timestamp_to_localized_datetime(
            device_time_sec, timezone=device_constants.TIMEZONE
        )
        
        # Compute the number of days until the target weekday
        current_day = device_dt.isoweekday()  # 1=Monday, 7=Sunday
        days_ahead = (self.day_of_week - current_day) % 7
        if days_ahead == 0:
            days_ahead = 7  # If today is the target weekday, select next week
        
        target_dt = device_dt + datetime.timedelta(days=days_ahead)
        target_dt = target_dt.replace(
            hour=self.hour,
            minute=self.minute,
            second=0,
            microsecond=0
        )
        
        # Read the calendar event
        events = sqlite_utils.get_rows_from_remote_device(
            calendar_utils.EVENTS_TABLE,
            calendar_utils.DB_PATH,
            sqlite_schema_utils.CalendarEvent,
            env,
        )
        
        logging.warning("📊 Recurring Event Evaluation:")
        logging.warning("   Looking for: '%s' at %s", self.title, target_dt.strftime("%Y-%m-%d %H:%M"))
        logging.warning("   Repeat: %s | Duration: %d mins", self.repeat_type, self.duration_mins)
        logging.warning("   Found %d event(s) in calendar", len(events))
        
        # Check whether a matching recurring event exists
        for event in events:
            # check title
            title_match = event.title.lower() == self.title.lower()
            
            # Check the time (allowing a 15-minute tolerance)
            time_diff = abs((event.start_datetime - target_dt).total_seconds())
            time_match = time_diff < 900  # 15 minutes
            
            # Check the duration
            duration_match = abs(event.duration_mins - self.duration_mins) <= 15
            
            # Check duplicate rule
            repeat_match = False
            if hasattr(event, 'rrule') and event.rrule:
                rrule_str = event.rrule.lower()
                if self.repeat_type == 'daily':
                    repeat_match = 'freq=daily' in rrule_str or 'daily' in rrule_str
                elif self.repeat_type == 'weekly':
                    repeat_match = 'freq=weekly' in rrule_str or 'weekly' in rrule_str
            
            # Check description (optional)
            description_match = True
            if self.description:
                event_desc = getattr(event, 'description', '') or ''
                description_match = self.description.lower() in event_desc.lower()
            
            if title_match and time_match and duration_match and repeat_match and description_match:
                logging.warning("✅ PASSED - Found matching recurring event:")
                logging.warning("   Title: %s", event.title)
                logging.warning("   Time: %s", event.start_datetime)
                logging.warning("   Duration: %d mins", event.duration_mins)
                logging.warning("   Repeat: %s", getattr(event, 'rrule', 'N/A'))
                return 1.0
        
        logging.warning("❌ FAILED - No matching recurring event found")
        return 0.0
    
    def initialize_task(self, env):
        """
        initialize task: clearcalendardatabase
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().initialize_task(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared")
    
    def tear_down(self, env):
        """
        clean environment: clear calendar database
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().tear_down(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared (tear down)")


# ============================================================================
# 3. LayeredCalendarDeleteEventsOnDate - Delete all events on a specific date
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarDeleteEventsOnDate")
class CalendarDeleteEventsOnDateEvaluator(BaseAppEvaluator):
    """
    Evaluation task for deleting all events on a specific date
    
    supported scenarios:
    - L0: "Open Simple Calendar Pro and delete all events on 2023-10-16"
    - L1: "Clear my calendar for 2023-10-16"
    - L2: "Remove everything scheduled on 2023-10-16"
    
    initialization:
    - Create multiple events on the target date (default: 3)
    
    evaluation content:
    - Check whether all events on the target date have been deleted
    """
    
    # ScenDroid standard attributes
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.year = params.get('year')
        self.month = params.get('month')
        self.day = params.get('day')
        self.num_events = params.get('num_events', 3)
        
        # Store the event IDs created during initialization
        self.events_before = []
        self.target_event_ids = []
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether all events on the target date have been deleted
        
        Returns:
            float: 1.0 indicates all events were deleted; 0.0 indicates some events remain
        """
        # import on demand
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        # Get events after deletion
        events_after = sqlite_utils.get_rows_from_remote_device(
            calendar_utils.EVENTS_TABLE,
            calendar_utils.DB_PATH,
            sqlite_schema_utils.CalendarEvent,
            env,
        )
        
        logging.warning("📊 Delete Events Evaluation:")
        logging.warning("   Target date: %04d-%02d-%02d", self.year, self.month, self.day)
        logging.warning("   Events before: %d", len(self.events_before))
        logging.warning("   Events after: %d", len(events_after))
        logging.warning("   Expected to delete: %d events (IDs: %s)",
                       len(self.target_event_ids), self.target_event_ids)
        
        # Check whether the target event has been deleted
        remaining_target_ids = []
        for event in events_after:
            if event.id in self.target_event_ids:
                remaining_target_ids.append(event.id)
                logging.warning("   ⚠️  Event still exists: ID=%d, title='%s', time=%s",
                               event.id, event.title, event.start_datetime)
        
        if remaining_target_ids:
            logging.warning("❌ FAILED - %d target event(s) still remain: %s",
                           len(remaining_target_ids), remaining_target_ids)
            return 0.0
        else:
            logging.warning("✅ PASSED - All %d events on %04d-%02d-%02d were deleted",
                           len(self.target_event_ids), self.year, self.month, self.day)
            return 1.0
    
    def initialize_task(self, env):
        """
        Initialize task: Clear the calendar and create multiple events on the target date
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        super().initialize_task(env)
        
        # clearcalendar
        calendar_utils.clear_calendar_db(env)
        
        # Create multiple events on the target date
        target_date = datetime.datetime(self.year, self.month, self.day, 
                                       tzinfo=datetime.timezone.utc)
        events_to_add = []
        
        logging.info("Creating %d events on %04d-%02d-%02d...", 
                    self.num_events, self.year, self.month, self.day)
        
        for i in range(self.num_events):
            # Create events at different times within one day
            hour = 9 + (i * 3)  # 9:00, 12:00, 15:00, 18:00, 21:00
            event_time = target_date.replace(hour=hour % 24)
            start_ts = int(event_time.timestamp())
            end_ts = start_ts + 3600  # 1 hour duration
            
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts,
                end_ts=end_ts,
                title=f"Event {i+1}",
                description=f"Test event {i+1} on {self.year}-{self.month:02d}-{self.day:02d}",
                location=f"Location {i+1}",
            )
            events_to_add.append(event)
            logging.info("  - Event %d: %s at %02d:00", i+1, event.title, hour)
        
        # Add event to database
        calendar_utils.add_events(events_to_add, env)
        time.sleep(2.0)  # e.g., wait for database update
        
        # Get current state (with database-assigned IDs)
        self.events_before = sqlite_utils.get_rows_from_remote_device(
            calendar_utils.EVENTS_TABLE,
            calendar_utils.DB_PATH,
            sqlite_schema_utils.CalendarEvent,
            env,
        )
        
        # Store the IDs of events on the target date
        self.target_event_ids = []
        for event in self.events_before:
            event_date = event.start_datetime.date()
            target_date_obj = target_date.date()
            if event_date == target_date_obj:
                self.target_event_ids.append(event.id)
        
        logging.warning("✅ Initialized %d events on %04d-%02d-%02d (IDs: %s)",
                       len(self.target_event_ids), self.year, self.month, self.day, 
                       self.target_event_ids)
    
    def tear_down(self, env):
        """
        clean environment: clear calendar database
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().tear_down(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared (tear down)")


# ============================================================================
# 4. LayeredCalendarGetNextEvent - Get the next upcoming event (information retrieval)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarGetNextEvent")
class CalendarGetNextEventEvaluator(BaseAppEvaluator):
    """
    Evaluation task for retrieving the title of the next event (information retrieval)
    
    supported scenarios:
    - L0: "Open Simple Calendar Pro and tell me the title of my next upcoming event"
    - L2: "Check what I have coming up next"
    
    initialization:
    - Create multiple events (some before and some after the current time)
    
    evaluation content:
    - Check whether the agent's answer contains the correct title of the next event
    """
    
    # ScenDroid standard attributes
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # parameter
        self.next_event_title = params.get('next_event_title')
        self.next_event_time_hour = params.get('next_event_time_hour')
        self.next_event_time_minute = params.get('next_event_time_minute', 0)
        
        # Store the expected answer
        self.expected_title = None
        self.all_events = []
        
        # set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the agent's answer contains the correct event title
        
        Returns:
            float: 1.0 indicates the answer is correct; 0.0 indicates an error
        """
        from .utils import get_agent_answer
        
        # get agent's answer
        agent_answer = get_agent_answer(env)
        
        if not agent_answer:
            logging.warning("❌ FAILED - No answer from agent")
            logging.warning("   Make sure the agent provided an answer using the answer action")
            return 0.0
        
        logging.warning("📊 Next Event Evaluation:")
        logging.warning("   Expected title: '%s'", self.expected_title)
        logging.warning("   Agent's answer: '%s'", agent_answer)
        
        # Check whether the answer contains the expected event title (case-insensitive, fuzzy match)
        answer_lower = agent_answer.lower()
        expected_lower = (self.expected_title or '').lower()
        
        if expected_lower in answer_lower:
            logging.warning("✅ PASSED - Answer contains the correct event title")
            return 1.0
        else:
            logging.warning("❌ FAILED - Answer does not contain the event title")
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Clear the calendar and create multiple events
        """
        from scendroid.env import device_constants
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.utils import datetime_utils
        from .utils import get_device_time_ms
        
        super().initialize_task(env)
        
        # clearcalendar
        calendar_utils.clear_calendar_db(env)
        
        # Device time is Oct 15, 2023 around 15:30 (3:30 PM)
        # We create events at: 10:00, 14:00, 16:00, 18:00, 20:00
        # The next event after 15:30 should be at 16:00
        
        device_time_ms = get_device_time_ms(env)
        device_time_sec = device_time_ms // 1000
        device_dt = datetime_utils.timestamp_to_localized_datetime(
            device_time_sec, timezone=device_constants.TIMEZONE
        )
        
        logging.warning("📅 Calendar Info Retrieval Task Initialization:")
        logging.warning("   Device time: %s", device_dt.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Create events for the current day
        year = 2023
        month = 10
        day = 15
        
        event_configs = [
            (10, 0, "Morning Meeting", "Discuss quarterly goals"),
            (14, 0, "Lunch with Team", "Team building lunch"),
            (16, 0, "Project Review", "Review Q3 progress"),  # This should be the next event
            (18, 0, "Dentist Appointment", "Regular checkup"),
            (20, 0, "Dinner with Friends", "Celebrate birthday"),
        ]
        
        events_to_add = []
        for hour, minute, title, description in event_configs:
            event_time = datetime.datetime(
                year, month, day, hour, minute, 
                tzinfo=datetime.timezone.utc
            )
            start_ts = int(event_time.timestamp())
            end_ts = start_ts + 3600  # 1 hour duration
            
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts,
                end_ts=end_ts,
                title=title,
                description=description,
                location="",
            )
            events_to_add.append(event)
            self.all_events.append({
                "time": event_time,
                "title": title,
                "description": description,
            })
            logging.info("  Created event: '%s' at %02d:%02d", title, hour, minute)
        
        # Add event to database
        calendar_utils.add_events(events_to_add, env)
        time.sleep(2.0)
        
        # Identify the next event after the device time
        for event in self.all_events:
            if event["time"] > device_dt:
                self.expected_title = event["title"]
                logging.warning("✅ Next upcoming event: '%s' at %s",
                               self.expected_title,
                               event["time"].strftime("%H:%M"))
                break
        
        if not self.expected_title:
            logging.error("❌ No upcoming events found after device time!")
    
    def tear_down(self, env):
        """
        clean environment: clear calendar database
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().tear_down(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared (tear down)")


# ============================================================================
# 5. LayeredCalendarDeleteEventByTime - Delete a specific event by time
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarDeleteEventByTime")
class CalendarDeleteEventByTimeEvaluator(BaseAppEvaluator):
    """
    Evaluation task for deleting a specific event by time
    
    supported scenarios:
    - L0: "Open Simple Calendar Pro and delete the event scheduled for 3:00 PM today"
    - L1: "Cancel my 3:00 PM appointment"
    - L2: "Remove my afternoon meeting"
    
    initialization:
    - Create the target event and multiple noise events
    
    evaluation content:
    - Check whether the event at the target time has been deleted
    - Check whether other events remain intact
    """
    
    # ScenDroid standard attributes
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.target_hour = params.get('target_hour')
        self.target_minute = params.get('target_minute')
        self.target_title = params.get('target_title', 'Team Meeting')
        self.num_noise_events = params.get('num_noise_events', 3)
        
        # Store the event ID
        self.events_before = []
        self.target_event_id = None
        self.noise_event_ids = []
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether the target event has been deleted and whether other events are retained.
        
        Returns:
            float: 1.0 indicates the target event was deleted and other events were retained; 0.0 indicates failure.
        """
        # import on demand
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        # Get events after deletion.
        events_after = sqlite_utils.get_rows_from_remote_device(
            calendar_utils.EVENTS_TABLE,
            calendar_utils.DB_PATH,
            sqlite_schema_utils.CalendarEvent,
            env,
        )
        
        logging.warning("📊 Delete Event Evaluation:")
        logging.warning("   Target time: %02d:%02d", self.target_hour, self.target_minute)
        logging.warning("   Target event ID: %s", self.target_event_id)
        logging.warning("   Events before: %d", len(self.events_before))
        logging.warning("   Events after: %d", len(events_after))
        
        # Check whether the target event has been deleted.
        target_still_exists = False
        for event in events_after:
            if event.id == self.target_event_id:
                target_still_exists = True
                logging.warning("   ❌ Target event still exists: ID=%d", event.id)
                break
        
        if target_still_exists:
            logging.warning("❌ FAILED - Target event was not deleted")
            return 0.0
        
        # Check whether noise events are retained.
        noise_remaining = []
        for event in events_after:
            if event.id in self.noise_event_ids:
                noise_remaining.append(event.id)
        
        if len(noise_remaining) != len(self.noise_event_ids):
            logging.warning("⚠️  WARNING - Some noise events were also deleted")
            logging.warning("   Expected %d noise events, found %d",
                           len(self.noise_event_ids), len(noise_remaining))
            # 🆕 Binary rating: deleting an event that should not be deleted is considered a failure.
            logging.warning("❌ FAILED - Deleted some noise events")
            return 0.0
        
        logging.warning("✅ PASSED - Target event deleted, noise events preserved")
        return 1.0
    
    def initialize_task(self, env):
        """
        Initialize task: create the target event and noise events.
        """
        from scendroid.env import device_constants
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.utils import datetime_utils
        from .utils import get_device_time_ms
        
        super().initialize_task(env)
        
        # clearcalendar
        calendar_utils.clear_calendar_db(env)
        
        # Get device time.
        device_time_ms = get_device_time_ms(env)
        device_time_sec = device_time_ms // 1000
        device_dt = datetime_utils.timestamp_to_localized_datetime(
            device_time_sec, timezone=device_constants.TIMEZONE
        )
        
        year = device_dt.year
        month = device_dt.month
        day = device_dt.day
        
        logging.warning("📅 Delete Event By Time - Initialization:")
        logging.warning("   Device date: %04d-%02d-%02d", year, month, day)
        logging.warning("   Target time: %02d:%02d", self.target_hour, self.target_minute)
        logging.warning("   Target title: '%s'", self.target_title)
        
        # Create the target event.
        target_time = datetime.datetime(
            year, month, day, self.target_hour, self.target_minute,
            tzinfo=datetime.timezone.utc
        )
        target_start_ts = int(target_time.timestamp())
        target_end_ts = target_start_ts + 3600
        
        target_event = sqlite_schema_utils.CalendarEvent(
            start_ts=target_start_ts,
            end_ts=target_end_ts,
            title=self.target_title,
            description="Important team discussion",
            location="Conference Room A",
        )
        
        # Create noise events (which should not be deleted).
        noise_times = [
            (9, 0, "Morning Standup", "Daily sync"),
            (12, 0, "Lunch Break", "Team lunch"),
            (17, 30, "Code Review", "Review PRs"),
            (20, 0, "Evening Planning", "Plan tomorrow"),
        ]
        
        events_to_add = [target_event]
        
        for i, (hour, minute, title, desc) in enumerate(noise_times[:self.num_noise_events]):
            noise_time = datetime.datetime(
                year, month, day, hour, minute,
                tzinfo=datetime.timezone.utc
            )
            noise_start_ts = int(noise_time.timestamp())
            noise_end_ts = noise_start_ts + 3600
            
            noise_event = sqlite_schema_utils.CalendarEvent(
                start_ts=noise_start_ts,
                end_ts=noise_end_ts,
                title=title,
                description=desc,
                location=f"Location {i+1}",
            )
            events_to_add.append(noise_event)
            logging.info("  Noise event: %s at %02d:%02d", title, hour, minute)
        
        # Add all events to the database.
        calendar_utils.add_events(events_to_add, env)
        time.sleep(2.0)
        
        # Get the current state (with database-assigned IDs).
        self.events_before = sqlite_utils.get_rows_from_remote_device(
            calendar_utils.EVENTS_TABLE,
            calendar_utils.DB_PATH,
            sqlite_schema_utils.CalendarEvent,
            env,
        )
        
        # Identify the target event ID and noise event IDs.
        for event in self.events_before:
            event_hour = event.start_datetime.hour
            event_minute = event.start_datetime.minute
            
            if event_hour == self.target_hour and event_minute == self.target_minute:
                self.target_event_id = event.id
                logging.warning("✅ Target event created: ID=%d, '%s' at %02d:%02d",
                               event.id, event.title, event_hour, event_minute)
            else:
                self.noise_event_ids.append(event.id)
                logging.info("  Noise event: ID=%d, '%s' at %02d:%02d",
                            event.id, event.title, event_hour, event_minute)
        
        if not self.target_event_id:
            logging.error("❌ Failed to create target event!")
        
        logging.warning("📊 Initialized: 1 target + %d noise events", len(self.noise_event_ids))
    
    def tear_down(self, env):
        """
        clean environment: clear calendar database
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        
        super().tear_down(env)
        calendar_utils.clear_calendar_db(env)
        logging.info("✅ Calendar database cleared (tear down)")


# ============================================================================
# 6. LayeredCalendarEditNote - Edit event notes.
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarEditNote")
class CalendarEditNoteEvaluator(BaseAppEvaluator):
    """
    Evaluation task for editing event notes.
    
    supported scenarios:
    - "Find 'Company Weekly Meeting', and add a note 'John, out of office'"
    
    evaluation content:
    - Check whether the existing event was modified (rather than creating a new event).
    - Whether the event description contains required keywords.
    """
    
    # ScenDroid standard attributes
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.event_title = params.get('event_title')
        self.note_must_contain = params.get('note_must_contain', [])
        self.should_not_create_new_event = params.get('should_not_create_new_event', True)
        
        # Store the initial event.
        self._initial_events = []
        self._target_event = None
        
        # set complexity
        self.complexity = 2.5
    
    # Calendar-specific constants.
    _CALENDAR_DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
    _EVENTS_TABLE = "events"
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether the event note was correctly edited.
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        # import on demand
        from scendroid.task_evals.utils import (
            sqlite_utils,
            sqlite_schema_utils,
        )
        from .utils import check_keywords_in_text
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar Note Edit:")
        logging.info("=" * 60)
        
        try:
            # Get the current event.
            current_events = sqlite_utils.get_rows_from_remote_device(
                self._EVENTS_TABLE,
                self._CALENDAR_DB_PATH,
                sqlite_schema_utils.GenericRow,
                env
            )
            
            # Check whether a new event was created (only checked when baseline data exists).
            if self._initial_events:
                initial_ids = {getattr(e, 'id', None) for e in self._initial_events}
                new_events = [e for e in current_events 
                             if getattr(e, 'id', None) not in initial_ids]
                
                if new_events and self.should_not_create_new_event:
                    logging.info(f"   ❌ FAIL: {len(new_events)} new event(s) created")
                    return 0.0
            else:
                logging.info("   ℹ️  Skipping new event check (no baseline data)")
            
            # Locate the target event.
            event_title_lower = self.event_title.lower()
            target_event = None
            for event in current_events:
                event_title_db = getattr(event, 'title', '')
                if event_title_lower in event_title_db.lower():
                    if self._target_event and getattr(event, 'id', None) == getattr(self._target_event, 'id', None):
                        target_event = event
                        break
                    elif not self._target_event:
                        target_event = event
                        break
            
            if not target_event:
                logging.info(f"   ❌ FAIL: Target event not found")
                return 0.0
            
            # Check for keywords in the description.
            description = getattr(target_event, 'description', '').lower()
            logging.info(f"   Event description: {description[:100]}...")
            
            keywords_found, keywords_missing, score = check_keywords_in_text(
                description, self.note_must_contain, min_required=len(self.note_must_contain)
            )
            
            if keywords_missing:
                logging.info(f"   ❌ FAIL: Missing keywords: {keywords_missing}")
                return 0.0
            else:
                logging.info(f"   ✅ SUCCESS: All keywords found: {keywords_found}")
                return 1.0
        
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: store the initial event status.
        """
        from scendroid.task_evals.utils import (
            sqlite_utils,
            sqlite_schema_utils,
        )
        
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Edit Task:")
        logging.info("=" * 60)
        
        # Get the initial event.
        try:
            self._initial_events = sqlite_utils.get_rows_from_remote_device(
                self._EVENTS_TABLE,
                self._CALENDAR_DB_PATH,
                sqlite_schema_utils.GenericRow,
                env
            )
        except Exception as e:
            logging.warning(f"   ⚠️  Could not load initial events: {e}")
            self._initial_events = []
        
        # Locate the target event.
        event_title_lower = self.event_title.lower()
        self._target_event = None
        for event in self._initial_events:
            event_title_db = getattr(event, 'title', '')
            if event_title_lower in event_title_db.lower():
                self._target_event = event
                break
        
        if self._target_event:
            logging.info(f"   ✅ Found target event: {getattr(self._target_event, 'title', 'Unknown')}")
            logging.info(f"   Event ID: {getattr(self._target_event, 'id', 'Unknown')}")
        else:
            logging.warning(f"   ⚠️  Target event '{self.event_title}' not found")
        
        logging.info("📋 Task Info:")
        logging.info(f"   Event title: {self.event_title}")
        logging.info(f"   Must contain: {self.note_must_contain}")
        logging.info("=" * 60)


# ============================================================================
# 7. LayeredCalendarCheckMeetingAnswer - Check meeting answer (information retrieval).
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCheckMeetingAnswer")
class CalendarCheckMeetingAnswerEvaluator(BaseAppEvaluator):
    """
    Evaluation task for calendar meeting query answers (information retrieval).
    
    supported scenarios:
    - "Check my calendar and tell me what meetings I have this morning"
    
    evaluation content:
    - Check whether the agent's answer contains required keywords.
    - Case-insensitive matching.
    """
    
    # ScenDroid standard attributes
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.must_contain_keywords = params.get('must_contain_keywords', [])
        self.min_keywords_found = params.get('min_keywords_found', 2)
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether the agent's answer contains required keywords.
        
        Returns:
            float: 1.0 indicates sufficient keywords are present; 0.0 indicates insufficient keywords.
        """
        from .utils import get_agent_answer, check_keywords_in_text
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar QA Answer:")
        logging.info("=" * 60)
        
        try:
            # 🆕 First check the type and content of interaction_cache.
            logging.info(f"   🔍 Checking interaction_cache...")
            logging.info(f"   Type: {type(env.interaction_cache)}")
            logging.info(f"   Raw value: {repr(env.interaction_cache)[:200]}")
            
            # get agent's answer
            agent_answer = get_agent_answer(env)
            
            if not agent_answer:
                logging.error("   ❌ No answer found in env.interaction_cache")
                logging.error("   Make sure the agent provided an answer using the answer action")
                logging.error(f"   💡 Debug: interaction_cache = {repr(env.interaction_cache)}")
                return 0.0
            
            logging.info(f"   ✅ Agent's answer extracted: {agent_answer}")
            
            # Check for keywords.
            logging.info(f"   🔍 Required keywords: {self.must_contain_keywords}")
            logging.info(f"   🔍 Minimum required: {self.min_keywords_found}")
            
            keywords_found, keywords_missing, _ = check_keywords_in_text(
                agent_answer, self.must_contain_keywords, self.min_keywords_found
            )
            
            logging.warning(f"   📊 Keywords found: {len(keywords_found)}/{len(self.must_contain_keywords)}")
            logging.warning(f"   ✅ Found: {keywords_found}")
            if keywords_missing:
                logging.warning(f"   ❌ Missing: {keywords_missing}")
            
            # Calculate the score.
            if len(keywords_found) >= self.min_keywords_found:
                score = 1.0
                logging.warning(f"   ✅ SUCCESS: {len(keywords_found)} >= {self.min_keywords_found} keywords")
            else:
                score = 0.0
                logging.warning(f"   ❌ FAIL: Only {len(keywords_found)}/{self.min_keywords_found} keywords found")
                logging.warning(f"   💡 To pass, need to find at least {self.min_keywords_found} out of {self.must_contain_keywords}")
            
            logging.info("=" * 60)
            return score
        
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: no special initialization required (query task).
        """
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar QA Task:")
        logging.info(f"   Required keywords: {self.must_contain_keywords}")
        logging.info(f"   Min keywords: {self.min_keywords_found}")
        logging.info("=" * 60)


# ============================================================================
# 8. LayeredCalendarExtractAttendees - Extract attendee list (information retrieval).
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarExtractAttendees")
class CalendarExtractAttendeesEvaluator(BaseAppEvaluator):
    """
    Evaluation task for extracting the event attendee list (information retrieval).
    
    supported scenarios:
    - "Read the attendee list from the Company Weekly Meeting and list them for me"
    
    evaluation content:
    - Check whether the agent's answer contains required attendee names.
    - Allow excluding the user themselves
    """
    
    # ScenDroid standard attributes
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.event_title = params.get('event_title')
        self.required_attendees = params.get('required_attendees', [])
        self.min_attendees_found = params.get('min_attendees_found', 2)
        self.exclude_self = params.get('exclude_self', False)
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether the agent's answer includes the required participants
        
        Returns:
            float: 1.0 indicates sufficient participants are included, 0.0 indicates insufficient participants
        """
        from .utils import get_agent_answer, check_keywords_in_text
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar Attendees Extraction:")
        logging.info("=" * 60)
        
        try:
            # 🆕 First, check the type and content of interaction_cache
            logging.info(f"   🔍 Checking interaction_cache...")
            logging.info(f"   Type: {type(env.interaction_cache)}")
            logging.info(f"   Raw value: {repr(env.interaction_cache)[:200]}")
            
            # get agent's answer
            agent_answer = get_agent_answer(env)
            
            if not agent_answer:
                logging.error("   ❌ No answer found")
                logging.error(f"   💡 Debug: interaction_cache = {repr(env.interaction_cache)}")
                return 0.0
            
            logging.info(f"   ✅ Agent's answer extracted: {agent_answer}")
            logging.info(f"   📋 Event: {self.event_title}")
            logging.info(f"   👥 Required attendees: {self.required_attendees}")
            logging.info(f"   🔢 Minimum required: {self.min_attendees_found}")
            
            # Check participant names
            attendees_found, attendees_missing, _ = check_keywords_in_text(
                agent_answer, self.required_attendees, self.min_attendees_found
            )
            
            logging.warning(f"   📊 Attendees found: {len(attendees_found)}/{len(self.required_attendees)}")
            logging.warning(f"   ✅ Found: {attendees_found}")
            if attendees_missing:
                logging.warning(f"   ❌ Missing: {attendees_missing}")
            
            # Calculate score
            if len(attendees_found) >= self.min_attendees_found:
                score = 1.0
                logging.warning(f"   ✅ SUCCESS: {len(attendees_found)} >= {self.min_attendees_found} attendees")
            else:
                score = 0.0
                logging.warning(f"   ❌ FAIL: Only {len(attendees_found)}/{self.min_attendees_found} attendees found")
                logging.warning(f"   💡 To pass, need to find at least {self.min_attendees_found} out of {self.required_attendees}")
            
            logging.info("=" * 60)
            return score
        
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """
        initialize task: no special initialization required (query task)
        """
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Attendees Query:")
        logging.info("=" * 60)
        logging.info(f"   Event: {self.event_title}")
        logging.info(f"   Required attendees: {self.required_attendees}")
        logging.info("=" * 60)


# ============================================================================
# 9. LayeredCalendarCheckAvailability - check calendar availability (information retrieval task)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCheckAvailability")
class CalendarCheckAvailabilityEvaluator(BaseAppEvaluator):
    """
    evaluation calendar availability query task (information retrieval)
    
    supported scenarios:
    - W2-01: "Check my Simple Calendar Pro - am I free this afternoon between 1 PM and 6 PM?"
    
    evaluation content:
    - Check whether the agent correctly answered whether there is availability during the specified time period
    - Expected answers (e.g., "free"/"busy") can be set up
    """
    
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Time range
        self.start_time = params.get('start_time', '13:00')
        self.end_time = params.get('end_time', '18:00')
        
        # Expected answer (optional)
        # If None, only check whether the agent provided a reasonable answer
        self.expected_answer = params.get('expected_answer', None)  # 'free', 'busy', or None
        
        # Keyword matching
        self.free_keywords = ['free', 'available', 'open', 'nothing', 'no events', 'no meetings', 'clear']
        self.busy_keywords = ['busy', 'occupied', 'meeting', 'event', 'conflict', 'scheduled']
        
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether the agent correctly answered the availability question
        
        Returns:
            float: 1.0 indicates a correct answer, 0.0 indicates an error
        """
        from .utils import get_agent_answer
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar Availability Check:")
        logging.info("=" * 60)
        logging.info(f"   Time range: {self.start_time} - {self.end_time}")
        if self.expected_answer:
            logging.info(f"   Expected answer: {self.expected_answer}")
        
        try:
            # get agent's answer
            agent_answer = get_agent_answer(env)
            
            if not agent_answer:
                logging.error("   ❌ No answer found in env.interaction_cache")
                return 0.0
            
            logging.info(f"   Agent's answer: {agent_answer}")
            
            answer_lower = agent_answer.lower()
            
            # Detect answer type
            has_free_keyword = any(kw in answer_lower for kw in self.free_keywords)
            has_busy_keyword = any(kw in answer_lower for kw in self.busy_keywords)
            
            if self.expected_answer:
                # An expected answer is provided and must match
                if self.expected_answer == 'free':
                    if has_free_keyword and not has_busy_keyword:
                        logging.info("   ✅ Correctly identified as FREE")
                        return 1.0
                    else:
                        logging.warning("   ❌ Expected FREE but answer suggests otherwise")
                        return 0.0
                elif self.expected_answer == 'busy':
                    if has_busy_keyword:
                        logging.info("   ✅ Correctly identified as BUSY")
                        return 1.0
                    else:
                        logging.warning("   ❌ Expected BUSY but answer suggests otherwise")
                        return 0.0
            else:
                # No expected answer is provided; it suffices that the agent provided a reasonable answer
                if has_free_keyword or has_busy_keyword:
                    logging.info("   ✅ Agent provided a clear availability answer")
                    return 1.0
                else:
                    # Check whether time was mentioned
                    if any(t in answer_lower for t in ['pm', 'am', ':', 'afternoon', 'morning']):
                        logging.info("   ✅ Agent mentioned time in response")
                        return 1.0
                    # 🆕 Binary rating: unclear answers are considered failures
                    logging.warning("   ❌ FAIL: Answer doesn't clearly indicate availability")
                    return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Availability Check:")
        logging.info("=" * 60)
        logging.info(f"   Time range: {self.start_time} - {self.end_time}")
        logging.info("=" * 60)



# ============================================================================
# 10. LayeredCalendarCheckConflict - check calendar conflicts (used in the 7-day scenario)
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarCheckConflict")
class CalendarCheckConflictEvaluator(BaseAppEvaluator):
    """
    evaluation calendar conflict detection task
    
    supported scenarios:
    - W3-02: "Add a meeting from 6 PM to 7 PM. Check if there's any conflict with exercise."
    
    evaluation logic: 
    - The agent must identify the conflict between the 6 PM–7 PM event and the daily 6:30 PM exercise habit
    - The conflict is based on the exercise time (18:30) mentioned in prior tasks, not on the calendar database
    - Only check whether the agent's answer mentions the conflict
    - Success = the agent explicitly mentions the conflict in their answer
    - Failure = the agent does not mention the conflict
    
    Note:
    - Do not check the calendar database (because the exercise habit may not be recorded in the calendar)
    - Only evaluate whether the agent remembered the daily 18:30 exercise habit from the context
    """
    
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Event to be created
        self.event_title = params.get('event_title', '')
        self.start_time = params.get('start_time', '18:00')
        self.end_time = params.get('end_time', '19:00')
        
        # Conflicting time (e.g., exercise habit)
        self.conflict_time = params.get('conflict_time', '18:30')
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether the agent correctly identified the conflict
        
        Important: 
        - The conflict is based on the exercise habit (daily at 18:30) mentioned in prior tasks
        - There is no need to check whether an actual event exists in the calendar database
        - It suffices to check whether the agent's response mentions the conflict with the exercise time
        
        Returns:
            float: 1.0 indicates correct conflict identification, 0.0 indicates failure
        """
        from scendroid.apps.calendar import utils as calendar_utils
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Calendar Conflict Check:")
        logging.info("=" * 60)
        logging.info(f"   Event: {self.event_title}")
        logging.info(f"   Time: {self.start_time} - {self.end_time}")
        logging.info(f"   Conflict time: {self.conflict_time} (exercise habit)")
        logging.info(f"   ⚠️  Note: Conflict is based on previously mentioned exercise habit, not calendar DB")
        
        try:
            # 1. get agent's answer
            agent_answer = calendar_utils.get_agent_answer(env)
            
            if not agent_answer:
                logging.warning("   ❌ No agent answer found")
                return 0.0
            
            logging.info(f"   Agent answer: {agent_answer[:200]}...")
            
            # 2. Check whether the agent's answer mentions the conflict
            agent_answer_lower = agent_answer.lower()
            
            conflict_keywords = [
                'conflict', 'clash', 'overlap', 'busy', 'exercise', 
                'already', 'scheduled', 'occupied', 'cant', "can't",
                'cannot', '18:30', '6:30', 'workout', 'fitness',
                'collision', 'interfere', 'interrupt'
            ]
            mentioned_conflict = any(kw in agent_answer_lower for kw in conflict_keywords)
            
            # 3. Check whether it explicitly states not to create an event
            rejection_keywords = [
                "don't create", "won't create", "not create", "avoid creating",
                "shouldn't create", "cannot create", "unable to create",
                "will not add", "won't add", "not add", "avoid adding",
                "decline", "skip", "cancel", "abort"
            ]
            mentioned_rejection = any(kw in agent_answer_lower for kw in rejection_keywords)
            
            # 4. Scoring logic
            if mentioned_conflict:
                logging.info(f"   ✅ Agent mentioned conflict in answer")
                
                if mentioned_rejection:
                    logging.info(f"   ✅ Agent explicitly stated not to create the event")
                    logging.info("   ✅ SUCCESS: Correctly identified conflict and rejected event creation")
                    return 1.0
                else:
                    logging.info("   ⚠️  Agent mentioned conflict but didn't explicitly reject event creation")
                    logging.info("   ✅ PARTIAL SUCCESS: Identified conflict (assuming implicit rejection)")
                    return 1.0  # Success if the conflict is mentioned, because the instruction is "if yes, tell me and don't create"
            else:
                logging.warning("   ❌ Agent did not mention conflict with exercise time")
                logging.warning("   ❌ FAIL: Failed to identify the conflict")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Conflict Check:")
        logging.info(f"   Event to add: {self.event_title}")
        logging.info(f"   Time: {self.start_time} - {self.end_time}")
        logging.info(f"   Conflict at: {self.conflict_time}")
        logging.info("=" * 60)


# ============================================================================
# 9. LayeredCalendarSetEventReminder - setupeventreminder
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarSetEventReminder")
class CalendarSetEventReminderEvaluator(BaseAppEvaluator):
    """
    🆕 evaluation Calendar event remindersetuptask
    
    supported scenarios:
    - W4-03: "Check calendar for keynote event and set it to remind me 5 minutes before"
    
    evaluation content:
    - Find the event containing the specified keyword
    - Check whether the event has the correct reminder set up (X minutes before)
    
    parameter:
    - event_keyword: The keyword for finding the event in the calendar (e.g., "keynote")
    - reminder_minutes_before: The number of minutes before the event to set the reminder (e.g., 5)
    
    Note:
    - Simple Calendar Pro stores reminders in the reminders table
    - reminder.minutes being negative indicates "before" (e.g., -5 means 5 minutes before)
    """
    
    app_names = ("simple calendar pro",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.event_keyword = params.get('event_keyword', '')
        self.reminder_minutes_before = params.get('reminder_minutes_before', 5)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the event reminder is set up correctly
        
        Returns:
            float: 1.0 indicates correct setup, 0.0 indicates failure
        """
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            from scendroid.task_evals.single.calendar import calendar_utils
            
            logging.warning(f"🔍 Checking reminder for event containing '{self.event_keyword}'...")
            logging.warning(f"   Expected reminder: {self.reminder_minutes_before} minutes before")
            
            # 1. Find the event containing the keyword
            events = sqlite_utils.get_rows_from_remote_device(
                calendar_utils.EVENTS_TABLE,
                calendar_utils.DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env,
            )
            
            target_event_id = None
            target_event_title = None
            
            for event in events:
                # CalendarEvent is a dataclass; use property access instead of dict.get()
                title = event.title.lower() if hasattr(event, 'title') and event.title else ''
                if self.event_keyword.lower() in title:
                    target_event_id = event.id if hasattr(event, 'id') else None
                    target_event_title = event.title if hasattr(event, 'title') else ''
                    logging.warning(f"   ✓ Found event: '{target_event_title}' (ID: {target_event_id})")
                    break
            
            if not target_event_id:
                logging.warning(f"   ❌ Event containing '{self.event_keyword}' not found")
                logging.warning("============================================================")
                logging.warning("❌ FAILED - Event not found")
                logging.warning("============================================================")
                return 0.0
            
            # 2. Query the reminders table
            _REMINDERS_TABLE = "reminders"
            
            try:
                reminders = sqlite_utils.get_rows_from_remote_device(
                    _REMINDERS_TABLE,
                    calendar_utils.DB_PATH,
                    sqlite_schema_utils.Reminder,  # Use the Reminder dataclass
                    env,
                )
            except Exception as e:
                logging.warning(f"   ⚠️ Could not read reminders table: {e}")
                reminders = []
            
            # 3. Check the reminder for this event
            event_has_reminder = False
            reminder_minutes = None
            
            for reminder in reminders:
                event_id = reminder.get('event_id')
                minutes = reminder.get('minutes', 0)
                
                if event_id == target_event_id:
                    event_has_reminder = True
                    reminder_minutes = minutes
                    logging.warning(f"   ✓ Found reminder for event: {minutes} minutes")
                    break
            
            if not event_has_reminder:
                logging.warning(f"   ❌ No reminder set for event '{target_event_title}'")
                logging.warning("============================================================")
                logging.warning("❌ FAILED - No reminder set")
                logging.warning("============================================================")
                return 0.0
            
            # 4. Check whether the reminder time is correct
            # Simple Calendar Pro uses negative numbers to indicate "before"
            expected_minutes = -self.reminder_minutes_before
            
            if reminder_minutes == expected_minutes:
                logging.warning(f"   ✅ Reminder correctly set: {self.reminder_minutes_before} minutes before")
                logging.warning("============================================================")
                logging.warning("✅ PASSED - Reminder set correctly")
                logging.warning("============================================================")
                return 1.0
            else:
                logging.warning(f"   ❌ Reminder time mismatch:")
                logging.warning(f"      Expected: {expected_minutes} ({self.reminder_minutes_before} min before)")
                logging.warning(f"      Actual: {reminder_minutes}")
                logging.warning("============================================================")
                logging.warning("❌ FAILED - Reminder time incorrect")
                logging.warning("============================================================")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Set Reminder:")
        logging.info(f"   Event keyword: {self.event_keyword}")
        logging.info(f"   Reminder: {self.reminder_minutes_before} minutes before")
        logging.info("=" * 60)


# ============================================================================
# 12. LayeredCalendarUpdateLocation - Update event location
# ============================================================================

@AppRegistry.register_evaluator("LayeredCalendarUpdateLocation")
class CalendarUpdateLocationEvaluator(BaseAppEvaluator):
    """
    Evaluation for tasks updating calendar event locations
    
    supported scenarios:
    - "Open Simple Calendar Pro and change the location of today's 10:00 AM 'Mountain Picnic' to 'West Peak Lookout'"
    
    evaluation content:
    - Check whether the event location has been updated to the new location
    """
    
    # ScenDroid standard attributes
    app_names = ("calendar",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.event_title = params.get('event_title', '')
        self.old_location = params.get('old_location', '')
        self.new_location = params.get('new_location', '')
        self.event_hour = params.get('event_hour', 10)
        self.event_minute = params.get('event_minute', 0)
        
        # set complexity
        self.complexity = 2.5
    
    # Calendar-specific constants
    _CALENDAR_DB_PATH = "/data/data/com.simplemobiletools.calendar.pro/databases/events.db"
    _EVENTS_TABLE = "events"
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the event location is correctly updated
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        # import on demand
        from scendroid.task_evals.utils import (
            sqlite_utils,
            sqlite_schema_utils,
        )
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Calendar Location Update:")
        logging.warning("=" * 60)
        logging.warning(f"   Event: {self.event_title}")
        logging.warning(f"   Expected location: {self.new_location}")
        logging.warning("=" * 60)
        
        try:
            # Get all events
            events = sqlite_utils.get_rows_from_remote_device(
                self._EVENTS_TABLE,
                self._CALENDAR_DB_PATH,
                sqlite_schema_utils.CalendarEvent,
                env
            )
            
            # Find the target event
            location_updated = False
            for event in events:
                if self.event_title.lower() in (event.title or '').lower():
                    event_location = event.location or ''
                    logging.info(f"   Found event '{event.title}' with location: {event_location}")
                    
                    if self.new_location.lower() in event_location.lower():
                        location_updated = True
                        logging.warning(f"   ✅ Location updated to: {event_location}")
                        break
            
            if location_updated:
                logging.warning("=" * 60)
                logging.warning("✅ PASSED - Location updated successfully")
                logging.warning("=" * 60)
                return 1.0
            else:
                logging.warning("=" * 60)
                logging.warning("❌ FAILED - Location not updated")
                logging.warning("=" * 60)
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Calendar Location Update:")
        logging.info(f"   Event: {self.event_title}")
        logging.info(f"   Old location: {self.old_location}")
        logging.info(f"   New location: {self.new_location}")
        logging.info("=" * 60)

