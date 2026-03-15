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

"""WebArena authentication adapter for ScenDroid.

This module adapts WebArena's Playwright-based auto-login mechanism to work
with Android Chrome using ADB commands and UI automation.
"""

import os
import time
from absl import logging
from scendroid.env import interface
from scendroid.env import adb_utils

# OneStopShop credentials (from WebArena's env_config.py)
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


class AndroidShoppingAuthenticator:
    """Authenticator for OneStopShop on Android Chrome.
    
    This adapts WebArena's Playwright login logic to work with Android.
    The original logic (from auto_login.py):
    
    ```python
    page.goto(f"{SHOPPING}/customer/account/login/")
    page.get_by_label("Email", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign In").click()
    ```
    
    We need to translate this to ADB/UI Automator commands.
    """
    
    def __init__(self, env: interface.AsyncEnv):
        """Initialize the authenticator.
        
        Args:
            env: ScenDroid environment with controller for ADB access
        """
        self.env = env
        self.login_url = SHOPPING_LOGIN_URL
        self.credentials = SHOPPING_CREDENTIALS
    
    def is_logged_in(self) -> bool:
        """Check if already logged in to OneStopShop.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # TODO: Implement login status check
            # Options:
            # 1. Navigate to a protected page and check if redirected to login
            # 2. Check for presence of account-specific UI elements
            # 3. Look for stored cookies/session data
            
            logging.info("Checking login status...")
            # For now, always assume not logged in
            return False
            
        except Exception as e:
            logging.error(f"Error checking login status: {e}")
            return False
    
    def login(self) -> bool:
        """Login to OneStopShop using Android Chrome.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logging.info(f"Logging in to OneStopShop at {self.login_url}")
            
            # Step 1: Open login page in Chrome
            self._open_url_in_chrome(self.login_url)
            time.sleep(3)  # Wait for page to load
            
            # Step 2: Fill in email field
            success = self._fill_email_field(self.credentials["username"])
            if not success:
                logging.error("Failed to fill email field")
                return False
            
            # Step 3: Fill in password field
            success = self._fill_password_field(self.credentials["password"])
            if not success:
                logging.error("Failed to fill password field")
                return False
            
            # Step 4: Click Sign In button
            success = self._click_sign_in_button()
            if not success:
                logging.error("Failed to click Sign In button")
                return False
            
            # Step 5: Wait and verify login
            time.sleep(3)
            if self._verify_login():
                logging.info("✅ Successfully logged in to OneStopShop")
                return True
            else:
                logging.warning("⚠️ Login verification failed")
                return False
            
        except Exception as e:
            logging.error(f"Error during login: {e}")
            return False
    
    def _open_url_in_chrome(self, url: str) -> None:
        """Open URL in Android Chrome.
        
        Args:
            url: URL to open
        """
        # Method 1: Use intent to open URL
        cmd = f'adb shell am start -a android.intent.action.VIEW -d "{url}"'
        self.env.controller.execute_adb_call(cmd)
    
    def _fill_email_field(self, email: str) -> bool:
        """Fill the email field on login page.
        
        Args:
            email: Email address to fill
            
        Returns:
            True if successful
        """
        try:
            # Use UI Automator to find and fill the email field
            # Look for field with content-desc, text, or resource-id containing "email"
            
            # Method 1: Try to find by resource-id
            # Note: Cannot use backslash in f-string, so escape @ outside
            escaped_email = email.replace("@", "\\@")
            cmd = (
                f'adb shell input text "{escaped_email}" && '
                f'adb shell input keyevent 66'  # KEYCODE_ENTER or TAB
            )
            
            # TODO: Implement proper UI element finding and interaction
            # This requires:
            # 1. Dump UI hierarchy: adb shell uiautomator dump
            # 2. Parse XML to find email field
            # 3. Get bounds and tap on it
            # 4. Input text
            
            logging.warning("Email field filling not fully implemented")
            logging.info(f"Would fill email: {email}")
            return False  # Return False until implemented
            
        except Exception as e:
            logging.error(f"Error filling email field: {e}")
            return False
    
    def _fill_password_field(self, password: str) -> bool:
        """Fill the password field on login page.
        
        Args:
            password: Password to fill
            
        Returns:
            True if successful
        """
        try:
            # Similar to email field, but look for password field
            logging.warning("Password field filling not fully implemented")
            logging.info(f"Would fill password: {'*' * len(password)}")
            return False  # Return False until implemented
            
        except Exception as e:
            logging.error(f"Error filling password field: {e}")
            return False
    
    def _click_sign_in_button(self) -> bool:
        """Click the Sign In button.
        
        Returns:
            True if successful
        """
        try:
            # Find and click the "Sign In" button
            # Look for button with text "Sign In" or similar
            
            logging.warning("Sign In button click not fully implemented")
            logging.info("Would click Sign In button")
            return False  # Return False until implemented
            
        except Exception as e:
            logging.error(f"Error clicking Sign In button: {e}")
            return False
    
    def _verify_login(self) -> bool:
        """Verify that login was successful.
        
        Returns:
            True if logged in
        """
        try:
            # Check for indicators of successful login:
            # 1. URL changed from login page
            # 2. Presence of user account elements
            # 3. Absence of login form
            
            logging.warning("Login verification not fully implemented")
            return False  # Return False until implemented
            
        except Exception as e:
            logging.error(f"Error verifying login: {e}")
            return False


def ensure_shopping_login(env: interface.AsyncEnv) -> bool:
    """Ensure user is logged in to OneStopShop.
    
    This function checks if already logged in, and if not, performs login.
    
    Args:
        env: ScenDroid environment
        
    Returns:
        True if logged in (or login successful), False otherwise
    """
    authenticator = AndroidShoppingAuthenticator(env)
    
    if authenticator.is_logged_in():
        logging.info("✅ Already logged in to OneStopShop")
        return True
    
    logging.info("🔐 Not logged in, attempting login...")
    return authenticator.login()


# Alternative approach: Use saved cookies/session from WebArena
def load_shopping_cookies_from_webarena(env: interface.AsyncEnv) -> bool:
    """Load shopping cookies from WebArena's auth files.
    
    WebArena saves authentication state in .auth/shopping_state.json.
    We can try to extract cookies and inject them into Android Chrome.
    
    Args:
        env: ScenDroid environment
        
    Returns:
        True if cookies loaded successfully
    """
    try:
        import json
        import os
        
        # Path to WebArena auth file
        auth_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))),
            "webarena-main", ".auth", "shopping_state.json"
        )
        
        if not os.path.exists(auth_file):
            logging.warning(f"Auth file not found: {auth_file}")
            return False
        
        with open(auth_file, 'r') as f:
            auth_data = json.load(f)
        
        cookies = auth_data.get("cookies", [])
        
        # TODO: Inject cookies into Android Chrome
        # This is complex and requires either:
        # 1. Using Chrome DevTools Protocol
        # 2. Manually creating Chrome cookie files on Android
        # 3. Using a Chrome extension to set cookies
        
        logging.warning("Cookie injection into Android Chrome not yet implemented")
        logging.info(f"Would load {len(cookies)} cookies from WebArena")
        
        return False  # Return False until implemented
        
    except Exception as e:
        logging.error(f"Error loading cookies from WebArena: {e}")
        return False
