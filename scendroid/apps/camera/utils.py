"""
Camera App Utility Functions

Provides helper functions related to the Camera app.
"""

from absl import logging


def get_media_files(controller, media_type='photo'):
    """
    Get the media file list on the device.
    
    Args:
        controller: ADB controller
        media_type: 'photo' or 'video'
        
    Returns:
        set: A set of file names.
    """
    from scendroid.env import adb_utils, device_constants
    
    if media_type == 'photo':
        path = device_constants.PHOTOS_DATA
    else:
        path = device_constants.VIDEOS_DATA
    
    contents = adb_utils.issue_generic_request(
        ["shell", "ls", path],
        controller,
    )
    
    files = set(
        contents.generic.output.decode().replace("\r", "").split("\n")
    )
    return files


def count_new_files(before_files: set, after_files: set) -> int:
    """
    Calculate the count of newly added files.
    
    Args:
        before_files: The initial set of files.
        after_files: The final set of files.
        
    Returns:
        int: The count of newly added files.
    """
    return len(after_files - before_files)
