"""
Camera App Module

Camera app-related evaluators (2):
1. LayeredCameraTakePhoto - Take a photo
2. LayeredCameraTakeVideo - Record a video

These evaluators are based on ScenDroid's camera module
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']
