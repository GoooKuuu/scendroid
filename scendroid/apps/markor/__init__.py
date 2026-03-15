"""
Markor App Module

Markor app-related evaluators (3)
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']
