# Copyright 2024 The ScenDroid Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Registry for WebArena tasks."""

import json
import os
from typing import Any

from absl import logging
from scendroid.task_evals.webarena import webarena_task


class WebArenaTaskRegistry:
    """Registry for loading and managing WebArena tasks."""
    
    def __init__(self, config_file: str = None):
        """Initialize the WebArena task registry.
        
        Args:
            config_file: Path to WebArena test.raw.json file.
                       If None, uses default path in webarena-main folder.
        """
        if config_file is None:
            # Default path - try multiple possible locations
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
            
            # Try different possible paths
            possible_paths = [
                os.path.join(base_dir, "webarena", "config_files", "test.raw.json"),
                os.path.join(base_dir, "webarena-main", "config_files", "test.raw.json"),
            ]
            
            config_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_file = path
                    break
            
            if config_file is None:
                # If still not found, use the first path as default (will show error with correct path)
                config_file = possible_paths[0]
        
        self.config_file = config_file
        self.all_tasks = self._load_tasks()
        self.shopping_tasks = self._filter_shopping_tasks()
        
        logging.info(f"Loaded {len(self.all_tasks)} total WebArena tasks")
        logging.info(f"Found {len(self.shopping_tasks)} Shopping tasks")
    
    def _load_tasks(self) -> list[dict[str, Any]]:
        """Load tasks from WebArena config file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            return tasks
        except FileNotFoundError:
            logging.error(f"WebArena config file not found: {self.config_file}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing WebArena config: {e}")
            return []
    
    def _filter_shopping_tasks(self) -> list[dict[str, Any]]:
        """Filter tasks for shopping site only."""
        shopping_tasks = []
        for task in self.all_tasks:
            sites = task.get("sites", [])
            if "shopping" in sites:
                shopping_tasks.append(task)
        return shopping_tasks
    
    def get_task_config(self, task_id: int) -> dict[str, Any] | None:
        """Get task configuration by task ID.
        
        Args:
            task_id: WebArena task ID
            
        Returns:
            Task configuration dict or None if not found
        """
        for task in self.shopping_tasks:
            if task.get("task_id") == task_id:
                return task
        return None
    
    def get_all_shopping_task_configs(self) -> list[dict[str, Any]]:
        """Get all shopping task configurations."""
        return self.shopping_tasks
    
    def create_task_registry(self) -> dict[str, type[webarena_task.WebArenaTaskEval]]:
        """Create a task registry compatible with ScenDroid's TaskRegistry.
        
        Returns:
            Dictionary mapping task names to dynamically created task classes
        """
        registry = {}
        
        for task_config in self.shopping_tasks:
            task_id = task_config.get("task_id", -1)
            intent = task_config.get("intent", "")
            eval_types = task_config.get("eval", {}).get("eval_types", [])
            
            # Create a unique task name
            task_name = f"WebArena_Shopping_{task_id}"
            
            # Determine base class based on eval type
            if "string_match" in eval_types:
                base_class = webarena_task.StringMatchWebArenaTask
            elif "url_match" in eval_types:
                base_class = webarena_task.URLMatchWebArenaTask
            elif "program_html" in eval_types:
                base_class = webarena_task.ProgramHTMLWebArenaTask
            else:
                base_class = webarena_task.StringMatchWebArenaTask
            
            # Create a dynamic class for this task
            # IMPORTANT: Use default parameter to capture value, not reference!
            # This avoids the Python closure trap where all lambdas would
            # reference the last task_config after the loop ends.
            def make_params_generator(config):
                """Factory function to capture task_config by value."""
                return classmethod(
                    lambda cls: {
                        "task_id": config.get("task_id", -1),
                        "intent": config.get("intent", ""),
                        "start_url": config.get("start_url", ""),
                        "eval_config": config.get("eval", {}),
                        "require_login": config.get("require_login", False),
                    }
                )
            
            task_class = type(
                task_name,
                (base_class,),
                {
                    "task_id": task_id,
                    "intent_text": intent,
                    "_task_config": task_config,
                    "template": intent,  # Use intent as template
                    
                    # Override generate_random_params to return task-specific params
                    "generate_random_params": make_params_generator(task_config),
                }
            )
            
            registry[task_name] = task_class
        
        return registry
    
    def get_task_by_name(self, task_name: str) -> type[webarena_task.WebArenaTaskEval] | None:
        """Get a task class by name.
        
        Args:
            task_name: Task name (e.g., "WebArena_Shopping_21")
            
        Returns:
            Task class or None if not found
        """
        registry = self.create_task_registry()
        return registry.get(task_name)
    
    def get_task_id_from_name(self, task_name: str) -> int:
        """Extract task ID from task name.
        
        Args:
            task_name: Task name (e.g., "WebArena_Shopping_21")
            
        Returns:
            Task ID or -1 if invalid format
        """
        try:
            # Expected format: "WebArena_Shopping_<ID>"
            parts = task_name.split("_")
            if len(parts) >= 3 and parts[0] == "WebArena" and parts[1] == "Shopping":
                return int(parts[2])
        except (ValueError, IndexError):
            pass
        return -1


# Global registry instance
_global_registry = None


def get_webarena_registry(config_file: str = None) -> WebArenaTaskRegistry:
    """Get the global WebArena task registry.
    
    Args:
        config_file: Optional path to config file. Only used on first call.
        
    Returns:
        WebArenaTaskRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = WebArenaTaskRegistry(config_file)
    return _global_registry


def create_webarena_task_suite() -> dict[str, type[webarena_task.WebArenaTaskEval]]:
    """Create a complete task suite for all WebArena shopping tasks.
    
    Returns:
        Dictionary of task name to task class
    """
    registry = get_webarena_registry()
    return registry.create_task_registry()

