# Copyright 2024 The ScenDroid Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""WebArena task adapter for ScenDroid.

This module adapts WebArena tasks to work within the ScenDroid framework.
WebArena tasks are web-based tasks that require browser interaction, which
we execute in Chrome on the Android emulator.
"""

import abc
import os
from typing import Any

from absl import logging
from scendroid.env import interface
from scendroid.task_evals import task_eval
from scendroid.task_evals.webarena import webarena_evaluator
from scendroid.task_evals.webarena import webarena_auth
from scendroid.task_evals.webarena import port_utils


class WebArenaTaskEval(task_eval.TaskEval):
    """Base class for WebArena tasks adapted to ScenDroid.
    
    WebArena tasks are browser-based tasks from the WebArena benchmark.
    They are executed in Chrome on the Android emulator, accessing the
    OneStopShop website (port dynamically mapped based on emulator).
    """
    
    # All WebArena tasks use Chrome browser
    app_names = ("chrome",)
    
    # WebArena tasks typically need more steps
    complexity = 3.0  # Default to 3, can be overridden
    
    # WebArena tasks should NOT start from home screen - they start in Chrome
    start_on_home_screen = False  # Override default behavior
    
    # Base URL will be set dynamically in initialize_task based on emulator port
    BASE_URL = None
    
    def __init__(self, params: dict[str, Any]):
        """Initialize WebArena task.
        
        Args:
            params: Dictionary containing:
                - task_id: WebArena task ID
                - intent: Task goal/instruction
                - start_url: Starting URL (optional)
                - eval_config: Evaluation configuration
                - require_login: Whether task requires login
        """
        super().__init__(params)
        self.task_id = params.get("task_id", -1)
        self.intent_text = params.get("intent", "")
        self.start_url = params.get("start_url", "__SHOPPING__")  # Placeholder, resolved later
        self.eval_config = params.get("eval_config", {})
        self.require_login = params.get("require_login", False)
    
    def _resolve_urls_with_env(self, env: interface.AsyncEnv):
        """Resolve all URL placeholders using the environment's emulator port.
        
        This is called during initialize_task when we have access to the env.
        """
        # Get base URL dynamically based on emulator port
        self.BASE_URL = port_utils.get_shopping_base_url(env)
        logging.info(f"Resolved shopping base URL: {self.BASE_URL}")
        
        # Replace __SHOPPING__ placeholder in start_url
        if self.start_url:
            self.start_url = self.start_url.replace("__SHOPPING__", self.BASE_URL)
        else:
            self.start_url = self.BASE_URL
        
        # Replace __SHOPPING__ in eval_config recursively
        self._replace_placeholders_in_eval_config()
    
    def _replace_placeholders_in_eval_config(self):
        """Replace __SHOPPING__ placeholders in eval_config recursively."""
        def replace_in_value(value):
            if isinstance(value, str):
                return value.replace("__SHOPPING__", self.BASE_URL)
            elif isinstance(value, dict):
                return {k: replace_in_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_in_value(item) for item in value]
            else:
                return value
        
        self.eval_config = replace_in_value(self.eval_config)
    
    def _get_shopping_mode(self) -> str:
        """Get the current shopping mode from environment or config.
        
        Returns:
            'chrome' or 'app'
        """
        # Try to import from integration_helper
        try:
            import sys
            import os
            # Add apps directory to path if needed
            apps_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'shopping_webview_app')
            if os.path.exists(apps_dir) and apps_dir not in sys.path:
                sys.path.insert(0, os.path.dirname(apps_dir))
            
            from apps.shopping_webview_app.integration_helper import get_shopping_mode
            return get_shopping_mode()
        except ImportError:
            pass
        
        # Fallback: check environment variable directly
        mode = os.environ.get("SHOPPING_MODE", "").lower()
        if mode in ("chrome", "app"):
            return mode
        
        # Check config file
        config_file = "/tmp/shopping_mode.conf"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("SHOPPING_MODE="):
                            mode = line.split("=", 1)[1].strip().lower()
                            if mode in ("chrome", "app"):
                                return mode
            except Exception:
                pass
        
        # Default to chrome
        return "chrome"
    
    def _initialize_with_app(self, env: interface.AsyncEnv) -> None:
        """Initialize task using Shopping App (WebView mode).
        
        In App mode:
        - Launch Shopping App instead of Chrome
        - Automatic login via ADB UI automation
        - Navigate to start URL
        """
        import time
        import subprocess
        
        logging.info("=" * 70)
        logging.info("📱 Initializing with Shopping App (WebView mode)")
        logging.info("=" * 70)
        
        # Get device name
        device_name = self._get_device_name(env)
        logging.info(f"Using device: {device_name}")
        
        # Package info
        PACKAGE_NAME = "com.onestopshop.app"
        MAIN_ACTIVITY = f"{PACKAGE_NAME}.MainActivity"
        
        # Check if app is installed
        result = subprocess.run(
            ["adb", "-s", device_name, "shell", "pm", "list", "packages", PACKAGE_NAME],
            capture_output=True, text=True
        )
        
        if PACKAGE_NAME not in result.stdout:
            logging.warning("⚠️ Shopping App not installed, falling back to Chrome mode")
            print("⚠️ Shopping App is not installed, falling back to Chrome mode")
            # Fallback to Chrome mode
            self._initialize_with_chrome(env)
            return
        
        # Force stop any existing instance
        subprocess.run([
            "adb", "-s", device_name,
            "shell", "am", "force-stop", PACKAGE_NAME
        ], check=False, capture_output=True)
        time.sleep(0.5)
        
        # Launch Shopping App
        logging.info(f"   🛒 Launching Shopping App...")
        
        # If login is required, first navigate to login page
        if self.require_login:
            login_url = f"{self.BASE_URL}/customer/account/login/"
            logging.info(f"   🔐 Task requires login, navigating to login page...")
            
            # Force stop existing instance to ensure clean start
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "am", "force-stop", PACKAGE_NAME
            ], check=False, capture_output=True)
            time.sleep(1)
            
            # Launch with login URL
            result = subprocess.run([
                "adb", "-s", device_name,
                "shell", "am", "start",
                "-n", f"{PACKAGE_NAME}/{MAIN_ACTIVITY}",
                "-a", "android.intent.action.VIEW",
                "-d", login_url
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.warning(f"   ⚠️ App launch may have failed: {result.stderr}")
            
            # Verify app is in foreground
            time.sleep(3)
            focus_result = subprocess.run([
                "adb", "-s", device_name,
                "shell", "dumpsys window windows | grep mCurrentFocus"
            ], capture_output=True, text=True)
            
            if "onestopshop" in focus_result.stdout.lower():
                logging.info("   ✅ Shopping App is in foreground")
            else:
                logging.warning(f"   ⚠️ Shopping App may not be in foreground")
                logging.warning(f"   Current focus: {focus_result.stdout.strip()}")
            
            # Wait for WebView to fully initialize and load the page
            logging.info("   ⏳ Waiting for WebView to initialize and load page...")
            time.sleep(10)  # Initial wait for App startup
            
            # Check if WebView debugging port is ready AND has loaded pages
            logging.info("   🔍 Checking if WebView has loaded the login page...")
            webview_ready = False
            for attempt in range(5):  # Increased to 5 attempts (up to 30 seconds)
                # Check if debugging port exists
                result = subprocess.run([
                    "adb", "-s", device_name,
                    "shell", "cat /proc/net/unix | grep webview_devtools_remote"
                ], capture_output=True, text=True)
                
                if "webview_devtools_remote" not in result.stdout:
                    logging.warning(f"   ⚠️ WebView debugging port not found (attempt {attempt + 1}/5)")
                    if attempt < 4:
                        time.sleep(6)
                    continue
                
                logging.info(f"   ✅ WebView debugging port found (attempt {attempt + 1})")
                
                # Try to check if page has loaded via CDP
                # This is a quick check to see if WebView has any pages
                import re
                match = re.search(r'@(webview_devtools_remote_\d+)', result.stdout)
                if match:
                    socket_name = match.group(1)
                    
                    # Set up temporary port forwarding to check
                    subprocess.run([
                        "adb", "-s", device_name,
                        "forward", "--remove", "tcp:9223"  # Use different port for check
                    ], check=False, capture_output=True)
                    
                    subprocess.run([
                        "adb", "-s", device_name,
                        "forward", "tcp:9223", f"localabstract:{socket_name}"
                    ], check=False, capture_output=True)
                    
                    time.sleep(1)
                    
                    # Check if pages are available
                    try:
                        import requests
                        response = requests.get("http://localhost:9223/json", timeout=3)
                        pages = response.json()
                        
                        if pages and len(pages) > 0:
                            logging.info(f"   ✅ WebView has loaded {len(pages)} page(s)")
                            webview_ready = True
                            break
                        else:
                            logging.warning(f"   ⚠️ WebView has no pages yet (attempt {attempt + 1}/5)")
                    except Exception as e:
                        logging.warning(f"   ⚠️ Cannot check WebView pages: {e}")
                    
                    # Clean up temporary forwarding
                    subprocess.run([
                        "adb", "-s", device_name,
                        "forward", "--remove", "tcp:9223"
                    ], check=False, capture_output=True)
                
                if not webview_ready and attempt < 4:
                    logging.info(f"   ⏳ Waiting 6 more seconds for page to load...")
                    time.sleep(6)
            
            if not webview_ready:
                logging.warning("   ⚠️ WebView may not have fully loaded the page, but continuing anyway...")
            
            # Attempt automatic login with retry
            login_success = False
            for login_attempt in range(2):  # Try twice
                if login_attempt > 0:
                    logging.info(f"   🔄 Retrying auto login (attempt {login_attempt + 1}/2)...")
                
                login_success = self._app_auto_login(device_name, env)
                
                if login_success:
                    break
                elif login_attempt < 1:
                    logging.warning("   ⚠️ First login attempt failed, waiting 5 seconds before retry...")
                    time.sleep(5)
            
            if login_success:
                logging.info("   ✅ Auto login successful!")
                print("✅ Automatic login succeeded! ")
                # CDP already navigated to self.start_url in _app_auto_login Step 9.
                # Do NOT use am start here: it triggers onNewIntent in the Shopping App,
                # which resets the WebView back to the hardcoded default URL (port 7770),
                # undoing the login for non-7770 ports (e.g., 7772, 7780).
            else:
                logging.warning("   ⚠️ Auto login failed after 2 attempts, agent may need to login manually")
                print("⚠️ Automatic login failed (attempted twice); the Agent may need to log in manually")
                print("   Email: emma.lopez@gmail.com")
                print("   Password: Password.123")
        else:
            # No login needed, just launch with start URL
            target_url = self.start_url or self.BASE_URL
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "am", "start",
                "-n", f"{PACKAGE_NAME}/{MAIN_ACTIVITY}",
                "-a", "android.intent.action.VIEW",
                "-d", target_url
            ], check=False, capture_output=True)
            time.sleep(5)
        
        logging.info(f"✅ Shopping App ready")
        print(f"✅ Shopping App is ready")
    
    def _app_auto_login(self, device_name: str, env) -> bool:
        """Perform automatic login in Shopping App using WebView CDP.
        
        Uses native WebSocket + CDP commands to connect to WebView and fill login form.
        WebView's CDP implementation is limited and doesn't support Playwright's full browser
        context management, so we use raw CDP commands instead.
        
        Args:
            device_name: ADB device serial
            env: ScenDroid environment
            
        Returns:
            True if login successful, False otherwise
        """
        import time
        import subprocess
        import json
        import requests
        import websocket
        
        CREDENTIALS = {
            "email": "emma.lopez@gmail.com",
            "password": "Password.123",
        }
        
        logging.info("   🔐 Attempting auto login via WebView CDP...")
        
        # Global command ID counter
        _command_id_counter = 99  # Start from 100
        
        def send_cdp_command(ws_conn, method, params=None, timeout_sec=5):
            """Send a CDP command and wait for response."""
            nonlocal _command_id_counter
            _command_id_counter += 1
            command_id = _command_id_counter
            
            command = {"id": command_id, "method": method}
            if params:
                command["params"] = params
            
            ws_conn.send(json.dumps(command))
            logging.debug(f"         → {method} (id={command_id})")
            
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout_sec:
                try:
                    msg = ws_conn.recv()
                    data = json.loads(msg)
                    
                    # Skip events
                    if "method" in data:
                        logging.debug(f"         ⏭️  {data['method']}")
                        continue
                    
                    # Check if this is our response
                    if data.get("id") == command_id:
                        if "result" in data:
                            logging.debug(f"         ✓ Success")
                            return data
                        elif "error" in data:
                            logging.warning(f"         ✗ Error: {data['error']}")
                            return None
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception as e:
                    logging.error(f"         ✗ Exception: {e}")
                    return None
            
            logging.warning(f"         ✗ Timeout")
            return None
        
        try:
            # Step 1: Find WebView debugging port
            logging.info("      Step 1: Finding WebView debugging port...")
            result = subprocess.run([
                "adb", "-s", device_name,
                "shell", "cat /proc/net/unix | grep webview_devtools_remote"
            ], capture_output=True, text=True)
            
            if "webview_devtools_remote" not in result.stdout:
                logging.warning("      WebView debugging port not found")
                return False
            
            # Extract port name
            import re
            match = re.search(r'@(webview_devtools_remote_\d+)', result.stdout)
            if not match:
                logging.warning(f"      Cannot parse WebView port: {result.stdout}")
                return False
            
            webview_socket = match.group(1)
            logging.info(f"      ✅ Found WebView port: {webview_socket}")
            
            # Step 2: Port forwarding (remove ALL existing forwards to avoid conflicts)
            logging.info("      Step 2: Setting up port forwarding...")
            
            # Check the current port forwarding list
            list_result = subprocess.run([
                "adb", "-s", device_name,
                "forward", "--list"
            ], capture_output=True, text=True)
            
            if "tcp:9222" in list_result.stdout:
                logging.info(f"      Existing forward detected on port 9222, cleaning up...")
            
            # Remove all port forwarding (more aggressive cleanup to avoid port conflicts)
            subprocess.run([
                "adb", "-s", device_name,
                "forward", "--remove-all"
            ], check=False, capture_output=True)
            time.sleep(1)
            
            # Set up new port forwarding
            result = subprocess.run([
                "adb", "-s", device_name,
                "forward", "tcp:9222", f"localabstract:{webview_socket}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.warning(f"      ⚠️  Port forwarding failed: {result.stderr}")
                if "Address already in use" in result.stderr:
                    logging.warning(f"      Port 9222 is occupied by another process")
                    logging.warning(f"      Try: adb kill-server && adb start-server")
                return False
            
            logging.info(f"      ✅ Port forwarding established: tcp:9222 -> {webview_socket}")
            time.sleep(1)
            
            # Step 3: Get WebSocket URL
            logging.info("      Step 3: Connecting to WebView via CDP...")
            response = requests.get("http://localhost:9222/json", timeout=5)
            pages = response.json()
            
            if not pages:
                logging.warning("      No pages found in WebView")
                return False
            
            ws_url = pages[0]["webSocketDebuggerUrl"]
            logging.info(f"      WebSocket: {ws_url}")
            
            # Step 4: Connect via WebSocket (suppress origin check to avoid 403 Forbidden)
            # Note: The 403 error suggests WebView requires --remote-allow-origins flag
            # We try to work around it by not sending an Origin header at all
            ws = websocket.create_connection(
                ws_url, 
                timeout=10,
                suppress_origin=True  # Don't send Origin header to avoid 403 Forbidden
            )
            ws.settimeout(5)
            
            # Enable CDP domains
            logging.info("      Step 4: Enabling CDP domains...")
            send_cdp_command(ws, "Page.enable")
            send_cdp_command(ws, "DOM.enable")
            send_cdp_command(ws, "Runtime.enable")
            
            # Get current URL
            result = send_cdp_command(ws, "Page.getNavigationHistory")
            current_url = ""
            if result and "result" in result:
                entries = result.get("result", {}).get("entries", [])
                if entries:
                    current_url = entries[-1].get("url", "")
            
            logging.info(f"      Current URL: {current_url}")
            
            # Navigate to login page if needed
            if "/customer/account/login" not in current_url:
                logging.info("      Step 5: Navigating to login page...")
                login_url = f"{self.BASE_URL}/customer/account/login/"
                send_cdp_command(ws, "Page.navigate", {"url": login_url})
                time.sleep(5)  # Wait for page load
            
            # Fill email
            logging.info("      Step 6: Filling login form...")
            js_fill_email = f"""
            (function() {{
                var emailField = document.querySelector('input[name="login[username]"]') || 
                                 document.querySelector('input[type="email"]');
                if (emailField) {{
                    emailField.value = '{CREDENTIALS["email"]}';
                    return {{success: true}};
                }}
                return {{success: false}};
            }})();
            """
            result = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": js_fill_email,
                "returnByValue": True
            })
            
            if not result or not result.get("result", {}).get("result", {}).get("value", {}).get("success"):
                logging.warning("      ⚠️ Failed to fill email")
                ws.close()
                return False
            
            # Fill password
            js_fill_password = f"""
            (function() {{
                var passwordField = document.querySelector('input[name="login[password]"]') || 
                                    document.querySelector('input[type="password"]');
                if (passwordField) {{
                    passwordField.value = '{CREDENTIALS["password"]}';
                    return {{success: true}};
                }}
                return {{success: false}};
            }})();
            """
            result = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": js_fill_password,
                "returnByValue": True
            })
            
            if not result or not result.get("result", {}).get("result", {}).get("value", {}).get("success"):
                logging.warning("      ⚠️ Failed to fill password")
                ws.close()
                return False
            
            # Click login button
            logging.info("      Step 7: Clicking login button...")
            js_click_login = """
            (function() {
                var button = document.querySelector('button[type="submit"].action.login.primary') || 
                             document.querySelector('button[type="submit"]');
                if (button) {
                    button.click();
                    return {success: true};
                }
                return {success: false};
            })();
            """
            result = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": js_click_login,
                "returnByValue": True
            })
            
            if not result or not result.get("result", {}).get("result", {}).get("value", {}).get("success"):
                logging.warning("      ⚠️ Failed to click login button")
                ws.close()
                return False
            
            # Wait for login
            logging.info("      Step 8: Waiting for login to complete...")
            time.sleep(5)
            
            # Check if login successful
            final_url = None
            for attempt in range(3):
                result = send_cdp_command(ws, "Page.getNavigationHistory", timeout_sec=3)
                if result and "result" in result:
                    entries = result.get("result", {}).get("entries", [])
                    if entries:
                        final_url = entries[-1].get("url", "")
                        break
                if attempt < 2:
                    time.sleep(2)
            
            if final_url and "/customer/account/login" not in final_url:
                logging.info(f"      ✅ Login successful! URL: {final_url}")

                # Navigate to start URL via CDP (avoids am start which resets WebView to hardcoded 7770)
                logging.info(f"      Step 9: Navigating to start URL: {self.start_url}")
                send_cdp_command(ws, "Page.navigate", {"url": self.start_url})
                time.sleep(3)

                ws.close()
                return True
            else:
                logging.warning(f"      ⚠️ Login may have failed. URL: {final_url}")
                ws.close()
                return False
            
        except Exception as e:
            logging.error(f"   ❌ WebView CDP auto login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Cleanup
            try:
                subprocess.run([
                    "adb", "-s", device_name,
                    "forward", "--remove", "tcp:9222"
                ], check=False, capture_output=True)
            except:
                pass
    

    def _app_auto_login_fallback(self, device_name: str, env) -> bool:
        """Fallback method using ADB UI automation (coordinates).
        
        This is the old method kept as fallback if CDP doesn't work.
        """
        import time
        import subprocess
        
        CREDENTIALS = {
            "email": "emma.lopez@gmail.com",
            "password": "Password.123",
        }
        
        logging.info("   🔐 Attempting auto login via ADB UI automation (fallback)...")
        
        try:
            # Step 1: Wait for page to fully load
            logging.info("      Step 1: Waiting for login page to load...")
            time.sleep(5)
            
            # Step 2: Navigate to login page first
            logging.info("      Step 2: Navigating to login page...")
            login_url = f"{self.BASE_URL}/customer/account/login/"
            logging.info(f"      Login URL: {login_url}")
            
            # Open the login URL in the WebView
            # This requires JS injection or intent with URL
            # For now, we'll assume the app starts at homepage and we navigate
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "am", "start",
                "-n", "com.onestopshop.app/.MainActivity",
                "-d", login_url
            ], check=False, capture_output=True)
            
            time.sleep(3)  # Wait for page to load
            
            # Step 3: Try CDP method first
            logging.info("      Step 3: Attempting WebView CDP login...")
            cdp_success = self._app_auto_login_webview_cdp(device_name, env)
            if cdp_success:
                return True
            
            # If CDP fails, fall back to coordinate method
            logging.warning("      CDP method failed, falling back to coordinate method...")
            return self._app_auto_login_fallback(device_name, env)
                
        except Exception as e:
            logging.error(f"      ❌ Auto login error: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return False
    
    def _find_element_by_hint(self, xml_path: str, hints: list) -> tuple:
        """Find element coordinates by hint text in UI dump.
        
        Args:
            xml_path: Path to UI dump XML file
            hints: List of hint texts to search for
            
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        import re
        
        try:
            with open(xml_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            for hint in hints:
                # Look for elements with matching hint/text
                pattern = rf'(?:hint|text)="[^"]*{re.escape(hint)}[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    return ((x1 + x2) // 2, (y1 + y2) // 2)
                
                # Also try reverse order (bounds before hint)
                pattern = rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*(?:hint|text)="[^"]*{re.escape(hint)}[^"]*"'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    return ((x1 + x2) // 2, (y1 + y2) // 2)
                    
        except Exception as e:
            logging.debug(f"Error finding element by hint: {e}")
        
        return None
    
    def _find_element_by_text(self, xml_path: str, texts: list) -> tuple:
        """Find element coordinates by exact text in UI dump.
        
        Args:
            xml_path: Path to UI dump XML file
            texts: List of texts to search for
            
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        import re
        
        try:
            with open(xml_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            for text in texts:
                # Look for elements with matching text
                pattern = rf'text="{re.escape(text)}"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    return ((x1 + x2) // 2, (y1 + y2) // 2)
                
                # Also try reverse order
                pattern = rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="{re.escape(text)}"'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    return ((x1 + x2) // 2, (y1 + y2) // 2)
                    
        except Exception as e:
            logging.debug(f"Error finding element by text: {e}")
        
        return None
    
    def _initialize_with_chrome(self, env: interface.AsyncEnv) -> None:
        """Initialize task using Chrome browser (original mode).
        
        This is the original Chrome-based initialization with CDP support.
        """
        # The rest of the original initialize_task code goes here
        # This is called when in Chrome mode
        pass  # Will be implemented by moving existing code
    
    def _get_device_name(self, env: interface.AsyncEnv) -> str:
        """Get Android device name from environment."""
        import subprocess
        
        # Method 1: Use port_utils
        try:
            extracted_port = port_utils.get_console_port_from_env(env)
            if extracted_port is not None:
                return f"emulator-{extracted_port}"
        except Exception:
            pass
        
        # Method 2: Direct access
        try:
            console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
            return f"emulator-{console_port}"
        except Exception:
            pass
        
        # Method 3: adb devices fallback
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                if '\t' in line:
                    return line.split('\t')[0]
        except Exception:
            pass
        
        return "emulator-5554"
    
    @property
    def schema(self) -> dict[str, Any]:
        """JSON schema for WebArena task parameters."""
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "intent": {"type": "string"},
                "start_url": {"type": "string"},
                "eval_config": {"type": "object"},
                "require_login": {"type": "boolean"},
            },
            "required": ["task_id", "intent", "eval_config"],
        }
    
    @property
    def goal(self) -> str:
        """Return the task goal (intent).
        
        Note: We don't add login instructions here anymore.
        Login is handled automatically by CDP in initialize_task().
        If CDP login fails, the agent will see the login page and can login manually.
        """
        return self.intent_text
    
    def initialize_task(self, env: interface.AsyncEnv) -> None:
        """Initialize the WebArena task.
        
        This supports two modes:
        - Chrome mode: launches Chrome with CDP debugging, handles login via CDP
        - App mode: launches Shopping App (WebView), no automatic login
        
        Mode is determined by environment variable or config file.
        """
        super().initialize_task(env)
        
        # Resolve URLs dynamically based on emulator port
        self._resolve_urls_with_env(env)
        
        logging.info(f"Initializing WebArena task {self.task_id}: {self.name}")
        logging.info(f"Goal: {self.goal}")
        logging.info(f"Start URL: {self.start_url}")
        print(f"🌐 Actual Start URL: {self.start_url}")
        
        # ============================================================
        # Detect Shopping mode (Chrome or App)
        # ============================================================
        shopping_mode = self._get_shopping_mode()
        logging.info(f"🎯 Shopping mode: {shopping_mode}")
        print(f"🎯 Shopping mode: {shopping_mode}")
        
        if shopping_mode == "app":
            # Use Shopping App mode
            self._initialize_with_app(env)
            return
        
        # Open Chrome and navigate to start URL using CDP
        try:
            import time
            import subprocess
            from scendroid.env import adb_utils
            from scendroid.task_evals.webarena import chrome_cdp_auth
            
            # Step 0: Clear any possible proxy setup (to avoid network redirection)
            logging.info("Clearing proxy settings...")
            import subprocess as sp
            
            # Get correct device name from controller config
            device_name_temp = None
            
            # 🆕 Method 1: Use port_utils.get_console_port_from_env (most reliable)
            try:
                extracted_port = port_utils.get_console_port_from_env(env)
                if extracted_port is not None:
                    device_name_temp = f"emulator-{extracted_port}"
                    logging.info(f"✅ Got device from port_utils: {device_name_temp} (console_port: {extracted_port})")
            except Exception as e:
                logging.warning(f"⚠️  port_utils.get_console_port_from_env failed: {e}")
            
            # Method 2: Direct access (fallback)
            if device_name_temp is None:
                try:
                    # Access via: AsyncAndroidEnv -> ScenDroidController -> wrapped env -> config
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    device_name_temp = f"emulator-{console_port}"
                    logging.info(f"✅ Got device from direct access: {device_name_temp} (console_port: {console_port})")
                except Exception as e:
                    logging.warning(f"⚠️  Direct access failed: {e}")
            
            # Method 3: adb devices fallback (least reliable)
            if device_name_temp is None:
                try:
                    result = sp.run(["adb", "devices"], capture_output=True, text=True)
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if '\t' in line:
                            device_name_temp = line.split('\t')[0]
                            logging.warning(f"⚠️  Using first device from adb devices: {device_name_temp} (may be incorrect for multi-emulator setup)")
                            break
                except Exception as e2:
                    logging.warning(f"⚠️  adb devices fallback also failed: {e2}")
            
            if not device_name_temp:
                device_name_temp = "emulator-5554"
                logging.warning(f"⚠️  Using default device: {device_name_temp} (fallback)")
            
            # Clear proxy setup
            sp.run([
                "adb", "-s", device_name_temp,
                "shell", "settings", "put", "global", "http_proxy", ":0"
            ], check=False, capture_output=True)
            
            sp.run([
                "adb", "-s", device_name_temp,
                "shell", "settings", "delete", "global", "http_proxy"
            ], check=False, capture_output=True)
            
            sp.run([
                "adb", "-s", device_name_temp,
                "shell", "settings", "delete", "global", "https_proxy"
            ], check=False, capture_output=True)
            
            # Step 1: Get device name
            def get_device_name() -> str:
                """Get Android device name."""
                # 🆕 Method 1: Use port_utils.get_console_port_from_env (most reliable - already tested and fixed)
                try:
                    extracted_port = port_utils.get_console_port_from_env(env)
                    if extracted_port is not None:
                        device_name = f"emulator-{extracted_port}"
                        logging.info(f"✅ [get_device_name] Got device from port_utils: {device_name} (console_port: {extracted_port})")
                        return device_name
                except Exception as e:
                    logging.warning(f"⚠️  [get_device_name] port_utils.get_console_port_from_env failed: {e}")
                
                # Method 2: Direct access (fallback for compatibility)
                try:
                    # Access via: AsyncAndroidEnv -> ScenDroidController -> wrapped env -> config
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    device_name = f"emulator-{console_port}"
                    logging.info(f"✅ [get_device_name] Got device from direct access: {device_name} (console_port: {console_port})")
                    return device_name
                except Exception as e:
                    logging.warning(f"⚠️  [get_device_name] Direct access failed: {e}")
                
                # Method 3: Try controller attributes
                if hasattr(env, 'controller'):
                    if hasattr(env.controller, '_device_name'):
                        device_name = env.controller._device_name
                        logging.info(f"✅ [get_device_name] Got device from controller._device_name: {device_name}")
                        return device_name
                    if hasattr(env.controller, 'device_name'):
                        device_name = env.controller.device_name
                        logging.info(f"✅ [get_device_name] Got device from controller.device_name: {device_name}")
                        return device_name
                
                # Method 4: Fallback - get first device from adb devices (less reliable)
                try:
                    result = subprocess.run(
                        ["adb", "devices"],
                        capture_output=True, text=True, check=True
                    )
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if '\t' in line:
                            device = line.split('\t')[0]
                            if device:
                                logging.warning(f"⚠️  [get_device_name] Using first device from adb devices: {device} (may be incorrect for multi-emulator setup)")
                                return device
                except Exception as e:
                    logging.debug(f"Could not get device from adb devices: {e}")
                
                # Final fallback
                logging.warning("⚠️  [get_device_name] Using default device emulator-5554 (fallback - may be incorrect)")
                return "emulator-5554"
            
            device_name = get_device_name()
            logging.info(f"Using device: {device_name}")
            
            # Step 2: Launch Shopping via home screen shortcut
            # Tap the Shopping shortcut on the home screen to open the URL
            # Shortcut location: coordinates (162, 1615)
            logging.info("Launching Shopping via home screen shortcut...")
            
            # Force stop Chrome first
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "am", "force-stop", "com.android.chrome"
            ], check=False, capture_output=True)
            
            time.sleep(1)
            
            # Press the Home key to return to the home screen
            logging.info("   📱 Pressing Home to go to home screen...")
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "input", "keyevent", "KEYCODE_HOME"
            ], check=False, capture_output=True)
            
            time.sleep(1)
            
            # Tap the Shopping shortcut (coordinates 162, 1615)
            logging.info("   🛒 Clicking Shopping shortcut at (162, 1615)...")
            target_url = self.start_url or self.BASE_URL
            print(f"🎯 The Shopping shortcut will open: {target_url}")
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "input", "tap", "162", "1615"
            ], check=True, capture_output=True)
            
            # Wait for Shopping page to fully load
            time.sleep(5)
            
            # Step 3: Handle login if task requires it (using improved CDP)
            logging.info(f"🔍 Checking login requirement: self.require_login = {self.require_login}")
            logging.info(f"🔍 Task params: task_id={self.task_id}, intent={self.intent_text[:50]}...")
            
            if self.require_login:
                logging.info("=" * 70)
                logging.info("🔐 Task requires login, attempting CDP-based authentication...")
                logging.info("=" * 70)
                print(f"🔐 Starting automatic login...")
                try:
                    # ✅ Use force_restart=False because Chrome has already been opened via the shortcut
                    login_success = chrome_cdp_auth.login_to_shopping(env, force_restart=False)
                    if login_success:
                        logging.info("=" * 70)
                        logging.info("✅ CDP login successful")
                        logging.info("=" * 70)
                        print(f"✅ Automatic login succeeded! ")
                        # After successful login, navigate again to start_url (login may redirect to the homepage)
                        if self.start_url:
                            logging.info(f"Re-navigating to start_url after login: {self.start_url}")
                            print(f"🔄 Navigating again after login: {self.start_url}")
                            subprocess.run([
                                "adb", "-s", device_name,
                                "shell", "am", "start",
                                "-n", "com.android.chrome/com.google.android.apps.chrome.Main",
                                "-a", "android.intent.action.VIEW",
                                "-d", self.start_url
                            ], check=False, capture_output=True)
                            time.sleep(2)
                    else:
                        logging.warning("=" * 70)
                        logging.warning("⚠️ CDP login failed")
                        logging.warning("=" * 70)
                        print(f"⚠️  Automatic login failed")
                        logging.info("   Agent should login with:")
                        logging.info("   Email: emma.lopez@gmail.com")
                        logging.info("   Password: Password.123")
                except Exception as login_error:
                    logging.warning("=" * 70)
                    logging.warning(f"⚠️ CDP login error: {login_error}")
                    logging.warning("=" * 70)
                    print(f"⚠️  Login error: {login_error}")
                    import traceback
                    logging.warning(traceback.format_exc())
                    logging.info("   Agent should login with:")
                    logging.info("   Email: emma.lopez@gmail.com")
                    logging.info("   Password: Password.123")
            else:
                logging.info("=" * 70)
                logging.info("ℹ️  Task does NOT require login (require_login=False)")
                logging.info("=" * 70)
                print(f"ℹ️  This task does not require login")
            
            logging.info("✅ Chrome initialized, ready for agent interaction")
            
        except Exception as e:
            logging.error(f"Error initializing Chrome with CDP: {e}")
            # Fallback to basic Chrome launch if CDP fails
            logging.warning("Falling back to basic Chrome launch...")
            try:
                adb_utils.send_android_intent(
                    'start',
                    'android.intent.action.VIEW',
                    env.controller,
                    data_uri=self.start_url or self.BASE_URL
                )
            except Exception as fallback_error:
                logging.error(f"Fallback also failed: {fallback_error}")
                raise
    
    def tear_down(self, env: interface.AsyncEnv) -> None:
        """Clean up after task execution.
        
        Handles both Chrome and App modes:
        - Chrome mode: close Chrome, remove port forwarding
        - App mode: close Shopping App
        """
        super().tear_down(env)
        
        try:
            from scendroid.env import adb_utils
            import time
            import subprocess
            
            # Get current mode
            shopping_mode = self._get_shopping_mode()
            device_name = self._get_device_name(env)
            
            if shopping_mode == "app":
                # App mode cleanup
                logging.info("Cleaning up Shopping App state...")
                
                PACKAGE_NAME = "com.onestopshop.app"
                subprocess.run([
                    "adb", "-s", device_name,
                    "shell", "am", "force-stop", PACKAGE_NAME
                ], check=False, capture_output=True)
                
                logging.info("✅ Shopping App cleanup completed")
            else:
                # Chrome mode cleanup
                logging.info("Cleaning up Chrome state...")
                
                # Close Chrome (uses 'am force-stop' internally)
                # Note: We don't clear app data to avoid triggering Welcome screen
                chrome_app_name = "chrome"
                adb_utils.close_app(chrome_app_name, env.controller)
                time.sleep(1)
                
                # Remove port forwarding
                subprocess.run([
                    "adb", "-s", device_name,
                    "forward", "--remove-all"
                ], check=False, capture_output=True)
                
                logging.info("✅ Chrome cleanup completed (data preserved)")
            
        except Exception as e:
            logging.warning(f"Error during cleanup: {e}")
    
    @abc.abstractmethod
    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if the task is successful.
        
        This should be implemented by specific task types based on their
        evaluation method (string_match, url_match, program_html).
        
        Args:
            env: Android environment
            
        Returns:
            1.0 if successful, 0.0 if failed
        """
        pass
    
    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        """Generate random parameters.
        
        For WebArena tasks, parameters are loaded from config files,
        not randomly generated.
        """
        return {
            "task_id": -1,
            "intent": "",
            "start_url": cls.BASE_URL,
            "eval_config": {},
            "require_login": False,
        }


class StringMatchWebArenaTask(WebArenaTaskEval):
    """WebArena task that requires string matching evaluation.
    
    The agent needs to provide a text answer that matches the reference answer.
    """
    
    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Evaluate task success based on string matching.
        
        For string match tasks, we need to get the agent's answer and
        compare it with the reference answer.
        
        Note: This requires the agent to store its final answer somewhere
        accessible (e.g., in env.interaction_cache or a dedicated field).
        """
        self._check_is_initialized()
        
        # Force flush for debugging
        import sys
        
        try:
            print("\n🔍 [DEBUG] Entering StringMatchWebArenaTask.is_successful", flush=True)
            
            # Try to get agent's answer from environment
            # The agent should store its answer in a standard location
            agent_answer = self._get_agent_answer(env)
            print(f"🔍 [DEBUG] agent_answer = {agent_answer}", flush=True)
            
            if agent_answer is None:
                logging.warning("No agent answer found for string_match evaluation")
                print("❌ [DEBUG] agent_answer is None", flush=True)
                return 0.0
            
            print(f"🔍 [DEBUG] Starting call to evaluate_task", flush=True)
            
            # Use WebArena's evaluation logic (adapted for Android)
            score, explanation = webarena_evaluator.evaluate_task(
                env=env,
                task_config={
                    "eval": self.eval_config,
                    "intent": self.intent_text,
                },
                agent_answer=agent_answer
            )
            
            print(f"🔍 [DEBUG] evaluate_task return: score={score}", flush=True)
            
            # Print detailed evaluation explanation
            print("\n" + "="*80, flush=True)
            print("📊 Evaluation details", flush=True)
            print("="*80, flush=True)
            print(f"Agent answer: {agent_answer}", flush=True)
            print(f"Final score: {score}", flush=True)
            print("\nEvaluation explanation:", flush=True)
            print(explanation, flush=True)
            print("="*80 + "\n", flush=True)
            
            logging.info(f"String match evaluation score: {score}")
            logging.info(f"Evaluation explanation:\n{explanation}")
            return score
            
        except Exception as e:
            logging.error(f"Error in string match evaluation: {e}")
            print(f"❌ [DEBUG] exception: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return 0.0
    
    def _get_agent_answer(self, env: interface.AsyncEnv) -> str | None:
        """Extract agent's final answer.
        
        Uses ScenDroid's standard method: directly read from env.interaction_cache
        This is how ScenDroid's information_retrieval tasks get agent answers.
        
        Args:
            env: Android environment
            
        Returns:
            Agent's answer as string, or None if not found
        """
        # ✅ Directly use ScenDroid's method (refer to information_retrieval.py)
        if hasattr(env, 'interaction_cache') and env.interaction_cache:
            return str(env.interaction_cache)
        
        return None


# Helper method for all task types
def _get_page_info_via_cdp(env: interface.AsyncEnv, force_restart: bool = False) -> tuple[str, str]:
    """Get current URL and HTML content via CDP.
    
    This is a module-level helper function used by all WebArena task types.
    
    Args:
        env: ScenDroid environment
        force_restart: If True, force restart Chrome. If False (default), 
                      connect to existing Chrome without disrupting it.
        
    Returns:
        Tuple of (url, html_content)
    """
    import asyncio
    from scendroid.task_evals.webarena import chrome_cdp
    
    async def get_info():
        try:
            print(f"\n🔍 [DEBUG] _get_page_info_via_cdp called, force_restart={force_restart}", flush=True)
            cdp_manager = chrome_cdp.ChromeCDPManager(env)
            # Don't restart Chrome during evaluation
            page = await cdp_manager.connect(force_restart=force_restart)
            
            # ✅ Wait for the page to stabilize to avoid retrieving outdated page status
            try:
                print(f"⏳ [DEBUG] Waiting for page load to complete...", flush=True)
                # Strategy 1: Wait until the network is idle (all requests completed), with a maximum wait of 5 seconds
                await page.wait_for_load_state('networkidle', timeout=5000)
                print(f"✅ [DEBUG] Network is idle", flush=True)
            except Exception as wait_error:
                # If the wait times out, continue execution (the page may already be static)
                logging.warning(f"Wait for load state timeout: {wait_error}")
                print(f"⚠️ [DEBUG] Network idle wait timed out (the page may be static)", flush=True)
            
            # Strategy 2: Wait an additional short period to ensure the DOM and URL are fully updated
            # Avoid capturing the navigation intermediate status
            await page.wait_for_timeout(500)  # e.g., wait for 500 ms
            
            # strategy3: Poll to check whether the URL is stable (up to 3 times)
            url = page.url
            print(f"📍 [DEBUG] Initial URL: {url[:80]}...", flush=True)
            
            for i in range(2):  # Check 2 more times
                await page.wait_for_timeout(500)  # Wait 500 ms each time
                new_url = page.url
                if new_url != url:
                    print(f"🔄 [DEBUG] URL changed: {new_url[:80]}...", flush=True)
                    url = new_url
                else:
                    print(f"✓ [DEBUG] URL is stable", flush=True)
                    break
            
            html = await page.content()
            
            print(f"✅ [DEBUG] Successfully retrieved page info: URL={url[:80]}...", flush=True)
            
            await cdp_manager.disconnect()
            
            return url, html
        except Exception as e:
            logging.error(f"Error getting page info via CDP: {e}")
            print(f"❌ [DEBUG] Failed to retrieve page info: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return "", ""
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_info())
    finally:
        loop.close()


class URLMatchWebArenaTask(WebArenaTaskEval):
    """WebArena task that requires URL matching evaluation.
    
    The agent needs to navigate to the correct URL.
    """
    
    @staticmethod
    def _normalize_url_query_params(url: str) -> str:
        """Normalize URL query parameters by stripping leading and trailing whitespace from parameter values.
        
        e.g.: "?q=usb+wifi+" → "?q=usb+wifi"
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url)
        
        if not parsed.query:
            return url
        
        # Parse query parameters
        query_dict = parse_qs(parsed.query, keep_blank_values=True)
        
        # Strip whitespace from each parameter value
        normalized_query = {}
        for key, values in query_dict.items():
            # parse_qs returns a list; strip each value
            normalized_query[key] = [v.strip() for v in values]
        
        # Re-encode query parameters (doseq=True preserves list format)
        new_query = urlencode(normalized_query, doseq=True)
        
        # Reconstruct the URL
        normalized_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return normalized_url
    
    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Evaluate task success based on URL matching using CDP.
        
        Check if the current URL matches the reference URL.
        """
        self._check_is_initialized()
        
        try:
            # Get current URL via CDP
            current_url, _ = _get_page_info_via_cdp(env)
            
            if not current_url:
                logging.warning("Could not get current URL via CDP")
                return 0.0
            
            logging.info(f"Current URL (via CDP): {current_url}")
            
            # Normalize URL query parameters (remove extra whitespace)
            current_url = self._normalize_url_query_params(current_url)
            logging.info(f"Normalized URL: {current_url}")
            
            # Use WebArena's URL evaluation logic
            from evaluation_harness.evaluators import URLEvaluator
            from evaluation_harness.helper_functions import PseudoPage
            import tempfile
            import json
            
            evaluator = URLEvaluator()
            
            # Create a mock Page object (PseudoPage needs an original_page)
            class MockPage:
                """Minimal mock of Playwright Page for URL evaluation."""
                def __init__(self, url):
                    self.url = url
            
            # Use PseudoPage to satisfy beartype checking
            mock_page = MockPage(current_url)
            page = PseudoPage(original_page=mock_page, url=current_url)
            
            # URLEvaluator expects a config file, so create a temporary one
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({'eval': self.eval_config, 'intent': self.intent_text}, f)
                config_file = f.name
            
            try:
                # URLEvaluator expects (trajectory, config_file, page, client)
                # trajectory is not used for URL matching, so pass empty list
                score = evaluator(
                    trajectory=[],  # Empty trajectory
                    config_file=config_file,
                    page=page,
                    client=None  # No CDP client needed for URL matching
                )
            finally:
                # Clean up temp file
                import os
                if os.path.exists(config_file):
                    os.unlink(config_file)
            
            logging.info(f"URL match evaluation score: {score}")
            return float(score)
            
        except Exception as e:
            logging.error(f"Error in URL match evaluation: {e}")
            import traceback
            traceback.print_exc()
            return 0.0


class ProgramHTMLWebArenaTask(WebArenaTaskEval):
    """WebArena task that requires HTML content checking.
    
    The agent needs to perform actions and we check the resulting page content.
    """
    
    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Evaluate task success based on program_html using CDP.
        
        This properly implements program_html evaluation:
        1. Resolve dynamic URLs (func:xxx())
        2. Navigate to target page via CDP
        3. Execute JavaScript locator
        4. Check required content
        """
        self._check_is_initialized()
        
        print("\n🔍 [DEBUG] Entering ProgramHTMLWebArenaTask.is_successful", flush=True)
        
        try:
            # Get program_html targets from config
            program_html = self.eval_config.get("program_html", [])
            
            if not program_html:
                logging.warning("No program_html targets specified")
                return 1.0
            
            # ✅ Use CDP to navigate and execute JavaScript locators
            from scendroid.task_evals.webarena import program_html_helper
            
            score, explanation = program_html_helper.evaluate_program_html_via_cdp(
                env, program_html
            )
            
            # Print evaluation details
            print("\n" + "="*80, flush=True)
            print("📊 Evaluation details", flush=True)
            print("="*80, flush=True)
            print(f"Final score: {score}", flush=True)
            print("\nEvaluation description:", flush=True)
            print(explanation, flush=True)
            print("="*80 + "\n", flush=True)
            
            logging.info(f"Program HTML evaluation score: {score}")
            logging.info(f"Evaluation explanation:\n{explanation}")
            return score
            
        except Exception as e:
            logging.error(f"Error in program_html evaluation: {e}")
            print(f"❌ [DEBUG] exception: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return 0.0


# Factory function to create the appropriate task type
def create_webarena_task(task_config: dict[str, Any]) -> WebArenaTaskEval:
    """Create a WebArena task instance based on the evaluation type.
    
    Args:
        task_config: Task configuration from WebArena JSON
        
    Returns:
        Appropriate WebArenaTaskEval subclass instance
    """
    eval_types = task_config.get("eval", {}).get("eval_types", [])
    
    # Determine primary evaluation type
    if "string_match" in eval_types:
        task_class = StringMatchWebArenaTask
    elif "url_match" in eval_types:
        task_class = URLMatchWebArenaTask
    elif "program_html" in eval_types:
        task_class = ProgramHTMLWebArenaTask
    else:
        # Default to string match
        logging.warning(f"Unknown eval type: {eval_types}, using StringMatch")
        task_class = StringMatchWebArenaTask
    
    # Prepare parameters
    params = {
        "task_id": task_config.get("task_id", -1),
        "intent": task_config.get("intent", ""),
        "start_url": task_config.get("start_url", ""),
        "eval_config": task_config.get("eval", {}),
        "require_login": task_config.get("require_login", False),
    }
    
    return task_class(params)

