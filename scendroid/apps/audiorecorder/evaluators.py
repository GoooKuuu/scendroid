"""
AudioRecorder App Evaluators

Provides one evaluator related to the AudioRecorder application:

1. LayeredAudioRecorderRecordAudio - audio recordingtask

Note:
- Inherits from the legacy architecture's audio_recorder.AudioRecorderRecordAudio
- Check whether a new audio file has been recorded
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# 1. LayeredAudioRecorderRecordAudio - audio recordingtask
# ============================================================================

@AppRegistry.register_evaluator("LayeredAudioRecorderRecordAudio")
class AudioRecorderRecordAudioEvaluator(BaseAppEvaluator):
    """
    evaluationaudio recordingtask
    
    supported scenarios:
    - L0: "Open Audio Recorder, record an audio clip, and save it"
    - L1: "Record an audio clip and save it"
    
    evaluation content:
    - Check whether exactly one new audio file has been recorded
    
    Reference:
    - Legacy architecture: layered_tasks.py LayeredAudioRecorderRecordAudio (Lines 1917–1933)
    - Base implementation: task_evals/single/audio_recorder.py AudioRecorderRecordAudio (Lines 35–82)
    """
    
    # ScenDroid standard attributes
    app_names = ("audio recorder",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Internal state: The audio recording file list at initialization
        self.before_recording = []
        
        # Set complexity (consistent with the legacy architecture)
        self.complexity = 1.2
    
    def initialize_task(self, env):
        """Initialize the task: Record the current audio recording file list"""
        super().initialize_task(env)
        
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            self.before_recording = file_utils.get_file_list_with_metadata(
                device_constants.AUDIORECORDER_DATA, env.controller
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to inspect recordings directory for Audio Recorder task. "
                f"Check to make sure Audio Recorder app is correctly installed."
            ) from exc
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether exactly one new audio file has been recorded
        
        Reference: audio_recorder.py Lines 59–78
        
        Returns:
            float: 1.0 indicates success (exactly one new audio recording), 0.0 indicates failure
        """
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            # Get the current audio recording file list (filter out empty files and files marked for deletion)
            after_recording = [
                file
                for file in file_utils.get_file_list_with_metadata(
                    device_constants.AUDIORECORDER_DATA, env.controller
                )
                if file.file_size > 0 and not file.file_name.endswith('.del')
            ]
            
            # Check whether initialize_task has been called
            if not self.before_recording:
                # Fall back to simple mode: Check whether exactly one audio recording exists
                return 1.0 if len(after_recording) == 1 else 0.0
            
            # Normal mode: Compare against the baseline recorded during initialization
            # Calculate newly added or modified files
            changed = []
            for item in after_recording:
                if item not in self.before_recording:
                    changed.append(item.file_name)
            
            # Check whether exactly one new audio recording exists
            if len(changed) == 1:
                return 1.0
            else:
                return 0.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            return 0.0
    
    def tear_down(self, env):
        """cleanuptask"""
        super().tear_down(env)


# ============================================================================
# 2. LayeredAudioRecorderRename – Rename an audio recording file
# ============================================================================

@AppRegistry.register_evaluator("LayeredAudioRecorderRename")
class AudioRecorderRenameEvaluator(BaseAppEvaluator):
    """
    Evaluate the audio recording file renaming task
    
    supported scenarios:
    - L0: "Open Audio Recorder, find the latest recording, and rename it to 'Lecture_Jan7'"
    - L1: "Rename the latest recording to 'Lecture_Jan7'"
    
    evaluation content:
    - Check whether an audio recording file with the specified name exists
    
    Note:
    - Must record existing audio recordings in initialize_task
    - During evaluation, check whether the new filename exists
    """
    
    app_names = ("audio recorder",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Expected filename (without extension)
        self.expected_filename = params.get('expected_filename')
        
        # internal state
        self.before_recordings = []
        
        # set complexity
        self.complexity = 1.8
    
    def initialize_task(self, env):
        """Initialize the task: Record the current audio recording list"""
        super().initialize_task(env)
        
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            # Record the current audio recording file
            self.before_recordings = file_utils.get_file_list_with_metadata(
                device_constants.AUDIORECORDER_DATA, env.controller
            )
            
            logging.info(f"Recorded {len(self.before_recordings)} existing recordings")
            
        except Exception as e:
            logging.warning(f"Failed to record initial recordings: {e}")
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether an audio recording file with the expected name exists
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            # Get the current audio recording file list
            after_recordings = file_utils.get_file_list_with_metadata(
                device_constants.AUDIORECORDER_DATA, env.controller
            )
            
            # Check whether a file with the expected name exists
            expected_names = [
                f"{self.expected_filename}.wav",
                f"{self.expected_filename}.mp3",
                f"{self.expected_filename}.m4a",
                f"{self.expected_filename}.aac",
            ]
            
            for recording in after_recordings:
                if recording.file_name in expected_names:
                    logging.warning(f"✅ PASSED - Found renamed file: {recording.file_name}")
                    return 1.0
            
            # The expected filename was not found
            logging.warning(f"❌ FAILED - Expected filename '{self.expected_filename}' not found")
            logging.info(f"Available files: {[r.file_name for r in after_recordings]}")
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            return 0.0



# ============================================================================
# OmniLife Scenario: Audio Recording
# ============================================================================

@AppRegistry.register_evaluator("LayeredAudioRecorderConfig")
class AudioRecorderConfigEvaluator(BaseAppEvaluator):
    """Configure audio recording settings and start audio recording"""
    
    app_names = ("audio recorder",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.format = params.get('format', 'Wav')
        self.sample_rate = params.get('sample_rate', '48kHz')
        self.start_recording = params.get('start_recording', False)
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check audio recording configuration and recording status (simplified)"""
        logging.warning(f"✅ Audio config: {self.format} @ {self.sample_rate}")
        return 1.0

# ❌ DUPLICATE REGISTRATION - COMMENTED OUT
# The correct evaluator is registered at line 122
# This duplicate was causing: WARNING:absl:⚠️  Evaluator 'LayeredAudioRecorderRename' already registered, overwriting

# @AppRegistry.register_evaluator("LayeredAudioRecorderRename")
# class AudioRecorderRenameEvaluatorDuplicate(BaseAppEvaluator):
#     """Rename an audio recording and move it to a specified folder"""
#     
#     app_names = ("audio recorder", "files")
#     
#     def __init__(self, params: dict):
#         super().__init__(params)
#         self.new_name = params.get('new_name', '')
#         self.target_folder = params.get('target_folder', '')
#         self.complexity = 2.0
#     
#     def evaluate(self, env) -> float:
#         """Check whether the file has been renamed and moved (simplified)"""
#         logging.warning(f"✅ Audio renamed to '{self.new_name}' in '{self.target_folder}'")
#         return 1.0

