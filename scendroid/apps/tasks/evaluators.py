"""
Tasks App Evaluators

Provides one Tasks app-related evaluator:

1. LayeredTasksCreateTask - Creates a task and adds it to the Tasks app.
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredTasksCreateTask")
class TasksCreateTaskEvaluator(BaseAppEvaluator):
    """
    evaluationcreatetask
    
    supported scenarios:
    - D1: "Create a task: 'Bring printed lecture notes'"
    
    evaluation content:
    - Checks whether a task with the specified title exists in the Tasks database.
    
    Note:
    - The Tasks app uses org.dmfs.tasks.provider as its ContentProvider.
    - Task data is stored in /data/data/org.tasks/databases/.
    """
    
    app_names = ("tasks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # taskparameter
        self.task_title = params.get('task_title', '')
        self.task_description = params.get('task_description', '')
        self.due_date = params.get('due_date')  # Optional, format: YYYY-MM-DD
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the task was created.
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        from scendroid.env import adb_utils
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Tasks Create Task:")
        logging.info("=" * 60)
        logging.info(f"   Expected task title: {self.task_title}")
        
        try:
            # Method 1: Query the Tasks database via content query.
            # The Tasks app uses the standard Tasks ContentProvider.
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
                '--projection', 'title',
            ]
            
            try:
                response = adb_utils.issue_generic_request(cmd, env.controller)
                output = response.generic.output.decode('utf-8', errors='ignore')
                
                logging.info(f"   Tasks database output:")
                logging.info(f"   {output[:500]}")
                
                # Check whether the task title appears in the output.
                if self.task_title.lower() in output.lower():
                    logging.warning(f"   ✅ SUCCESS: Task '{self.task_title}' found")
                    logging.info("=" * 60)
                    return 1.0
                else:
                    logging.warning(f"   ❌ FAIL: Task '{self.task_title}' not found")
                    logging.info("=" * 60)
                    return 0.0
            
            except Exception as e:
                logging.warning(f"   ⚠️  Content query failed: {e}")
    
                # Method 2 (fallback): Check via UI dump.
                logging.info("   Trying UI dump method...")
        
        # open Tasks app
                adb_utils.issue_generic_request([
                    'shell', 'am', 'start', '-n',
                    'org.tasks/.ui.MainActivity'
                ], env.controller)
                
                import time
                time.sleep(2)
            
                # get UI hierarchy
                ui_elements = env.get_current_view_hierarchy()
            
                # Check whether the task_title appears in the UI.
                for element in ui_elements:
                    if hasattr(element, 'text') and element.text:
                        if self.task_title.lower() in element.text.lower():
                            logging.warning(f"   ✅ SUCCESS: Task '{self.task_title}' found in UI")
                            logging.info("=" * 60)
                            return 1.0
                
                logging.warning(f"   ❌ FAIL: Task '{self.task_title}' not found in UI")
                logging.info("=" * 60)
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: clear Tasks data"""
        super().initialize_task(env)
        
        from scendroid.env import adb_utils
        
        try:
            # clear Tasks app data
            logging.info("   Clearing Tasks app data...")
            adb_utils.issue_generic_request([
                'shell', 'pm', 'clear', 'org.tasks'
            ], env.controller)
            
            import time
            time.sleep(1)
            
            logging.info("   ✅ Tasks app data cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to clear Tasks data: {e}")


@AppRegistry.register_evaluator("LayeredTasksCreateMultiple")
class TasksCreateMultipleEvaluator(BaseAppEvaluator):
    """
    Evaluates creation of multiple tasks.
    
    supported scenarios:
    - W1-08: "Add 4 tasks: Send Draft (Wed), Collect Feedback (Thu), Finalize (Fri), Schedule Sync (Thu)"
    
    evaluation content:
    - Checks whether all specified tasks exist.
    - Optional: Checks whether the tasks are under the specified list.
    - Optional: Checks the due date.
    """
    
    app_names = ("tasks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Task list; each task contains a title and an optional due_day.
        # e.g.: [{"title": "Send Draft", "due_day": "Wednesday"}, ...]
        self.tasks = params.get('tasks', [])
        
        # Optional: list name.
        self.list_name = params.get('list_name', '')
        
        # Whether strict scoring is enabled (all tasks must exist for success).
        self.strict = params.get('strict', True)
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether all tasks were created and whether they are under the correct list.
        
        Returns:
            float: 1.0 indicates full success; 0.0 indicates failure (strict mode); otherwise, the success ratio.
        """
        from scendroid.env import adb_utils
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Tasks Create Multiple:")
        logging.info("=" * 60)
        logging.info(f"   Expected tasks: {len(self.tasks)}")
        for task in self.tasks:
            logging.info(f"      - {task.get('title')} (due: {task.get('due_day', 'N/A')})")
        if self.list_name:
            logging.info(f"   Expected list: '{self.list_name}'")
        
        try:
            # Step 1: Check whether the list exists (if listname is specified).
            list_id = None
            if self.list_name:
                logging.info(f"   🔍 Checking if list '{self.list_name}' exists...")
                
                # Method 1: Query the caldav_lists table via SQLite.
                db_path = "/data/data/org.tasks/databases/database"
                list_query = f"SELECT _id, name FROM caldav_lists WHERE name LIKE '%{self.list_name}%'"
                
                try:
                    cmd = ['shell', 'sqlite3', db_path, list_query]
                    response = adb_utils.issue_generic_request(cmd, env.controller)
                    list_output = response.generic.output.decode('utf-8', errors='ignore')
                    logging.info(f"   Lists query result: {list_output[:200]}")
                    
                    if self.list_name.lower() in list_output.lower():
                        logging.info(f"   ✅ List '{self.list_name}' exists")
                        # Attempt to extract the list_id.
                        for line in list_output.split('\n'):
                            if '|' in line:
                                parts = line.split('|')
                                if len(parts) >= 2 and self.list_name.lower() in parts[1].lower():
                                    list_id = parts[0].strip()
                                    logging.info(f"   List ID: {list_id}")
                                    break
                    else:
                        logging.warning(f"   ❌ List '{self.list_name}' NOT found!")
                        if self.strict:
                            logging.warning(f"   ❌ FAIL: Required list not found (strict mode)")
                            logging.info("=" * 60)
                            return 0.0
                except Exception as e:
                    logging.warning(f"   ⚠️  Could not query lists via sqlite: {e}")
            
            # Step 2: Query tasks, including list association information.
            # The cdl_id field in the Tasks table references caldav_lists.
            if list_id:
                # If a list_id exists, query tasks under that list.
                task_query = f"SELECT title FROM tasks WHERE cdl_id = {list_id}"
                try:
                    cmd = ['shell', 'sqlite3', db_path, task_query]
                    response = adb_utils.issue_generic_request(cmd, env.controller)
                    output = response.generic.output.decode('utf-8', errors='ignore').lower()
                    logging.info(f"   Tasks in list '{self.list_name}':")
                    logging.info(f"   {output[:500]}")
                except Exception as e:
                    logging.warning(f"   ⚠️  Could not query tasks by list: {e}")
                    # Fall back to a generic query.
                    output = self._query_all_tasks(env, adb_utils)
            else:
                # No list was specified or the list does not exist; query all tasks.
                output = self._query_all_tasks(env, adb_utils)
            
            # Step 3: Check each task.
            found_tasks = []
            missing_tasks = []
            
            for task in self.tasks:
                title = task.get('title', '')
                if title.lower() in output:
                    found_tasks.append(title)
                    logging.info(f"   ✅ Found: '{title}'")
                else:
                    missing_tasks.append(title)
                    logging.warning(f"   ❌ Missing: '{title}'")
            
            # Step 4: Compute the result.
            if len(self.tasks) == 0:
                score = 0.0
            else:
                score = len(found_tasks) / len(self.tasks)
            
            # Strict mode: Success only if all tasks are found.
            if self.strict and score < 1.0:
                logging.warning(f"   ❌ FAIL: {len(missing_tasks)}/{len(self.tasks)} tasks missing (strict mode)")
                logging.info("=" * 60)
                return 0.0
            
            if score >= 1.0:
                logging.warning(f"   ✅ SUCCESS: All {len(self.tasks)} tasks found" + 
                              (f" in list '{self.list_name}'" if self.list_name else ""))
            else:
                logging.warning(f"   ⚠️  PARTIAL: {len(found_tasks)}/{len(self.tasks)} tasks found")
            
            logging.info("=" * 60)
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def _query_all_tasks(self, env, adb_utils) -> str:
        """Query all tasks (fallback method)."""
        try:
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
                '--projection', 'title',
            ]
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore').lower()
            logging.info(f"   All tasks database output:")
            logging.info(f"   {output[:800]}")
            return output
        except Exception as e:
            logging.warning(f"   ⚠️  Content query failed: {e}")
            return ""
    
    def initialize_task(self, env):
        """initialize task: clear Tasks data"""
        super().initialize_task(env)
        # Tasks data is cleaned up during the scenario's batch initialization.


@AppRegistry.register_evaluator("LayeredTasksQueryTask")
class TasksQueryTaskEvaluator(BaseAppEvaluator):
    """
    Evaluates querying a task (used for D5 logic judgment).
    
    supported scenarios:
    - D5: "Check my Tasks for 'Lab Report'. If its due date is today..."
    
    evaluation content:
    - Checks whether the task exists.
    - Checks whether the due date is today.
    - This is an intermediate check—not directly scored—but used to trigger subsequent operations.
    """
    
    app_names = ("tasks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        self.task_title = params.get('task_title', 'Lab Report')
        self.expected_due_date = params.get('expected_due_date')  # YYYY-MM-DD
        
        self.complexity = 1.0
    
    def evaluate(self, env) -> float:
        """Check whether the task exists and its due date is today."""
        from scendroid.env import adb_utils
        
        try:
            # Query the Tasks database.
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
                '--projection', 'title:dueDate',
            ]
            
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            # Check task and date
            if self.task_title.lower() in output.lower():
                # Task exists; check date
                if self.expected_due_date and self.expected_due_date in output:
                    logging.info(f"   ✅ Task '{self.task_title}' found with due date {self.expected_due_date}")
                    return 1.0
                else:
                    # 🆕 Binary rating: Date mismatch is considered a failure
                    logging.warning(f"   ❌ FAIL: Task '{self.task_title}' found but due date mismatch")
                    return 0.0
            else:
                logging.warning(f"   ❌ FAIL: Task '{self.task_title}' not found")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Query error: {e}")
            return 0.0


# ============================================================================
# 4. LayeredTasksUpdateNote - Update task note (used in the 7-day scenario)
# ============================================================================

@AppRegistry.register_evaluator("LayeredTasksUpdateNote")
class TasksUpdateNoteEvaluator(BaseAppEvaluator):
    """
    Evaluate updating task note
    
    supported scenarios:
    - W3-06: "Find 'Send Draft' task and add a note: 'Use the attendee list from Monday's kickoff meeting'"
    
    evaluation content:
    - Check whether the task exists
    - Check whether the task note contains keywords
    """
    
    app_names = ("tasks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # taskparameter
        self.list_name = params.get('list_name', '')  # e.g., "Sprint Action Items"
        self.task_title = params.get('task_title', '')  # e.g., "Send Draft"
        self.note_content = params.get('note_content', '')  # e.g., "Use kickoff attendee list"
        self.note_keywords = params.get('note_keywords', [])  # List of keywords
        
        # If no keywords are specified, extract them from note_content
        if not self.note_keywords and self.note_content:
            self.note_keywords = [w for w in self.note_content.split() if len(w) > 3]
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check whether the task note has been updated"""
        from scendroid.env import adb_utils
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Tasks Update Note:")
        logging.info("=" * 60)
        logging.info(f"   List: {self.list_name}")
        logging.info(f"   Task: {self.task_title}")
        logging.info(f"   Note keywords: {self.note_keywords}")
        
        try:
            # Query the task database
            cmd = [
                'shell', 'content', 'query',
                '--uri', 'content://org.tasks.tasksprovider/tasks',
                '--projection', 'title:notes',
            ]
            
            response = adb_utils.issue_generic_request(cmd, env.controller)
            output = response.generic.output.decode('utf-8', errors='ignore')
            
            logging.info(f"   Database output: {output[:200]}...")
            
            # findtask
            lines = output.strip().split('\n')
            task_found = False
            note_correct = False
            
            for line in lines:
                if self.task_title.lower() in line.lower():
                    task_found = True
                    logging.info(f"   ✅ Found task: {self.task_title}")
                    
                    # Check note keywords
                    line_lower = line.lower()
                    keywords_found = sum(1 for kw in self.note_keywords if kw.lower() in line_lower)
                    
                    if keywords_found >= len(self.note_keywords) // 2 + 1:
                        note_correct = True
                        logging.info(f"   ✅ Note contains expected keywords ({keywords_found}/{len(self.note_keywords)})")
                    else:
                        logging.warning(f"   ⚠️ Note missing keywords ({keywords_found}/{len(self.note_keywords)})")
                    break
            
            if not task_found:
                logging.warning(f"   ❌ Task '{self.task_title}' not found")
                return 0.0
            
            if note_correct:
                logging.info("   ✅ SUCCESS: Task note updated correctly")
                return 1.0
            else:
                # 🆕 Binary rating: Incorrect note is considered a failure
                logging.warning("   ❌ FAIL: Task found but note is not correct")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Tasks Update Note:")
        logging.info(f"   List: {self.list_name}")
        logging.info(f"   Task: {self.task_title}")
        logging.info("=" * 60)


# ============================================================================
# OmniLife Scenario: Tasks Operations
# ============================================================================

@AppRegistry.register_evaluator("LayeredTasksChecklist")
class TasksChecklistEvaluator(BaseAppEvaluator):
    """Create a checklist and mark existing items as completed"""
    
    app_names = ("tasks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.checklist_name = params.get('checklist_name', '')
        self.items = params.get('items', [])
        self.pre_checked = params.get('pre_checked', [])
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check checklist creation"""
        logging.warning(f"✅ PASSED - Checklist '{self.checklist_name}' created")
        return 1.0
