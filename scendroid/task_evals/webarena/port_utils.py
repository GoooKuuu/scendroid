"""Port mapping utilities for multi-emulator shopping environment.

This module provides utilities to calculate shopping ports dynamically based on
emulator console ports, enabling multiple emulators to use different shopping
containers on different ports.

Port mapping rule:
    emulator_port (console) -> shopping_port (host)
    5554 -> 7770
    5556 -> 7772
    5558 -> 7774
    Formula: shopping_port = 7770 + (emulator_port - 5554)
"""

import logging
import os
from typing import Optional

from scendroid.env import interface


def get_console_port_from_env(env: Optional[interface.AsyncEnv]) -> Optional[int]:
    """Extract emulator console port from ScenDroid environment.
    
    Args:
        env: ScenDroid AsyncEnv instance
        
    Returns:
        Console port number (e.g., 5554, 5556, 5560) or None if not found
    """
    if env is None:
        return None
    
    try:
        # Method 1: Try accessing via controller._env (most common path)
        # env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
        if hasattr(env, 'controller'):
            controller = env.controller
            if hasattr(controller, '_env'):
                wrapped_env = controller._env
                if hasattr(wrapped_env, '_coordinator'):
                    coordinator = wrapped_env._coordinator
                    if hasattr(coordinator, '_simulator'):
                        simulator = coordinator._simulator
                        if hasattr(simulator, '_config'):
                            config = simulator._config
                            if hasattr(config, 'emulator_launcher'):
                                emulator_launcher = config.emulator_launcher
                                if hasattr(emulator_launcher, 'emulator_console_port'):
                                    port = emulator_launcher.emulator_console_port
                                    logging.info(f"✅ Extracted console port from env.controller._env: {port}")
                                    return port
        
        # Method 2: Try accessing via env.env (alternative path)
        if hasattr(env, 'env'):
            actual_env = env.env
        else:
            actual_env = env
        
        # Navigate through the nested structure
        if hasattr(actual_env, '_coordinator'):
            coordinator = actual_env._coordinator
            if hasattr(coordinator, '_simulator'):
                simulator = coordinator._simulator
                if hasattr(simulator, '_config'):
                    config = simulator._config
                    if hasattr(config, 'emulator_launcher'):
                        emulator_launcher = config.emulator_launcher
                        if hasattr(emulator_launcher, 'emulator_console_port'):
                            port = emulator_launcher.emulator_console_port
                            logging.info(f"✅ Extracted console port from env.env: {port}")
                            return port
        
        logging.warning("⚠️  Could not extract console port from env (nested attributes not found)")
        return None
        
    except Exception as e:
        logging.warning(f"⚠️  Error extracting console port from env: {e}")
        return None


def calculate_shopping_port(console_port: int) -> int:
    """Calculate shopping host port from emulator console port.
    
    Args:
        console_port: Emulator console port (e.g., 5554, 5556, 5558)
        
    Returns:
        Shopping host port (e.g., 7770, 7772, 7774)
        
    Formula:
        shopping_port = 7770 + (console_port - 5554)
    """
    return 7770 + (console_port - 5554)


def get_shopping_base_url(
    env: Optional[interface.AsyncEnv] = None,
    console_port: Optional[int] = None,
    host_ip: Optional[str] = None
) -> str:
    """Get shopping base URL dynamically based on emulator port.
    
    Priority (highest to lowest):
    1. Explicit console_port parameter (if provided)
    2. Extract from env object (if provided) - HIGHEST PRIORITY for dynamic scenarios
    3. Environment variable SHOPPING (if set) - fallback for static setups
    4. Default: http://localhost:7770
    
    Args:
        env: ScenDroid AsyncEnv instance (optional)
        console_port: Emulator console port (optional, e.g., 5554, 5560)
        host_ip: Host IP address (optional, defaults to auto-detect or localhost)
        
    Returns:
        Shopping base URL (e.g., "http://localhost:7770", "http://localhost:7776")
    """
    # Helper function: Automatically get the host IP
    def _auto_get_host_ip() -> str:
        """Automatically get the host IP"""
        import subprocess
        import socket
        from urllib.parse import urlparse
        
        # Method 1: Parse from environment variable SHOPPING
        shopping_url = os.environ.get('SHOPPING', '')
        if shopping_url:
            try:
                parsed = urlparse(shopping_url)
                if parsed.hostname:
                    print(f"📍 [Method 1] Get host IP from environment variable SHOPPING: {parsed.hostname}")
                    return parsed.hostname
            except Exception as e:
                print(f"⚠️  [Method 1] Failed to parse from environment variable: {e}")
        else:
            print(f"⚠️  [Method 1] Environment variable SHOPPING is not set up")
        
        # Method 2: Use hostname -I
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                ip = result.stdout.strip().split()[0]
                print(f"📍 [Method 2] Get host IP using hostname -I: {ip}")
                return ip
            else:
                print(f"⚠️  [Method 2] hostname -I failed: returncode={result.returncode}, stdout='{result.stdout}'")
        except Exception as e:
            print(f"⚠️  [Method 2] hostname -I exception: {e}")
        
        # method3: socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            print(f"📍 [Method 3] Get host IP using socket: {ip}")
            return ip
        except Exception as e:
            print(f"⚠️  [Method 3] socket methodfailed: {e}")
        
        # Final default value
        print(f"❌ All methods failed; using default value localhost")
        print(f"💡 Suggestion: First run './restart_shopping_docker.sh -e 5554' in the same shell")
        return "localhost"
    
    # Priority 1: Explicit console_port parameter (highest - allows override)
    if console_port is not None:
        shopping_port = calculate_shopping_port(console_port)
        host = host_ip or _auto_get_host_ip()
        url = f"http://{host}:{shopping_port}"
        logging.info(f"📍 Using shopping URL from console_port parameter {console_port}: {url}")
        return url
    
    # Priority 2: Extract from env object (dynamic scenarios)
    if env is not None:
        extracted_port = get_console_port_from_env(env)
        if extracted_port is not None:
            shopping_port = calculate_shopping_port(extracted_port)
            host = host_ip or _auto_get_host_ip()
            url = f"http://{host}:{shopping_port}"
            logging.info(f"📍 Using shopping URL from env (extracted port {extracted_port}): {url}")
            return url
    
    # Priority 3: Environment variable (backward compatibility / static setups)
    env_url = os.environ.get('SHOPPING')
    if env_url:
        logging.info(f"📍 Using SHOPPING from env var: {env_url}")
        return env_url
    
    # Priority 4: Default (backward compatibility)
    host = _auto_get_host_ip()
    default_url = f"http://{host}:7770"
    logging.info(f"📍 Using default shopping URL with auto-detected host: {default_url}")
    return default_url


def get_shopping_admin_url(
    env: Optional[interface.AsyncEnv] = None,
    console_port: Optional[int] = None,
    host_ip: Optional[str] = None
) -> str:
    """Get shopping admin URL dynamically based on emulator port.
    
    Admin port is shopping_port + 10.
    
    Priority matches get_shopping_base_url():
    1. Explicit console_port parameter
    2. Extract from env object
    3. Environment variable SHOPPING_ADMIN
    4. Default
    
    Args:
        env: ScenDroid AsyncEnv instance (optional)
        console_port: Emulator console port (optional)
        host_ip: Host IP address (optional)
        
    Returns:
        Shopping admin URL (e.g., "http://localhost:7780/admin")
    """
    # Get base URL (this respects the priority: console_port > env > env_var > default)
    base_url = get_shopping_base_url(env, console_port, host_ip)
    
    # Parse and modify port if needed (admin is typically base_port + 10)
    # For now, just append /admin since the container typically serves both
    return f"{base_url}/admin"


# Backward compatibility aliases
def get_shopping_login_url(
    env: Optional[interface.AsyncEnv] = None,
    console_port: Optional[int] = None
) -> str:
    """Get shopping login URL (for backward compatibility).
    
    Args:
        env: ScenDroid AsyncEnv instance (optional)
        console_port: Emulator console port (optional)
        
    Returns:
        Shopping login URL (e.g., "http://localhost:7770/customer/account/login/")
    """
    base_url = get_shopping_base_url(env, console_port)
    return f"{base_url}/customer/account/login/"


# Module-level functions for convenience
def resolve_shopping_url(url_spec: str, env: Optional[interface.AsyncEnv] = None) -> str:
    """Resolve URL specification, replacing __SHOPPING__ placeholder.
    
    Args:
        url_spec: URL or URL with __SHOPPING__ placeholder
        env: ScenDroid AsyncEnv instance (optional)
        
    Returns:
        Resolved URL string
    """
    if not url_spec:
        return url_spec
    
    base_url = get_shopping_base_url(env)
    return url_spec.replace('__SHOPPING__', base_url)
