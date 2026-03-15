"""Chrome DevTools Protocol (CDP) integration for ScenDroid.

This module enables Playwright to connect to Chrome running in the Android emulator
via CDP, allowing full browser automation capabilities including:
- Reading current URL and page content
- Finding and interacting with elements
- Executing JavaScript
- Automatic login and task evaluation

Usage:
    from scendroid.task_evals.webarena import chrome_cdp
    
    # Initialize CDP connection
    cdp_manager = chrome_cdp.ChromeCDPManager(env)
    
    # Connect to Chrome
    page = await cdp_manager.connect()
    
    # Use Playwright API
    url = page.url
    content = await page.content()
    await page.fill('input[name="email"]', 'test@example.com')
    
    # Cleanup
    await cdp_manager.disconnect()
"""

import asyncio
import re
import subprocess
import time
from typing import Optional
from absl import logging

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Run: pip install playwright && playwright install chromium")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logging.debug("aiohttp not installed, will use urllib for HTTP requests")

from scendroid.env import interface


class ChromeCDPManager:
    """Manages Chrome DevTools Protocol connection to Android Chrome.
    
    This class handles:
    1. Enabling remote debugging in Android Chrome
    2. Port forwarding via adb
    3. Connecting Playwright to Chrome via CDP
    4. Managing the connection lifecycle
    """
    
    def __init__(self, env: interface.AsyncEnv, cdp_port: int = 9222):
        """Initialize CDP manager.
        
        Args:
            env: ScenDroid environment
            cdp_port: Local port to use for CDP connection (default: 9222)
        """
        self.env = env
        self.cdp_port = cdp_port
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._port_forwarded = False
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required for CDP connection. "
                "Install with: pip install playwright && playwright install chromium"
            )
    
    async def connect(self, force_restart: bool = False) -> Page:
        """Connect to Chrome via CDP and return a Playwright Page object.
        
        Args:
            force_restart: If True, force restart Chrome. If False, try to connect
                          to existing Chrome first (default: False)
        
        Returns:
            Playwright Page object for browser automation
            
        Raises:
            RuntimeError: If connection fails
        """
        try:
            # Step 1: Setup port forwarding first (doesn't affect Chrome)
            logging.info(f"Forwarding Chrome debugging port to localhost:{self.cdp_port}...")
            self._setup_port_forwarding()
            
            # Step 2: Try to connect to existing Chrome
            if not force_restart:
                logging.info("🔗 Trying to connect to existing Chrome (without restart)...")
                print(f"🔍 [DEBUG CDP] force_restart={force_restart}, attempting to connect to existing Chrome", flush=True)
                try:
                    # Use the corrected WebSocket URL to connect
                    ws_url = await self._get_corrected_ws_url()
                    if ws_url:
                        self.playwright = await async_playwright().start()
                        self.browser = await self.playwright.chromium.connect_over_cdp(
                            ws_url,
                            timeout=5000  # 5 seconds timeout
                        )
                        
                        # Get existing page
                        contexts = self.browser.contexts
                        if contexts:
                            self.context = contexts[0]
                            pages = self.context.pages
                            if pages:
                                self.page = pages[0]
                                logging.info(f"✅ Connected to existing Chrome. Current URL: {self.page.url}")
                                print(f"✅ [DEBUG CDP] Successfully connected to existing Chrome: {self.page.url}", flush=True)
                                return self.page
                        
                        logging.info("Connected but no active pages, will restart Chrome...")
                        print(f"⚠️ [DEBUG CDP] Connection succeeded but no active page found; will restart Chrome", flush=True)
                        await self.disconnect()
                    else:
                        logging.info("Could not get WebSocket URL, will restart Chrome...")
                        print(f"⚠️ [DEBUG CDP] Failed to get WebSocket URL; will restart Chrome", flush=True)
                    
                except Exception as e:
                    logging.info(f"Cannot connect to existing Chrome ({e}), will restart...")
                    print(f"❌ [DEBUG CDP] Failed to connect to existing Chrome: {e}; will restart", flush=True)
                    await self.disconnect()
            else:
                print(f"🔄 [DEBUG CDP] force_restart={force_restart}, forcing Chrome restart", flush=True)
            
            # Step 3: If connection failed or force_restart, launch Chrome
            logging.info("🔄 Launching Chrome with remote debugging...")
            print(f"🚀 [DEBUG CDP] Launching Chrome...", flush=True)
            
            # Get correct shopping URL dynamically
            from . import port_utils
            shopping_url = port_utils.get_shopping_base_url(self.env)
            logging.info(f"   📍 Will launch Chrome with URL: {shopping_url}")
            print(f"   📍 [DEBUG CDP] Launching with URL: {shopping_url}", flush=True)
            
            self._launch_chrome_with_debugging(start_url=shopping_url)
            
            # Wait for Chrome to fully start and create debug socket
            # Chrome requires some time to create the debug socket
            time.sleep(5)
            
            # Step 4: Re-setup port forwarding after Chrome restart
            # After Chrome restarts, port forwarding must be reconfigured
            logging.info("🔄 Re-setting up port forwarding after Chrome restart...")
            self._port_forwarded = False  # reset flag
            self._setup_port_forwarding()
            
            # Additional wait after port forwarding
            time.sleep(2)
            
            # Verify port is accepting connections before attempting CDP
            import socket
            max_retries = 3
            for retry in range(max_retries):
                try:
                    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_sock.settimeout(3)
                    test_sock.connect(('localhost', self.cdp_port))
                    test_sock.close()
                    logging.info(f"✅ Port {self.cdp_port} is accepting connections")
                    break
                except Exception as e:
                    logging.warning(f"   Port check attempt {retry+1}/{max_retries} failed: {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
                    else:
                        logging.warning("   ⚠️ Port may not be ready, will try CDP connection anyway")
            
            # Step 5: Connect Playwright to Chrome using corrected WebSocket URL
            logging.info("Connecting Playwright to Chrome via CDP...")
            
            # Get the corrected WebSocket URL (to resolve Android Chrome returning an incorrect port)
            ws_url = await self._get_corrected_ws_url()
            if not ws_url:
                raise RuntimeError("Could not get WebSocket URL from Chrome")
            
            logging.info(f"Using WebSocket URL: {ws_url}")
            
            self.playwright = await async_playwright().start()
            
            # Use the corrected WebSocket URL to connect
            self.browser = await self.playwright.chromium.connect_over_cdp(ws_url)
            
            # Get or create a page
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                pages = self.context.pages
                if pages:
                    self.page = pages[0]
                else:
                    self.page = await self.context.new_page()
            else:
                # Create new context and page
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
            
            logging.info(f"✅ Connected to Chrome. Current URL: {self.page.url}")
            return self.page
            
        except Exception as e:
            logging.error(f"Failed to connect to Chrome via CDP: {e}")
            await self.disconnect()
            raise RuntimeError(f"CDP connection failed: {e}")
    
    async def _get_corrected_ws_url(self) -> str:
        """Get the corrected WebSocket URL. 
        
        When Android Chrome debugs via Unix socket, the returned webSocketDebuggerUrl may contain
        an incorrect port (e.g., 8123); we need to replace it with our port-forwarding port (9222). 
        
        Returns:
            The corrected WebSocket URL, or None if retrieval fails
        """
        try:
            if AIOHTTP_AVAILABLE:
                return await self._get_ws_url_aiohttp()
            else:
                return await self._get_ws_url_urllib()
        except Exception as e:
            logging.warning(f"[CDP] Failed to get WebSocket URL: {e}")
            return None
    
    async def _get_ws_url_aiohttp(self) -> str:
        """Use aiohttp to get the WebSocket URL"""
        async with aiohttp.ClientSession() as session:
            # First, attempt /json/version
            try:
                async with session.get(
                    f"http://localhost:{self.cdp_port}/json/version",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ws_url = data.get('webSocketDebuggerUrl', '')
                        if ws_url:
                            corrected_url = self._fix_ws_url_port(ws_url)
                            logging.info(f"[CDP] Original WS URL: {ws_url}")
                            logging.info(f"[CDP] Corrected WS URL: {corrected_url}")
                            return corrected_url
            except Exception as e:
                logging.debug(f"[CDP] /json/version failed: {e}")
            
            # If /json/version fails, attempt /json to get the page list
            try:
                async with session.get(
                    f"http://localhost:{self.cdp_port}/json",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        pages = await response.json()
                        if pages and len(pages) > 0:
                            ws_url = pages[0].get('webSocketDebuggerUrl', '')
                            if ws_url:
                                corrected_url = self._fix_ws_url_port(ws_url)
                                logging.info(f"[CDP] Original page WS URL: {ws_url}")
                                logging.info(f"[CDP] Corrected page WS URL: {corrected_url}")
                                return corrected_url
            except Exception as e:
                logging.debug(f"[CDP] /json failed: {e}")
        
        return None
    
    async def _get_ws_url_urllib(self) -> str:
        """Use urllib to get the WebSocket URL (fallback solution when aiohttp is unavailable)"""
        import urllib.request
        import json
        
        def fetch_json(url):
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    return json.loads(response.read().decode())
            except Exception as e:
                logging.debug(f"[CDP] urllib fetch failed for {url}: {e}")
                return None
        
        # Execute synchronous requests in a thread pool
        loop = asyncio.get_running_loop()
        
        # First, attempt /json/version
        data = await loop.run_in_executor(
            None, 
            fetch_json, 
            f"http://localhost:{self.cdp_port}/json/version"
        )
        if data:
            ws_url = data.get('webSocketDebuggerUrl', '')
            if ws_url:
                corrected_url = self._fix_ws_url_port(ws_url)
                logging.info(f"[CDP] Original WS URL: {ws_url}")
                logging.info(f"[CDP] Corrected WS URL: {corrected_url}")
                return corrected_url
        
        # attempt /json
        pages = await loop.run_in_executor(
            None, 
            fetch_json, 
            f"http://localhost:{self.cdp_port}/json"
        )
        if pages and len(pages) > 0:
            ws_url = pages[0].get('webSocketDebuggerUrl', '')
            if ws_url:
                corrected_url = self._fix_ws_url_port(ws_url)
                logging.info(f"[CDP] Original page WS URL: {ws_url}")
                logging.info(f"[CDP] Corrected page WS URL: {corrected_url}")
                return corrected_url
        
        return None
    
    def _fix_ws_url_port(self, ws_url: str) -> str:
        """Correct the port in the WebSocket URL. 
        
        The WebSocket URL returned by Android Chrome may contain an internal port (e.g., ws://127.0.0.1:8123/...), 
        which we need to replace with our port-forwarding port. 
        
        Args:
            ws_url: Original WebSocket URL
            
        Returns:
            Corrected WebSocket URL
        """
        # Match ws://host:port/path format
        # Replace the port with our cdp_port
        pattern = r'ws://[^:]+:\d+'
        replacement = f'ws://localhost:{self.cdp_port}'
        
        corrected = re.sub(pattern, replacement, ws_url)
        return corrected
    
    def _get_device_name(self) -> str:
        """Get Android device name.
        
        Returns:
            Device name (e.g., 'emulator-5554')
        """
        # Method 1: Try to get console_port from controller config (most reliable)
        try:
            # Access via: AsyncAndroidEnv -> ScenDroidController -> wrapped env -> config
            console_port = self.env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
            device_name = f"emulator-{console_port}"
            logging.info(f"[CDP] Got device from controller config: {device_name}")
            return device_name
        except Exception as e:
            logging.debug(f"[CDP] Could not get console_port from config: {e}")
        
        # Method 2: Try to get from controller attributes
        if hasattr(self.env, 'controller'):
            if hasattr(self.env.controller, '_device_name'):
                return self.env.controller._device_name
            if hasattr(self.env.controller, 'device_name'):
                return self.env.controller.device_name
        
        # Method 3: Fallback - get first device from adb devices (less reliable in multi-device scenarios)
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if '\t' in line:
                    device = line.split('\t')[0]
                    if device.startswith('emulator') or device.startswith('device'):
                        logging.warning(f"[CDP] Using first device from adb devices: {device} (may be incorrect in multi-device setup)")
                        return device
        except Exception as e:
            logging.debug(f"[CDP] Could not get device from adb devices: {e}")
        
        # Final fallback: use default
        logging.warning("[CDP] Using default device emulator-5554 (may be incorrect)")
        return "emulator-5554"
    
    def _launch_chrome_with_debugging(self, start_url: str = None):
        """Launch Chrome with remote debugging enabled.
        
        Args:
            start_url: URL to open in Chrome. If not provided, uses default shopping URL.
        
        Chrome on Android creates a Unix socket for debugging.
        """
        device_name = self._get_device_name()
        
        # Force stop Chrome first to clean state
        logging.info("Stopping Chrome...")
        subprocess.run([
            "adb", "-s", device_name,
            "shell", "am", "force-stop", "com.android.chrome"
        ], check=False, capture_output=True)
        
        time.sleep(2)
        
        # Remove old debug socket if exists
        subprocess.run([
            "adb", "-s", device_name,
            "shell", "rm", "-f", "/data/local/tmp/chrome_devtools_remote"
        ], check=False, capture_output=True)
        
        # ✅ Use am start to directly launch Chrome and pass in the correct URL
        # No longer rely on the home-screen shortcut (the shortcut may be configured with an outdated URL)
        if not start_url:
            # Fallback: get shopping URL from env
            from . import port_utils
            start_url = port_utils.get_shopping_base_url(self.env)
        
        logging.info(f"Launching Chrome with URL: {start_url}")
        print(f"   🌐 [DEBUG CDP] Launch URL: {start_url}", flush=True)
        
        result = subprocess.run([
            "adb", "-s", device_name,
            "shell", "am", "start",
            "-n", "com.android.chrome/com.google.android.apps.chrome.Main",
            "-a", "android.intent.action.VIEW",
            "-d", start_url
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"Failed to start Chrome: {result.stderr}")
            raise RuntimeError(f"Chrome launch failed: {result.stderr}")
        
        logging.info("Waiting for Chrome to start...")
        
        # Wait for Chrome to fully start (important after clearing data)
        max_wait = 15  # Maximum 15 seconds
        for i in range(max_wait):
            time.sleep(1)
            
            # Check if Chrome process is running using ps -A (not shell=True)
            ps_result = subprocess.run([
                "adb", "-s", device_name,
                "shell", "ps", "-A"
            ], capture_output=True, text=True)
            
            if "com.android.chrome" in ps_result.stdout:
                logging.info(f"✅ Chrome is running (waited {i+1}s)")
                # Give it more time to create debug socket
                # Chrome requires additional time to create the chrome_devtools_remote socket
                logging.info("   Waiting for debug socket to be created...")
                time.sleep(5)
                return
        
        logging.warning("⚠️ Chrome may not be running after 15s wait")
    
    def _setup_port_forwarding(self):
        """Setup adb port forwarding for Chrome debugging.
        
        Chrome on Android uses Unix domain sockets for debugging.
        We need to forward these to a local TCP port.
        """
        if self._port_forwarded:
            return
        
        device_name = self._get_device_name()
        
        # First, clear all existing forwards to start fresh
        subprocess.run([
            "adb", "-s", device_name,
            "forward", "--remove-all"
        ], check=False, capture_output=True)
        
        time.sleep(0.5)
        
        # Try different socket names that Chrome might use
        chrome_pid = self._get_chrome_pid()
        socket_names = [
            "chrome_devtools_remote",
            "chrome_devtools_remote_0"
        ]
        # Only attempt WebView socket if PID is retrieved
        if chrome_pid:
            socket_names.insert(1, f"webview_devtools_remote_{chrome_pid}")
        
        success = False
        for socket_name in socket_names:
            logging.info(f"Trying socket: {socket_name}")
            
            result = subprocess.run([
                "adb", "-s", device_name,
                "forward", f"tcp:{self.cdp_port}",
                f"localabstract:{socket_name}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info(f"✅ Port forwarding established: localhost:{self.cdp_port} -> {socket_name}")
                
                # Verify the forward is working by checking if we can connect
                import socket
                time.sleep(1)
                try:
                    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_sock.settimeout(2)
                    test_sock.connect(('localhost', self.cdp_port))
                    test_sock.close()
                    logging.info(f"✅ Port {self.cdp_port} is accepting connections")
                    success = True
                    break
                except Exception as e:
                    logging.warning(f"Port forward created but cannot connect: {e}")
                    continue
        
        if not success:
            raise RuntimeError(
                f"Failed to establish port forwarding. "
                f"Make sure Chrome is running and debugging is enabled."
            )
        
        self._port_forwarded = True
    
    def _get_chrome_pid(self) -> str:
        """Get Chrome process ID.
        
        Returns:
            Chrome PID as string, or empty string if not found
        """
        device_name = self._get_device_name()
        
        # Do not use check=True because Chrome may not have started yet
        result = subprocess.run([
            "adb", "-s", device_name,
            "shell", "pidof", "com.android.chrome"
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        # Attempt using the ps command as a fallback
        try:
            ps_result = subprocess.run([
                "adb", "-s", device_name,
                "shell", "ps", "-A"
            ], capture_output=True, text=True, check=False)
            
            for line in ps_result.stdout.split('\n'):
                if 'com.android.chrome' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]  # PID is usually the second column
        except Exception:
            pass
        
        return ""
    
    async def disconnect(self):
        """Disconnect from Chrome and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            # Remove port forwarding
            if self._port_forwarded:
                device_name = self._get_device_name()
                subprocess.run([
                    "adb", "-s", device_name,
                    "forward", "--remove", f"tcp:{self.cdp_port}"
                ], check=False)
                self._port_forwarded = False
            
            logging.info("CDP connection closed")
            
        except Exception as e:
            logging.warning(f"Error during CDP cleanup: {e}")
    
    async def __aenter__(self):
        """Context manager entry."""
        return await self.connect()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()


# Synchronous wrapper for easier integration
class SyncChromeCDPManager:
    """Synchronous wrapper around ChromeCDPManager.
    
    This provides a synchronous interface for use in non-async code.
    """
    
    def __init__(self, env: interface.AsyncEnv, cdp_port: int = 9222):
        self.manager = ChromeCDPManager(env, cdp_port)
        self.loop = None
        self.page = None
    
    def connect(self) -> Page:
        """Connect to Chrome synchronously.
        
        Returns:
            Playwright Page object
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.page = self.loop.run_until_complete(self.manager.connect())
        return self.page
    
    def disconnect(self):
        """Disconnect synchronously."""
        if self.loop and self.manager:
            self.loop.run_until_complete(self.manager.disconnect())
            self.loop.close()
            self.loop = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


# Helper functions

async def get_chrome_page(env: interface.AsyncEnv) -> Page:
    """Quick helper to get a Chrome Page object.
    
    Args:
        env: ScenDroid environment
        
    Returns:
        Playwright Page object connected to Android Chrome
        
    Example:
        page = await get_chrome_page(env)
        url = page.url
        await page.goto("http://example.com")
    """
    manager = ChromeCDPManager(env)
    return await manager.connect()


def get_chrome_page_sync(env: interface.AsyncEnv) -> Page:
    """Synchronous version of get_chrome_page.
    
    Args:
        env: ScenDroid environment
        
    Returns:
        Playwright Page object connected to Android Chrome
    """
    manager = SyncChromeCDPManager(env)
    return manager.connect()

