"""
Shopping App Utility Functions

Provides helper functions related to the Shopping application.  

Shopping tasks primarily use the WebArena framework and the Chrome browser,  
Therefore, most functionality is provided by the scendroid.task_evals.webarena module.  
"""

from absl import logging


def get_webarena_evaluator(task_type: str, params: dict):
    """
    Create a WebArena evaluator based on the task type.  
    
    Args:
        task_type: tasktype ("program_html" or "string_match")
        params: taskparameter
        
    Returns:
        WebArena evaluatorinstance
    """
    from scendroid.task_evals.webarena import webarena_task
    
    if task_type == "program_html":
        return webarena_task.ProgramHTMLWebArenaTask(params)
    elif task_type == "string_match":
        return webarena_task.StringMatchWebArenaTask(params)
    elif task_type == "url_match":
        return webarena_task.URLMatchWebArenaTask(params)
    else:
        raise ValueError(f"Unknown WebArena task type: {task_type}")


def rebuild_shopping_container():
    """
    rebuild Shopping container
    
    Some tasks modify the status of the Shopping website (e.g., placing an order),  
    requiring the container to be rebuilt to restore the initial status.  
    
    Returns:
        bool: Whether the container was successfully rebuilt.  
    """
    try:
        from scendroid.task_evals.webarena import container_manager
        
        logging.info("🔄 Rebuilding Shopping container...")
        manager = container_manager.ShoppingContainerManager()
        success = manager.rebuild_container()
        
        if success:
            logging.info("✅ Shopping container rebuilt successfully")
        else:
            logging.error("❌ Failed to rebuild Shopping container")
        
        return success
    except Exception as e:
        logging.error(f"❌ Error rebuilding container: {e}")
        return False


def should_rebuild_container(check_method: str = None, eval_types: list = None) -> bool:
    """
    Determine whether the Shopping container needs to be rebuilt.  
    
    Args:
        check_method: checkmethod ("order", "cart" etc.)
        eval_types: evaluationtypelist
        
    Returns:
        bool: Whether rebuilding is required.  
    """
    # If check_method is "order", an order has been placed, so rebuilding is required.  
    if check_method == "order":
        return True
    
    # If it is a read-only operation (e.g., string_match), rebuilding is not required.  
    if eval_types and "string_match" in eval_types and len(eval_types) == 1:
        return False
    
    # Default case: If program_html is involved, rebuilding may be required.
    return False

