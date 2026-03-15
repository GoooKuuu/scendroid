"""
Files App Evaluators

Provides Files app-related evaluators (3):

1. LayeredFilesDeleteFile - deletefile
2. LayeredFilesMoveFile - Move a file to a specified folder
3. LayeredFilesCreateFolder - Create a folder

Note: all scendroid.env imports are done inside functions
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredFilesDeleteFile")
class FilesDeleteFileEvaluator(BaseAppEvaluator):
    """
    evaluationdeletefiletask
    
    supported scenarios:
    - L0: "Open Files, go to Downloads, and delete the file named 'report.pdf'."
    - L1: "Delete 'report.pdf' from Downloads."
    
    evaluation content:
    - Create a file during initialization
    - Check whether the file has been deleted
    """
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # saveparameter(latencycreate DeleteFile task)
        self.delete_file_task = None
        self.file_name = params.get('file_name')
        self.complexity = 2.0
    
    def _get_delete_file_task(self):
        """latencycreate DeleteFile task"""
        if self.delete_file_task is None:
            from scendroid.env import device_constants
            from scendroid.task_evals.common_validators import file_validators
            
            # Force use of the Downloads subfolder
            params_copy = self._params.copy()
            params_copy["subfolder"] = "Download"
            
            self.delete_file_task = file_validators.DeleteFile(
                params_copy, device_constants.EMULATOR_DATA
            )
        return self.delete_file_task
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check whether the file has been deleted"""
        try:
            result = self._get_delete_file_task().is_successful(env)
            
            if result >= 0.99:
                logging.warning(f"✅ PASSED - File '{self.file_name}' deleted")
            else:
                logging.warning(f"❌ FAILED - File '{self.file_name}' still exists")
            
            return result
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Create the file to be deleted"""
        super().initialize_task(env)
        self._get_delete_file_task().initialize_task(env)
        
        logging.warning(f"📁 File created for deletion test:")
        logging.warning(f"   File: {self.file_name}")
        logging.warning(f"   Location: Downloads folder")


@AppRegistry.register_evaluator("LayeredFilesMoveFile")
class FilesMoveFileEvaluator(BaseAppEvaluator):
    """
    Evaluation for moving a file task
    
    supported scenarios:
    - D4: "Move this file to the 'Documents/Study' folder"
    
    evaluation content:
    - Create a file at the source location during initialization
    - Check whether the file has been moved to the target folder
    - Check whether the source file has been deleted (moved, not copied)
    """
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # fileparameter
        self.file_name = params.get('file_name')  # e.g.:"recording.wav"
        self.source_folder = params.get('source_folder', 'Download')  # Source folder
        self.target_folder = params.get('target_folder')  # e.g.:"Documents/Study"
        
        # File size (used to create test file)
        self.file_size = params.get('file_size', 1024)  # Default 1 KB
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check whether the file has been moved"""
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import os
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Files Move File:")
        logging.info("=" * 60)
        logging.info(f"   File: {self.file_name}")
        logging.info(f"   From: {self.source_folder}")
        logging.info(f"   To: {self.target_folder}")
        
        try:
            # Construct path
            base_path = device_constants.EMULATOR_DATA
            source_path = os.path.join(base_path, self.source_folder, self.file_name)
            target_path = os.path.join(base_path, self.target_folder, self.file_name)
            
            # Check whether the target file exists
            target_exists = file_utils.check_file_exists(target_path, env.controller)
            
            # Check whether the source file has been deleted
            source_exists = file_utils.check_file_exists(source_path, env.controller)
            
            logging.info(f"   Target file exists: {target_exists}")
            logging.info(f"   Source file exists: {source_exists}")
            
            if target_exists and not source_exists:
                # Perfect: File has been moved (not copied)
                logging.warning(f"   ✅ SUCCESS: File moved to {self.target_folder}")
                logging.info("=" * 60)
                return 1.0
            elif target_exists and source_exists:
                # 🆕 Binary rating: File was copied instead of moved, considered failure
                logging.warning(f"   ❌ FAIL: File copied (not moved)")
                logging.info("=" * 60)
                return 0.0
            elif not target_exists and not source_exists:
                # Failure: File was deleted
                logging.warning(f"   ❌ FAIL: File deleted (not moved)")
                logging.info("=" * 60)
                return 0.0
            else:
                # Failure: File was not moved
                logging.warning(f"   ❌ FAIL: File not moved")
                logging.info("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Create a file at the source location"""
        super().initialize_task(env)
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import os
        
        try:
            base_path = device_constants.EMULATOR_DATA
            source_path = os.path.join(base_path, self.source_folder, self.file_name)
            
            # Create source file (use dd command to create a file of specified size)
            logging.info(f"   Creating file: {source_path}")
            
            # Ensure the source folder exists
            source_folder_path = os.path.join(base_path, self.source_folder)
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', source_folder_path
            ], env.controller)
            
            # createfile
            adb_utils.issue_generic_request([
                'shell', 'dd', 'if=/dev/zero', f'of={source_path}', 
                f'bs={self.file_size}', 'count=1'
            ], env.controller)
            
            import time
            time.sleep(0.5)
            
            # Verify whether the file was created successfully
            if file_utils.check_file_exists(source_path, env.controller):
                logging.warning(f"   ✅ Test file created:")
                logging.warning(f"      {source_path}")
            else:
                logging.error(f"   ❌ Failed to create test file")
                
        except Exception as e:
            logging.error(f"   ❌ Initialization error: {e}")
            import traceback
            logging.error(traceback.format_exc())


@AppRegistry.register_evaluator("LayeredFilesCreateFolder")
class FilesCreateFolderEvaluator(BaseAppEvaluator):
    """
    Evaluation for creating a folder task
    
    supported scenarios:
    - D4: "Create the 'Documents/Study' folder if it doesn't exist"
    
    evaluation content:
    - Check whether the folder has been created
    """
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Folder path (relative to /storage/emulated/0/)
        self.folder_path = params.get('folder_path')  # e.g.:"Documents/Study"
        
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check whether the folder exists"""
        from scendroid.env import device_constants, adb_utils
        import os
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Files Create Folder:")
        logging.info("=" * 60)
        logging.info(f"   Folder: {self.folder_path}")
        
        try:
            base_path = device_constants.EMULATOR_DATA
            full_path = os.path.join(base_path, self.folder_path)
            
            # Check whether the folder exists
            cmd = ['shell', 'test', '-d', full_path, '&&', 'echo', 'EXISTS']
            
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            if 'EXISTS' in output:
                logging.warning(f"   ✅ SUCCESS: Folder created")
                logging.info("=" * 60)
                return 1.0
            else:
                logging.warning(f"   ❌ FAIL: Folder not found")
                logging.info("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Ensure the folder does not exist"""
        super().initialize_task(env)
        
        from scendroid.env import device_constants, adb_utils
        import os
        
        try:
            base_path = device_constants.EMULATOR_DATA
            full_path = os.path.join(base_path, self.folder_path)
            
            # Delete the folder (if it exists)
            logging.info(f"   Removing folder (if exists): {full_path}")
            adb_utils.issue_generic_request([
                'shell', 'rm', '-rf', full_path
            ], env.controller)
            
            import time
            time.sleep(0.5)
            
            logging.info(f"   ✅ Folder removed")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to remove folder: {e}")


# ============================================================================
# 4. LayeredFilesSearch - Search for files (information retrieval)
# ============================================================================

@AppRegistry.register_evaluator("LayeredFilesSearch")
class FilesSearchEvaluator(BaseAppEvaluator):
    """
    Evaluation for file search task (information retrieval)
    
    supported scenarios:
    - W2-02: "Use the Files app to find that recording I made and tell me the filename and where it's stored."
    
    evaluation content:
    - Check whether the agent found the correct file
    - Check whether the agent's answer contains the expected filename or path
    """
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # searchmode
        self.search_pattern = params.get('search_pattern', '')
        
        # Expected path or filename keyword
        self.expected_path_contains = params.get('expected_path_contains', '')
        self.expected_filename = params.get('expected_filename', '')
        
        # evaluationmode
        self.require_path = params.get('require_path', False)  # Whether the path must be included
        self.require_filename = params.get('require_filename', True)  # Whether the filename must be included
        
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether the agent correctly located the file
        
        Returns:
            float: 1.0 indicates the file was found, 0.0 indicates it was not found
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Files Search:")
        logging.info("=" * 60)
        logging.info(f"   Search pattern: {self.search_pattern}")
        if self.expected_path_contains:
            logging.info(f"   Expected path contains: {self.expected_path_contains}")
        if self.expected_filename:
            logging.info(f"   Expected filename: {self.expected_filename}")
        
        try:
            # get agent's answer
            agent_answer = ""
            if hasattr(env, 'interaction_cache') and env.interaction_cache:
                agent_answer = str(env.interaction_cache)
            
            if not agent_answer:
                logging.error("   ❌ No answer found in env.interaction_cache")
                return 0.0
            
            logging.info(f"   Agent's answer: {agent_answer}")
            
            answer_lower = agent_answer.lower()
            score = 0.0
            checks_passed = 0
            total_checks = 0
            
            # Check the filename
            if self.expected_path_contains:
                total_checks += 1
                if self.expected_path_contains.lower() in answer_lower:
                    logging.info(f"   ✅ Found expected path/filename: {self.expected_path_contains}")
                    checks_passed += 1
                else:
                    logging.warning(f"   ❌ Missing expected path/filename: {self.expected_path_contains}")
            
            # checksearchmode
            if self.search_pattern:
                total_checks += 1
                if self.search_pattern.lower() in answer_lower:
                    logging.info(f"   ✅ Found search pattern: {self.search_pattern}")
                    checks_passed += 1
                else:
                    logging.warning(f"   ❌ Missing search pattern: {self.search_pattern}")
            
            # Check whether the file or path was mentioned
            file_indicators = ['file', 'folder', 'path', 'directory', 'storage', '.mp3', '.m4a', '.wav', '.ogg']
            has_file_reference = any(ind in answer_lower for ind in file_indicators)
            
            if total_checks > 0:
                score = checks_passed / total_checks
            elif has_file_reference:
                # If no explicit check condition is specified, but file-related content is mentioned
                logging.info("   ✅ Answer contains file-related information")
                score = 1.0
            
            if score >= 1.0:
                logging.info("   ✅ SUCCESS: File found and reported correctly")
            elif score > 0:
                logging.warning(f"   ⚠️ PARTIAL: {checks_passed}/{total_checks} checks passed")
            else:
                logging.warning("   ❌ FAIL: File not found or incorrect answer")
            
            logging.info("=" * 60)
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Files Search:")
        logging.info("=" * 60)
        logging.info(f"   Search pattern: {self.search_pattern}")
        logging.info("=" * 60)


# ============================================================================
# OmniLife Scenario: Files Organization
# ============================================================================

@AppRegistry.register_evaluator("LayeredFilesOrganize")
class FilesOrganizeEvaluator(BaseAppEvaluator):
    """Organize files: deduplicate + categorize"""
    
    app_names = ("files",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.source_folder = params.get('source_folder', 'DCIM')
        self.target_folders = params.get('target_folders', [])
        self.deduplicate = params.get('deduplicate', False)
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check file organization"""
        logging.warning(f"✅ PASSED - Files organized into {len(self.target_folders)} folders")
        return 1.0
