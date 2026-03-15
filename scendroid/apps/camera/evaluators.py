"""
Camera App Evaluators

Provides Camera app-related evaluators (2):

1. LayeredCameraTakePhoto - Take a photo
2. LayeredCameraTakeVideo - Record a video

Note: all scendroid.env imports are done inside functions
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# 1. LayeredCameraTakePhoto - Take a photo
# ============================================================================

@AppRegistry.register_evaluator("LayeredCameraTakePhoto")
class CameraTakePhotoEvaluator(BaseAppEvaluator):
    """
    Evaluate the photo-taking task
    
    supported scenarios:
    - L0: "Open Camera, switch to Photo mode, take one photo"
    - L1: "Take a photo."
    
    evaluation content:
    - Check whether a new photo has been taken
    """
    
    # ScenDroid standard attributes
    app_names = ("camera",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # internal state
        self.before_photos = set()
        
        # set complexity
        self.complexity = 1.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether a new photo has been taken
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            from scendroid.env import adb_utils, device_constants
            
            # Get the current photo list
            contents = adb_utils.issue_generic_request(
                ["shell", "ls", device_constants.PHOTOS_DATA],
                env.controller
            )
            after_photos = set(
                contents.generic.output.decode().replace("\r", "").split("\n")
            )
            
            # Calculate the count of newly added photos
            new_photos_count = len(after_photos - self.before_photos)
            
            logging.warning("📊 Camera Photo Evaluation:")
            logging.warning(f"   Photos before: {len(self.before_photos)}")
            logging.warning(f"   Photos after: {len(after_photos)}")
            logging.warning(f"   New photos: {new_photos_count}")
            
            if new_photos_count == 1:
                logging.warning("✅ PASSED - Exactly 1 new photo")
                return 1.0
            else:
                logging.warning(f"❌ FAILED - Expected 1 new photo, got {new_photos_count}")
                return 0.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Record the current photo list
        """
        from scendroid.env import adb_utils, device_constants
        
        super().initialize_task(env)
        
        contents = adb_utils.issue_generic_request(
            ["shell", "ls", device_constants.PHOTOS_DATA],
            env.controller
        )
        self.before_photos = set(
            contents.generic.output.decode().replace("\r", "").split("\n")
        )
        logging.info(f"Initial photos count: {len(self.before_photos)}")


# ============================================================================
# 2. LayeredCameraTakeVideo - Record a video
# ============================================================================

@AppRegistry.register_evaluator("LayeredCameraTakeVideo")
class CameraTakeVideoEvaluator(BaseAppEvaluator):
    """
    Evaluate the video-recording task
    
    supported scenarios:
    - L0: "Open Camera, switch to Video mode, record a video, then stop"
    - L1: "Take a video"
    
    evaluation content:
    - Check whether a new video has been recorded
    """
    
    # ScenDroid standard attributes
    app_names = ("camera",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # internal state
        self.before_videos = set()
        
        # set complexity
        self.complexity = 1.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether a new video has been recorded
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            from scendroid.env import adb_utils, device_constants
            
            # Get the current video list
            contents = adb_utils.issue_generic_request(
                ["shell", "ls", device_constants.VIDEOS_DATA],
                env.controller
            )
            after_videos = set(
                contents.generic.output.decode().replace("\r", "").split("\n")
            )
            
            # Calculate the count of newly added videos
            new_videos_count = len(after_videos - self.before_videos)
            
            logging.warning("📊 Camera Video Evaluation:")
            logging.warning(f"   Videos before: {len(self.before_videos)}")
            logging.warning(f"   Videos after: {len(after_videos)}")
            logging.warning(f"   New videos: {new_videos_count}")
            
            if new_videos_count == 1:
                logging.warning("✅ PASSED - Exactly 1 new video")
                return 1.0
            else:
                logging.warning(f"❌ FAILED - Expected 1 new video, got {new_videos_count}")
                return 0.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Record the current video list
        """
        from scendroid.env import adb_utils, device_constants
        
        super().initialize_task(env)
        
        contents = adb_utils.issue_generic_request(
            ["shell", "ls", device_constants.VIDEOS_DATA],
            env.controller
        )
        self.before_videos = set(
            contents.generic.output.decode().replace("\r", "").split("\n")
        )
        logging.info(f"Initial videos count: {len(self.before_videos)}")
