"""WebArena authentication using Chrome CDP.

This module implements automatic login to OneStopShop using Playwright
connected via CDP to Android Chrome.
"""

import asyncio
import os
from absl import logging
from scendroid.env import interface
from scendroid.task_evals.webarena import chrome_cdp

# OneStopShop credentials
SHOPPING_CREDENTIALS = {
    "username": "emma.lopez@gmail.com",
    "password": "Password.123",
}

# Get Shopping URL dynamically (supports multi-emulator isolation)
from scendroid.task_evals.webarena import port_utils

def get_shopping_login_url(env=None) -> str:
    """Get Shopping login URL dynamically based on emulator port.
    
    Args:
        env: ScenDroid AsyncEnv instance (optional)
        
    Returns:
        Shopping login URL
    """
    return port_utils.get_shopping_login_url(env)

# For backward compatibility (will use environment variable or default)
SHOPPING_LOGIN_URL = get_shopping_login_url()


async def login_to_shopping_async(env: interface.AsyncEnv, skip_navigation: bool = False, force_restart: bool = True) -> bool:
    """Login to OneStopShop using CDP.
    
    Args:
        env: ScenDroid environment
        skip_navigation: If True, don't navigate to login page (assume already there)
        force_restart: If True (default), restart Chrome for clean login. If False,
                      try to connect to existing Chrome.
        
    Returns:
        True if login successful, False otherwise
    """
    # Get current Shopping URL dynamically (supports multi-emulator isolation)
    shopping_login_url = get_shopping_login_url(env)
    shopping_base = port_utils.get_shopping_base_url(env)
    
    cdp_manager = chrome_cdp.ChromeCDPManager(env)
    
    try:
        # Connect to Chrome (force restart for clean login state by default)
        page = await cdp_manager.connect(force_restart=force_restart)
        
        # Check current page status (WITHOUT navigating!)
        current_url = page.url
        logging.info(f"📍 Current URL: {current_url}")
        
        # Case 1: Already on account page (logged in) - no need to login
        if "customer/account" in current_url and "login" not in current_url:
            logging.info("✅ Already logged in (on account page)")
            await cdp_manager.disconnect()
            return True
        
        # Case 2: Check if login cookies exist (more reliable than URL check)
        try:
            cookies = await page.context.cookies()
            has_login_cookie = any(
                cookie.get('name') in ['login', 'customer', 'frontend'] 
                for cookie in cookies
            )
            if has_login_cookie:
                logging.info("✅ Already logged in (found login cookies)")
                await cdp_manager.disconnect()
                return True
        except Exception as cookie_error:
            logging.debug(f"Could not check cookies: {cookie_error}")
        
        # Case 3: Need to login - check if on login page
        if "customer/account/login" in current_url or "/customer/account/login" in current_url:
            logging.info("📄 On login page, will proceed to login")
        else:
            # Not on login page - need to navigate
            # But ONLY if we're on a shopping page (avoid triggering redirect)
            # Check if on any shopping domain (including different ports for multi-user)
            from urllib.parse import urlparse
            
            # Parse both current URL and shopping base URL to compare hosts
            try:
                current_parsed = urlparse(current_url)
                shopping_parsed = urlparse(shopping_base)
                
                # Check if we're on a shopping page (same host or contains 'onestopshop')
                is_shopping_page = (
                    current_parsed.hostname == shopping_parsed.hostname or
                    "onestopshop" in current_url.lower() or
                    current_url.startswith(shopping_base)
                )
                
                logging.info(f"🔍 [DEBUG] Checking if on shopping page:")
                logging.info(f"   Current URL: {current_url}")
                logging.info(f"   Current host: {current_parsed.hostname}")
                logging.info(f"   Shopping base: {shopping_base}")
                logging.info(f"   Shopping host: {shopping_parsed.hostname}")
                logging.info(f"   Is shopping page: {is_shopping_page}")
                
            except Exception as parse_error:
                logging.warning(f"⚠️ URL parsing error: {parse_error}")
                is_shopping_page = "onestopshop" in current_url.lower()
            
            if is_shopping_page:
                logging.info(f"🔄 Not on login page, navigating to: {shopping_login_url}")
                try:
                    await page.goto(shopping_login_url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(1500)
                    
                    # Check URL after navigation
                    current_url = page.url
                    logging.info(f"📍 After navigation: {current_url}")
                    
                    # If redirected to account page, already logged in
                    if "customer/account" in current_url and "login" not in current_url:
                        logging.info("✅ Already logged in (redirected after navigation)")
                        await cdp_manager.disconnect()
                        return True
                except Exception as nav_error:
                    logging.error(f"❌ Navigation failed: {nav_error}")
                    await cdp_manager.disconnect()
                    return False
            else:
                logging.warning(f"⚠️ On unexpected page: {current_url}")
                logging.warning(f"   Expected shopping host: {shopping_parsed.hostname if 'shopping_parsed' in locals() else 'unknown'}")
                await cdp_manager.disconnect()
                return False
        
        # Before filling form, do a final check if we're still on login page
        # (navigation might have changed the page)
        await page.wait_for_timeout(1000)  # Give time for any redirects
        current_url = page.url
        if "customer/account" in current_url and "login" not in current_url:
            logging.info("✅ Already logged in (detected before filling form)")
            await cdp_manager.disconnect()
            return True
        
        # Find and clear email field first (in case there's residual data)
        try:
            email_input = await page.wait_for_selector('input[name="login[username]"]', timeout=10000)
            if email_input:
                # Clear existing content
                await email_input.click(click_count=3)  # Select all
                await email_input.press('Backspace')
                # Fill new value
                await email_input.fill(SHOPPING_CREDENTIALS['username'])
                logging.info(f"✅ Filled email: {SHOPPING_CREDENTIALS['username']}")
        except Exception as e:
            logging.error(f"Error filling email: {e}")
            await cdp_manager.disconnect()
            return False
        
        # Find and clear password field
        try:
            password_input = await page.wait_for_selector('input[name="login[password]"]', timeout=5000)
            if password_input:
                # Clear existing content
                await password_input.click(click_count=3)  # Select all
                await password_input.press('Backspace')
                # Fill new value
                await password_input.fill(SHOPPING_CREDENTIALS['password'])
                logging.info("✅ Filled password")
        except Exception as e:
            logging.error(f"Error filling password: {e}")
            await cdp_manager.disconnect()
            return False
        
        # Click sign in button
        try:
            logging.info("Clicking Sign In button...")
            # Increase timeout for click action (especially important for consecutive tests)
            await page.click('button[type="submit"].action.login.primary', timeout=15000)
            
            # Wait for navigation - use longer timeout and be more lenient
            try:
                await page.wait_for_load_state("networkidle", timeout=20000)
            except Exception as wait_error:
                logging.debug(f"Wait for networkidle timeout (may be ok): {wait_error}")
                # Even if networkidle times out, the navigation might have completed
                # We'll check the URL below
                await page.wait_for_timeout(2000)  # Wait a bit more
        except Exception as e:
            logging.warning(f"Error during sign in: {e}")
            # Continue to check if we're logged in anyway
        
        # Check if login successful
        final_url = page.url
        if "customer/account" in final_url and "login" not in final_url:
            logging.info(f"✅ Login successful! Current URL: {final_url}")
            await cdp_manager.disconnect()
            return True
        else:
            logging.warning(f"⚠️ Login may have failed. Current URL: {final_url}")
            await cdp_manager.disconnect()
            return False
            
    except Exception as e:
        logging.error(f"Error during login: {e}")
        try:
            await cdp_manager.disconnect()
        except:
            pass
        return False


def login_to_shopping(env: interface.AsyncEnv, force_restart: bool = True) -> bool:
    """Synchronous wrapper for login_to_shopping_async.
    
    Args:
        env: ScenDroid environment
        force_restart: If True (default), restart Chrome for clean login. If False,
                      try to connect to existing Chrome (useful when Chrome is already
                      opened via home screen shortcut).
        
    Returns:
        True if login successful, False otherwise
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(login_to_shopping_async(env, force_restart=force_restart))
    finally:
        loop.close()


async def check_login_status_async(env: interface.AsyncEnv) -> bool:
    """Check if currently logged in to OneStopShop.
    
    Args:
        env: ScenDroid environment
        
    Returns:
        True if logged in, False otherwise
    """
    cdp_manager = chrome_cdp.ChromeCDPManager(env)
    
    try:
        page = await cdp_manager.connect()
        current_url = page.url
        
        # Simple check: if we're on a customer account page (not login), we're logged in
        logged_in = "customer/account" in current_url and "login" not in current_url
        
        if logged_in:
            logging.info(f"✅ Logged in. Current URL: {current_url}")
        else:
            logging.info(f"❌ Not logged in. Current URL: {current_url}")
        
        return logged_in
        
    except Exception as e:
        logging.warning(f"Error checking login status: {e}")
        return False
    
    finally:
        await cdp_manager.disconnect()


def check_login_status(env: interface.AsyncEnv) -> bool:
    """Synchronous wrapper for check_login_status_async."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(check_login_status_async(env))
    finally:
        loop.close()

