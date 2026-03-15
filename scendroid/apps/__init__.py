"""
App Layer - Automatically load all app modules

This module is responsible for:
1. Exporting the registry and base classes for use by other modules
2. Automatically importing all app submodules (triggering evaluator registration)
3. Providing a convenient query interface

usage:
    from scendroid.apps import AppRegistry
    
    # getevaluator
    evaluator_class = AppRegistry.get_evaluator("LayeredClockSetAlarm")
    
    # getinitializefunction
    setup_func = AppRegistry.get_setup_function("clock", "setup_alarm")
"""

import os
import importlib
import logging

# ============================================================================
# 1. Export core components
# ============================================================================

from .registry import AppRegistry
from .base import BaseAppEvaluator, BaseSetupFunction

__all__ = ['AppRegistry', 'BaseAppEvaluator', 'BaseSetupFunction']

# ============================================================================
# 2. Automatically import all app modules
# ============================================================================

# Get the current directory path
_current_dir = os.path.dirname(__file__)

# Record successfully loaded modules
_loaded_modules = []
_failed_modules = []

# Traverse the directory to find all app modules
for item in os.listdir(_current_dir):
    item_path = os.path.join(_current_dir, item)
    
    # Skip special files and directories
    if item.startswith('_') or item.startswith('.'):
        continue
    
    if item in ['registry.py', 'base.py', '__pycache__']:
        continue
    
    # Only import directories containing __init__.py (app modules)
    if os.path.isdir(item_path):
        init_file = os.path.join(item_path, '__init__.py')
        
        if os.path.exists(init_file):
            try:
                # Dynamically import the app module
                # This triggers decorators in the module, automatically registering evaluators and initializing functions
                module = importlib.import_module(f'.{item}', package='scendroid.apps')
                _loaded_modules.append(item)
                logging.debug(f"✅ Loaded app module: {item}")
            except Exception as e:
                _failed_modules.append((item, str(e)))
                logging.warning(f"⚠️  Failed to load app module '{item}': {e}")
                # Do not raise exceptions; continue loading other modules

# ============================================================================
# 3. Record load statistics
# ============================================================================

_total_evaluators = len(AppRegistry._evaluators)
_total_setup_functions = len(AppRegistry._setup_functions)

logging.info(f"{'='*80}")
logging.info(f"📦 App Layer Initialization Complete")
logging.info(f"{'='*80}")
logging.info(f"✅ Loaded Modules: {len(_loaded_modules)}")
if _loaded_modules:
    for module_name in sorted(_loaded_modules):
        logging.info(f"   - {module_name}")

if _failed_modules:
    logging.warning(f"⚠️  Failed Modules: {len(_failed_modules)}")
    for module_name, error in _failed_modules:
        logging.warning(f"   - {module_name}: {error}")

logging.info(f"📊 Registry Statistics:")
logging.info(f"   - Total Evaluators: {_total_evaluators}")
logging.info(f"   - Total Setup Functions: {_total_setup_functions}")
logging.info(f"{'='*80}")

# ============================================================================
# 4. Convenient query functions
# ============================================================================

def get_evaluator(evaluator_name: str):
    """
    Get evaluator class (convenient function)
    
    Args:
        evaluator_name: evaluatorname
    
    Returns:
        Evaluator class or None
    
    Example:
        from scendroid.apps import get_evaluator
        
        evaluator_class = get_evaluator("LayeredClockSetAlarm")
        if evaluator_class:
            evaluator = evaluator_class(params)
    """
    return AppRegistry.get_evaluator(evaluator_name)


def get_setup_function(app_name: str, function_name: str):
    """
    Get initialize function (convenient function)
    
    Args:
        app_name: App name
        function_name: functionname
    
    Returns:
        initializefunctionor None
    
    Example:
        from scendroid.apps import get_setup_function
        
        setup_func = get_setup_function("clock", "setup_alarm")
        if setup_func:
            setup_func(env, hour=8, minute=0)
    """
    return AppRegistry.get_setup_function(app_name, function_name)


def list_all_evaluators():
    """
    List all registered evaluators
    
    Returns:
        evaluatornamelist
    """
    return AppRegistry.list_registered_evaluators()


def list_all_setup_functions():
    """
    List all registered initialize functions
    
    Returns:
        initializefunctionnamelist
    """
    return AppRegistry.list_registered_setups()


def print_app_registry():
    """
    Print registry information (for debugging)
    """
    AppRegistry.print_registry()


# Export convenient functions
__all__.extend([
    'get_evaluator',
    'get_setup_function',
    'list_all_evaluators',
    'list_all_setup_functions',
    'print_app_registry',
])

# ============================================================================
# 5. Module-level variables (for external queries)
# ============================================================================

# These variables can be used to query the load status
loaded_modules = _loaded_modules
failed_modules = _failed_modules
registry_stats = {
    'total_evaluators': _total_evaluators,
    'total_setup_functions': _total_setup_functions,
    'loaded_modules': len(_loaded_modules),
    'failed_modules': len(_failed_modules),
}

