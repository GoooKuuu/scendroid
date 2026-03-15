"""
Files App Module

Files app-related evaluator (1)
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']
