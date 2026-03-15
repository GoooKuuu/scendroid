"""
App Registry - Automatically register and manage all apps' initialize functions and evaluators

This registry uses a decorator-based approach, allowing individual app modules to automatically register their functionalities:
1. Evaluator Classes - Used to evaluate whether a task has been successfully completed
2. Initialize Functions - Used to set up the task environment

usage:
    # Register evaluator
    @AppRegistry.register_evaluator("LayeredClockSetAlarm")
    class ClockSetAlarmEvaluator(BaseAppEvaluator):
        pass
    
    # Register initialize function
    @AppRegistry.register_setup("clock", "setup_alarm")
    def setup_alarm(env, hour, minute):
        pass
"""

from absl import logging
from typing import Dict, Callable, Type, Any, Optional


class AppRegistry:
    """
    Global registry managing all apps' initialize functions and evaluators
    
    Uses class variables to store all registered functionalities, ensuring global uniqueness.
    """
    
    # Store all registered evaluator classes: {evaluator_name: EvaluatorClass}
    _evaluators: Dict[str, Type] = {}
    
    # Store all registered initialize functions: {app.function: callable}
    _setup_functions: Dict[str, Callable] = {}
    
    # ========== Registration Decorators ==========
    
    @classmethod
    def register_evaluator(cls, evaluator_name: str):
        """
        Decorator for registering evaluator classes
        
        Args:
            evaluator_name: evaluator name (corresponding to androidworld_reference in JSON)
        
        Returns:
            Decorator function
        
        Usage:
            @AppRegistry.register_evaluator("LayeredClockSetAlarm")
            class ClockSetAlarmEvaluator(BaseAppEvaluator):
                def evaluate(self, env):
                    return 1.0
        """
        def decorator(evaluator_class: Type):
            if evaluator_name in cls._evaluators:
                logging.warning(
                    f"⚠️  Evaluator '{evaluator_name}' already registered, overwriting"
                )
            
            cls._evaluators[evaluator_name] = evaluator_class
            logging.debug(f"📝 Registered evaluator: {evaluator_name}")
            return evaluator_class
        
        return decorator
    
    @classmethod
    def register_setup(cls, app_name: str, function_name: str):
        """
        Decorator for registering initialize functions
        
        Args:
            app_name: App name (e.g., "clock")
            function_name: Function name (e.g., "setup_alarm")
        
        Returns:
            Decorator function
        
        Usage:
            @AppRegistry.register_setup("clock", "setup_alarm")
            def setup_alarm(env, hour, minute):
                pass
        """
        def decorator(func: Callable):
            key = f"{app_name}.{function_name}"
            
            if key in cls._setup_functions:
                logging.warning(
                    f"⚠️  Setup function '{key}' already registered, overwriting"
                )
            
            cls._setup_functions[key] = func
            logging.debug(f"📝 Registered setup: {key}")
            return func
        
        return decorator
    
    # ========== Query Methods ==========
    
    @classmethod
    def get_evaluator(cls, evaluator_name: str) -> Optional[Type]:
        """
        Get evaluator class
        
        Args:
            evaluator_name: evaluator name (e.g., "LayeredClockSetAlarm")
        
        Returns:
            Evaluator class, or None if not found
        
        Example:
            evaluator_class = AppRegistry.get_evaluator("LayeredClockSetAlarm")
            if evaluator_class:
                evaluator = evaluator_class(params)
                score = evaluator.is_successful(env)
        """
        evaluator_class = cls._evaluators.get(evaluator_name)
        
        if evaluator_class is None:
            logging.debug(
                f"⚠️  Evaluator '{evaluator_name}' not found in registry"
            )
            logging.debug(f"Available evaluators: {cls.list_registered_evaluators()}")
        
        return evaluator_class
    
    @classmethod
    def get_setup_function(cls, app_name: str, function_name: str) -> Optional[Callable]:
        """
        getinitializefunction
        
        Args:
            app_name: App name (e.g., "clock")
            function_name: Function name (e.g., "setup_alarm")
        
        Returns:
            Initialize function, or None if not found
        
        Example:
            setup_func = AppRegistry.get_setup_function("clock", "setup_alarm")
            if setup_func:
                setup_func(env, hour=8, minute=0)
        """
        key = f"{app_name}.{function_name}"
        func = cls._setup_functions.get(key)
        
        if func is None:
            logging.debug(
                f"⚠️  Setup function '{key}' not found in registry"
            )
            logging.debug(f"Available functions: {cls.list_registered_setups()}")
        
        return func
    
    # ========== Debug and Query Methods ==========
    
    @classmethod
    def list_registered_evaluators(cls) -> list:
        """
        List all registered evaluators
        
        Returns:
            List of evaluator names (in alphabetical order)
        """
        return sorted(cls._evaluators.keys())
    
    @classmethod
    def list_registered_setups(cls) -> list:
        """
        List all registered initialize functions
        
        Returns:
            List of initialize function names (in alphabetical order, format: app.function)
        """
        return sorted(cls._setup_functions.keys())
    
    @classmethod
    def get_stats(cls) -> dict:
        """
        Get registry statistics
        
        Returns:
            statisticsdictionary
        """
        return {
            'total_evaluators': len(cls._evaluators),
            'total_setup_functions': len(cls._setup_functions),
            'evaluators': cls.list_registered_evaluators(),
            'setup_functions': cls.list_registered_setups(),
        }
    
    @classmethod
    def print_registry(cls):
        """
        Print registry information (for debugging)
        
        Display all registered evaluators and initialize functions.
        """
        print("\n" + "="*80)
        print("📋 App Registry Status")
        print("="*80)
        
        print(f"\n✅ Registered Evaluators ({len(cls._evaluators)}):")
        if cls._evaluators:
            for name in sorted(cls._evaluators.keys()):
                evaluator_class = cls._evaluators[name]
                print(f"   - {name}")
                print(f"     └─ {evaluator_class.__module__}.{evaluator_class.__name__}")
        else:
            print("   (None)")
        
        print(f"\n✅ Registered Setup Functions ({len(cls._setup_functions)}):")
        if cls._setup_functions:
            for key in sorted(cls._setup_functions.keys()):
                func = cls._setup_functions[key]
                print(f"   - {key}")
                print(f"     └─ {func.__module__}.{func.__name__}")
        else:
            print("   (None)")
        
        print("="*80 + "\n")
    
    @classmethod
    def clear_registry(cls):
        """
        Clear the registry (primarily for testing)
        
        Warning: This will clear all registered evaluators and initialize functions!
        """
        cls._evaluators.clear()
        cls._setup_functions.clear()
        logging.info("🗑️  Registry cleared")

