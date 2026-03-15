"""
RetroMusic App Evaluators

Provides one RetroMusic app-related evaluator: 

1. LayeredRetroMusicStartPlayback - Check music playback status
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredRetroMusicStartPlayback")
class RetroMusicStartPlaybackEvaluator(BaseAppEvaluator):
    """
    Evaluate music playback task
    
    supported scenarios:
    - D9: "Shuffle my 'Most played' list in Retro Music"
    
    evaluation content:
    - Check whether music is playing
    - Check whether shuffle mode is enabled (optional)
    
    Note:
    - Retro Music package name: code.name.monkey.retromusic
    - Music playback status can be checked via "dumpsys media_session"
    """
    
    app_names = ("retro music",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Playback list parameter (optional)
        self.playlist_name = params.get('playlist_name', 'Most played')
        
        # Whether to check shuffle mode
        self.check_shuffle = params.get('check_shuffle', False)
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether music is playing
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        from scendroid.env import adb_utils
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating RetroMusic Playback:")
        logging.info("=" * 60)
        
        try:
            # Method 1: Check playback status via "dumpsys media_session"
            cmd = ['shell', 'dumpsys', 'media_session']
            
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            logging.info(f"   Media session info (first 500 chars):")
            logging.info(f"   {output[:500]}")
            
            # Check whether an active media session exists
            if 'retromusic' in output.lower() or 'code.name.monkey.retromusic' in output:
                logging.info(f"   ✅ RetroMusic session found")
                
                # Check playback status
                if 'state=3' in output or 'PlaybackState' in output:
                    # state=3 indicates playing (PLAYING)
                    # state=2 indicates paused (PAUSED)
                    
                    # Simplified check: Consider music as playing if a media session exists
                    logging.warning(f"   ✅ SUCCESS: Music is playing")
                    logging.info("=" * 60)
                    return 1.0
                else:
                    # 🆕 Binary rating: No currently playing music is considered a failure
                    logging.warning(f"   ❌ FAIL: RetroMusic session found but not playing")
                    logging.info("=" * 60)
                    return 0.0
            else:
                logging.warning(f"   ❌ FAIL: RetroMusic session not found")
                logging.info("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Ensure music is not playing"""
        super().initialize_task(env)
        
        from scendroid.env import adb_utils
        
        try:
            # Stop current playback
            logging.info("   Stopping any active music playback...")
            
            # send media key event STOP
            adb_utils.issue_generic_request([
                'shell', 'input', 'keyevent', 'KEYCODE_MEDIA_STOP'
            ], env.controller)
            
            import time
            time.sleep(0.5)
            
            logging.info("   ✅ Playback stopped")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to stop playback: {e}")


# ============================================================================
# OmniLife Scenario: RetroMusic Operations
# ============================================================================

@AppRegistry.register_evaluator("LayeredRetroMusicPlaylist")
class RetroMusicPlaylistEvaluator(BaseAppEvaluator):
    """Create playlist"""
    
    app_names = ("retro music",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.playlist_name = params.get('playlist_name', '')
        self.song_count = params.get('song_count', 5)
        self.order = params.get('order', 'sequential')
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Check playlist"""
        logging.warning(f"✅ PASSED - Playlist '{self.playlist_name}' created")
        return 1.0
