"""
CrossApp Module

CrossApp cross-app task module, responsible for orchestrating and combining functionalities from multiple apps.

Implemented CrossApp tasks (5):
1. LayeredCrossAppShoppingExpense - Shopping + Expense (compositional)
2. LayeredCrossAppMeetingNotification - Calendar + SMS (collaborative)
3. LayeredCrossAppMeetingUpdateNotify - Calendar + SMS (collaborative)
4. LayeredCrossAppSportsSummary - OpenTracks + Markor (collaborative)
5. LayeredCrossAppScheduleQuery - Calendar + Tasks (question-answering)

Design principles:
- Reuse the initialize and evaluation methods from the App Layer
- Provide orchestration and composition capabilities
- Support weighted scoring and result aggregation
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']

