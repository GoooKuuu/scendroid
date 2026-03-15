"""
Calendar App Module

Provides evaluators and initialization functions related to the Simple Calendar Pro app.  

Evaluators (8):  
- LayeredCalendarCreateMeeting: Create a calendar meeting/event.  
- LayeredCalendarCreateRecurringEvent: Create a recurring event.  
- LayeredCalendarDeleteEventsOnDate: Delete all events on a specific date.  
- LayeredCalendarGetNextEvent: Get the next upcoming event (information retrieval).  
- LayeredCalendarDeleteEventByTime: Delete a specific event by time.  
- LayeredCalendarEditNote: Edit an event's note/description.  
- LayeredCalendarCheckMeetingAnswer: Check answers regarding calendar meetings (information retrieval).  
- LayeredCalendarExtractAttendees: Extract the list of event attendees (information retrieval).  
"""

# Import evaluators (for trigger registration)
from . import evaluators

__all__ = ['evaluators']

