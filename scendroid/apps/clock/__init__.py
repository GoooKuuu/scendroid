"""
Clock App Module

Provides Clock app-related evaluators and initialization functions.

evaluator:
- LayeredClockSetAlarm: setupalarm
- LayeredClockDisableAllAlarms: Disable all alarms
- LayeredClockStartTimer: Start the timer
"""

# Import evaluators (trigger registration)
from . import evaluators

__all__ = ['evaluators']

