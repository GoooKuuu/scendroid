"""Helper functions for program_html evaluation with CDP.

This module provides functions to:
1. Resolve dynamic URLs (func:xxx())
2. Navigate to target pages via CDP
3. Execute JavaScript locators via CDP
4. Extract and evaluate content
"""

import re
import logging
import os
from typing import Any, Optional
from scendroid.env import interface
from scendroid.task_evals.webarena import port_utils


def _get_shopping_mode() -> str:
    """Get current shopping mode (chrome or app) from config file.
    
    Returns:
        'chrome' or 'app', defaults to 'chrome' if not specified
    """
    config_file = "/tmp/shopping_mode.conf"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('SHOPPING_MODE='):
                        mode = line.split('=', 1)[1].strip()
                        return mode.lower()
    except Exception as e:
        logging.debug(f"Could not read shopping mode from {config_file}: {e}")
    
    # Check environment variable as fallback
    mode = os.environ.get('SHOPPING_MODE', 'chrome')
    return mode.lower()


def resolve_url(url_spec: str, env: Optional[interface.AsyncEnv] = None) -> str:
    """Resolve URL specification, supporting dynamic functions and placeholders.
    
    Args:
        url_spec: URL or function call like "func:shopping_get_latest_order_url()"
                  or URL with __SHOPPING__ placeholder
        env: ScenDroid AsyncEnv instance (optional, for dynamic port mapping)
        
    Returns:
        Resolved URL string
    """
    if not url_spec:
        return url_spec
    
    # Replace __SHOPPING__ placeholder with actual base URL (dynamic port mapping)
    base_url = port_utils.get_shopping_base_url(env)
    url_spec = url_spec.replace('__SHOPPING__', base_url)
    
    # If not a function call, return the resolved URL
    if not url_spec.startswith("func:"):
        return url_spec
    
    # Extract function name
    match = re.match(r'func:(\w+)\(\)', url_spec)
    if not match:
        logging.error(f"Invalid func URL format: {url_spec}")
        return url_spec
    
    func_name = match.group(1)
    
    # Import and call the function
    try:
        from evaluation_harness.helper_functions import (
            shopping_get_latest_order_url,
            shopping_get_sku_latest_review_author,
            shopping_get_sku_latest_review_rating,
        )
        
        func_map = {
            'shopping_get_latest_order_url': shopping_get_latest_order_url,
            'shopping_get_sku_latest_review_author': shopping_get_sku_latest_review_author,
            'shopping_get_sku_latest_review_rating': shopping_get_sku_latest_review_rating,
        }
        
        if func_name not in func_map:
            logging.error(f"Unknown function: {func_name}")
            return url_spec
        
        resolved_url = func_map[func_name]()
        logging.info(f"Resolved {url_spec} → {resolved_url}")
        return resolved_url
        
    except Exception as e:
        logging.error(f"Error resolving {url_spec}: {e}")
        return url_spec


async def navigate_and_execute_locator(
    page, 
    url: str, 
    locator: str
) -> str:
    """Navigate to URL and execute JavaScript locator via CDP.
    
    Args:
        page: Playwright page object
        url: Target URL to navigate to
        locator: JavaScript expression to evaluate
        
    Returns:
        Content extracted by the locator
    """
    try:
        # Navigate to target URL if specified
        if url:
            logging.info(f"Navigating to: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Execute JavaScript locator or get full page content
        if not locator or not locator.strip():
            # Empty locator: get full page content
            logging.info("Empty locator, getting full page content")
            content = await page.content()
        else:
            # Execute JavaScript locator
            logging.info(f"Executing locator: {locator}")
            result = await page.evaluate(locator)
            content = str(result) if result is not None else ""
        
        logging.info(f"Locator result (first 200 chars): {content[:200]}")
        return content
        
    except Exception as e:
        logging.error(f"Error executing locator: {e}")
        print(f"❌ [DEBUG] JavaScriptexecutefailed: {e}", flush=True)
        return ""


def evaluate_program_html_via_cdp(
    env: interface.AsyncEnv,
    program_html_targets: list[dict[str, Any]]
) -> tuple[float, str]:
    """Evaluate program_html checks using CDP.
    
    Supports both Chrome mode and App (WebView) mode.
    
    Args:
        env: ScenDroid environment
        program_html_targets: List of check configurations from eval_config
        
    Returns:
        tuple: (score, explanation)
    """
    # Check shopping mode
    shopping_mode = _get_shopping_mode()
    logging.info(f"🎯 Evaluation mode: {shopping_mode}")
    
    if shopping_mode == 'app':
        return evaluate_program_html_via_webview_cdp(env, program_html_targets)
    else:
        return evaluate_program_html_via_chrome_cdp(env, program_html_targets)


def evaluate_program_html_via_chrome_cdp(
    env: interface.AsyncEnv,
    program_html_targets: list[dict[str, Any]]
) -> tuple[float, str]:
    """Evaluate program_html checks using Chrome CDP.
    
    Args:
        env: ScenDroid environment
        program_html_targets: List of check configurations from eval_config
        
    Returns:
        tuple: (score, explanation)
    """
    import asyncio
    from scendroid.task_evals.webarena import chrome_cdp
    
    async def evaluate():
        try:
            # Connect to Chrome via CDP
            cdp_manager = chrome_cdp.ChromeCDPManager(env)
            page = await cdp_manager.connect(force_restart=False)
            
            score = 1.0
            explanations = []
            
            for i, target in enumerate(program_html_targets, 1):
                
                # 1. Resolve URL (pass env for dynamic port mapping)
                url_spec = target.get('url', '')
                target_url = resolve_url(url_spec, env)
                
                # 2. Execute locator
                locator = target.get('locator', '')
                content = await navigate_and_execute_locator(page, target_url, locator)
                
                # If the locator is empty, also retrieve plain text content as a fallback
                text_content = None
                if not locator or not locator.strip():
                    try:
                        text_content = await page.evaluate('document.body.innerText')
                    except Exception as e:
                        logging.warning(f"Could not get text content: {e}")
                
                # 3. Check required contents
                required_contents = target.get('required_contents', {})
                
                if 'must_include' in required_contents:
                    must_include_list = required_contents['must_include']
                    if not isinstance(must_include_list, list):
                        must_include_list = [must_include_list]
                    
                    for required in must_include_list:
                        # Support two match modes:
                        # 1. Exact string match (original mode)
                        # 2. Keyword match (keywords separated by |AND|)
                        
                        # Check whether keyword match mode is used (contains |AND|)
                        if ' |AND| ' in required:
                            # Keyword match: all keywords must appear
                            keywords = [kw.strip() for kw in required.split(' |AND| ')]
                            logging.info(f"Keyword matching mode: {keywords}")
                            
                            # Check each keyword
                            all_found = True
                            found_keywords = []
                            missing_keywords = []
                            
                            for keyword in keywords:
                                found_in_html = keyword.lower() in content.lower()
                                found_in_text = text_content and keyword.lower() in text_content.lower()
                                
                                if found_in_html or found_in_text:
                                    where = "HTML" if found_in_html else "text"
                                    found_keywords.append(f"{keyword} ({where})")
                                else:
                                    all_found = False
                                    missing_keywords.append(keyword)
                            
                            if all_found:
                                explanations.append(f"✅ checkpoint{i}: All keywords found - {', '.join(found_keywords)}")
                            else:
                                score *= 0.0
                                explanations.append(f"❌ checkpoint{i}: Missing keywords - {', '.join(missing_keywords)}")
                        else:
                            # Exact string match (original mode)
                            found_in_html = required.lower() in content.lower()
                            found_in_text = text_content and required.lower() in text_content.lower()
                            
                            if found_in_html or found_in_text:
                                where = "HTML" if found_in_html else "text"
                                explanations.append(f"✅ checkpoint{i}: '{required}' present in content ({where})")
                            else:
                                score *= 0.0
                                explanations.append(f"❌ checkpoint{i}: '{required}' not present in content")
                                # Show excerpt of content for debugging
                                excerpt = content[:300] if content else "(empty)"
                                explanations.append(f"   Content excerpt: {excerpt}...")
            
            await cdp_manager.disconnect()
            
            return score, "\n".join(explanations)
            
        except Exception as e:
            logging.error(f"CDP program_html evaluation error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0, f"❌ evaluation error: {e}"
    
    # Run async evaluation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(evaluate())
    finally:
        loop.close()


def evaluate_program_html_via_webview_cdp(
    env: interface.AsyncEnv,
    program_html_targets: list[dict[str, Any]]
) -> tuple[float, str]:
    """Evaluate program_html checks using WebView CDP (App mode).
    
    Uses native WebSocket + CDP commands to connect to WebView.
    
    Args:
        env: ScenDroid environment
        program_html_targets: List of check configurations from eval_config
        
    Returns:
        tuple: (score, explanation)
    """
    import subprocess
    import json
    import requests
    import websocket
    import time
    
    logging.info("📱 Using WebView CDP for evaluation (App mode)")
    
    try:
        # Step 1: Get device name
        device_name = _get_device_name(env)
        logging.info(f"Device: {device_name}")
        
        # Step 2: Find WebView debugging port
        result = subprocess.run([
            "adb", "-s", device_name,
            "shell", "cat /proc/net/unix | grep webview_devtools_remote"
        ], capture_output=True, text=True)
        
        if "webview_devtools_remote" not in result.stdout:
            logging.warning("WebView debugging port not found")
            return 0.0, "❌ WebView debugportnot found"
        
        # Extract port name
        import re
        match = re.search(r'@(webview_devtools_remote_\d+)', result.stdout)
        if not match:
            logging.warning(f"Cannot parse WebView port: {result.stdout}")
            return 0.0, "❌ Unable to parse WebView port"
        
        webview_socket = match.group(1)
        logging.info(f"WebView port: {webview_socket}")
        
        # Step 3: Port forwarding
        subprocess.run([
            "adb", "-s", device_name,
            "forward", "tcp:9222", f"localabstract:{webview_socket}"
        ], check=False, capture_output=True)
        time.sleep(1)
        
        # Step 4: Get WebSocket URL
        response = requests.get("http://localhost:9222/json", timeout=5)
        pages = response.json()
        
        if not pages:
            logging.warning("No pages found in WebView")
            return 0.0, "❌ Page not found in WebView"
        
        ws_url = pages[0]["webSocketDebuggerUrl"]
        logging.info(f"WebSocket URL: {ws_url}")
        
        # Step 5: Connect via WebSocket
        ws = websocket.create_connection(ws_url, timeout=10)
        ws.settimeout(5)
        
        # CDP command counter
        command_id = 100
        
        def send_cdp_command(method, params=None, timeout_sec=10):
            """Send CDP command and wait for response."""
            nonlocal command_id
            command_id += 1
            cmd_id = command_id
            
            command = {"id": cmd_id, "method": method}
            if params:
                command["params"] = params
            
            ws.send(json.dumps(command))
            logging.debug(f"→ {method} (id={cmd_id})")
            
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout_sec:
                try:
                    msg = ws.recv()
                    data = json.loads(msg)
                    
                    # Skip events
                    if "method" in data:
                        logging.debug(f"⏭️  {data['method']}")
                        continue
                    
                    # Check if this is our response
                    if data.get("id") == cmd_id:
                        if "result" in data:
                            logging.debug("✓ Success")
                            return data
                        elif "error" in data:
                            logging.warning(f"✗ Error: {data['error']}")
                            return None
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception as e:
                    logging.error(f"✗ Exception: {e}")
                    return None
            
            logging.warning("✗ Timeout")
            return None
        
        # Enable CDP domains
        send_cdp_command("Page.enable")
        send_cdp_command("DOM.enable")
        send_cdp_command("Runtime.enable")
        
        # Evaluate each target
        score = 1.0
        explanations = []
        
        for i, target in enumerate(program_html_targets, 1):
            # 1. Resolve URL
            url_spec = target.get('url', '')
            target_url = resolve_url(url_spec, env)
            logging.info(f"Check {i}: URL = {target_url}")
            
            # 2. Navigate if needed
            if target_url:
                result = send_cdp_command("Page.getNavigationHistory")
                current_url = ""
                if result and "result" in result:
                    entries = result.get("result", {}).get("entries", [])
                    if entries:
                        current_url = entries[-1].get("url", "")
                
                if current_url != target_url:
                    logging.info(f"Navigating to: {target_url}")
                    send_cdp_command("Page.navigate", {"url": target_url})
                    time.sleep(5)  # Wait for page load
            
            # 3. Execute locator
            locator = target.get('locator', '')
            content = ""
            text_content = None
            
            if not locator or not locator.strip():
                # Empty locator: get full page content
                result = send_cdp_command("Runtime.evaluate", {
                    "expression": "document.body.innerHTML",
                    "returnByValue": True
                })
                if result:
                    content = result.get("result", {}).get("result", {}).get("value", "")
                
                # Also get text content
                result = send_cdp_command("Runtime.evaluate", {
                    "expression": "document.body.innerText",
                    "returnByValue": True
                })
                if result:
                    text_content = result.get("result", {}).get("result", {}).get("value", "")
            else:
                # Execute JavaScript locator
                logging.info(f"Executing locator: {locator}")
                result = send_cdp_command("Runtime.evaluate", {
                    "expression": locator,
                    "returnByValue": True
                })
                if result:
                    value = result.get("result", {}).get("result", {}).get("value")
                    content = str(value) if value is not None else ""
            
            logging.info(f"Content (first 200 chars): {content[:200]}")
            
            # 4. Check required contents
            required_contents = target.get('required_contents', {})
            
            if 'must_include' in required_contents:
                must_include_list = required_contents['must_include']
                if not isinstance(must_include_list, list):
                    must_include_list = [must_include_list]
                
                for required in must_include_list:
                    # Support keyword matching with |AND|
                    if ' |AND| ' in required:
                        keywords = [kw.strip() for kw in required.split(' |AND| ')]
                        logging.info(f"Keyword matching mode: {keywords}")
                        
                        all_found = True
                        found_keywords = []
                        missing_keywords = []
                        
                        for keyword in keywords:
                            found_in_html = keyword.lower() in content.lower()
                            found_in_text = text_content and keyword.lower() in text_content.lower()
                            
                            if found_in_html or found_in_text:
                                where = "HTML" if found_in_html else "text"
                                found_keywords.append(f"{keyword} ({where})")
                            else:
                                all_found = False
                                missing_keywords.append(keyword)
                        
                        if all_found:
                            explanations.append(f"✅ checkpoint{i}: All keywords found - {', '.join(found_keywords)}")
                        else:
                            score *= 0.0
                            explanations.append(f"❌ checkpoint{i}: Missing keywords - {', '.join(missing_keywords)}")
                    else:
                        # Full string matching
                        found_in_html = required.lower() in content.lower()
                        found_in_text = text_content and required.lower() in text_content.lower()
                        
                        if found_in_html or found_in_text:
                            where = "HTML" if found_in_html else "text"
                            explanations.append(f"✅ checkpoint{i}: '{required}' present in content ({where})")
                        else:
                            score *= 0.0
                            explanations.append(f"❌ checkpoint{i}: '{required}' not present in content")
                            excerpt = content[:300] if content else "(empty)"
                            explanations.append(f"   Content excerpt: {excerpt}...")
        
        # Cleanup
        ws.close()
        subprocess.run([
            "adb", "-s", device_name,
            "forward", "--remove", "tcp:9222"
        ], check=False, capture_output=True)
        
        return score, "\n".join(explanations)
        
    except Exception as e:
        logging.error(f"WebView CDP evaluation error: {e}")
        import traceback
        traceback.print_exc()
        return 0.0, f"❌ evaluation error: {e}"


def _get_device_name(env: interface.AsyncEnv) -> str:
    """Get Android device name from environment."""
    try:
        console_port = port_utils.get_console_port_from_env(env)
        if console_port is not None:
            return f"emulator-{console_port}"
    except Exception as e:
        logging.debug(f"Could not get console port: {e}")
    
    # Fallback
    return "emulator-5554"

