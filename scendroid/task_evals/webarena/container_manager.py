"""Container rebuild management module

Used to rebuild the OneStopShop container and restore it to its initial status after task execution.
Uses the container rebuild strategy (approximately 2 minutes), replacing snapshot restoration (approximately 5 minutes).
"""

import logging
import os
import re
import subprocess
import time
import traceback
from typing import Optional


class ShoppingContainerManager:
    """Manages the rebuilding of the OneStopShop container and restoration of its status"""
    
    # Class-level rebuild cooldown mechanism (shared across all instances to avoid duplicate rebuilds among different instances)
    _last_rebuild_times = {}  # {container_name: timestamp}
    _rebuild_cooldown = 5.0  # 5-second cooldown period
    
    def __init__(self, console_port: Optional[int] = None):
        """initializecontainermanager
        
        Args:
            console_port: Emulator console port (e.g., 5554, 5556)
                         Used to distinguish container instances for different emulators
                         If not provided, uses the default shopping container
        """
        # Create an independent container instance based on the console_port
        if console_port and console_port != 5554:
            # Create an independent container for non-default ports
            self.docker_container = f"shopping_{console_port}"
            self.host_port = 7770 + (console_port - 5554)  # 7770, 7772, 7774...
        else:
            # Default container (for backward compatibility)
            self.docker_container = "shopping"
            self.host_port = 7770
        
        self.docker_image = "shopping_final_0712"
        self.db_user = "magentouser"
        self.db_password = "MyPassword"
        self.db_name = "magentodb"
        self.console_port = console_port
        
        # Detect whether sudo is required
        self.docker_cmd = self._get_docker_cmd()
        
        logging.info(f"🛒 Shopping Container Manager initialized:")
        logging.info(f"   Container: {self.docker_container}")
        logging.info(f"   Host Port: {self.host_port}")
        logging.info(f"   Emulator Port: {console_port or 'default'}")
        
        if not self.docker_cmd:
            logging.warning(f"   ❌ Docker: NOT AVAILABLE")
    
    def _get_docker_cmd(self) -> list:
        """Get the Docker command prefix (may include sudo)
        
        Returns:
            ['docker'] or ['/usr/bin/docker'] or ['sudo', 'docker'] or None (unavailable)
        """
        # Common Docker paths
        docker_paths = [
            'docker',              # In PATH
            '/usr/bin/docker',     # Most common Linux path
            '/usr/local/bin/docker',  # Another common path
        ]
        
        errors = []  # Collect error information for diagnosis
        
        # Method 1: Attempt Docker at various paths (without sudo)
        for docker_path in docker_paths:
            try:
                result = subprocess.run(
                    [docker_path, 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return [docker_path]
                else:
                    # Log the error, but if it is a permission issue, continue attempting with sudo
                    error_msg = f"{docker_path}: exit code {result.returncode}, stderr: {result.stderr[:100]}"
                    errors.append(error_msg)
                    # Detect whether it is a permission issue
                    if 'permission denied' in result.stderr.lower():
                        logging.debug(f"⚠️  {docker_path} has permission issue, will try sudo")
            except FileNotFoundError as e:
                errors.append(f"{docker_path}: not found")
            except subprocess.TimeoutExpired:
                errors.append(f"{docker_path}: timeout")
            except Exception as e:
                errors.append(f"{docker_path}: {type(e).__name__}: {str(e)[:100]}")
        
        # Method 2: Attempt using sudo (may have cached credentials)
        for docker_path in docker_paths:
            try:
                # First attempt with -n (no password), then fall back to regular sudo if it fails
                result = subprocess.run(
                    ['sudo', '-n', docker_path, 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logging.info(f"⚠️  Docker requires sudo (passwordless)")
                    return ['sudo', docker_path]
                
                # If the -n attempt fails, attempt regular sudo (may have cached credentials)
                result = subprocess.run(
                    ['sudo', docker_path, 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=3,  # Short timeout
                    input='\n'  # If a password is required, send newline immediately (will fail but won't hang)
                )
                if result.returncode == 0:
                    logging.info(f"⚠️  Docker requires sudo (with cached credentials)")
                    return ['sudo', docker_path]
                else:
                    errors.append(f"sudo {docker_path}: exit code {result.returncode}")
            except FileNotFoundError:
                errors.append(f"sudo {docker_path}: not found")
            except subprocess.TimeoutExpired:
                errors.append(f"sudo {docker_path}: timeout")
            except Exception as e:
                errors.append(f"sudo {docker_path}: {type(e).__name__}: {str(e)[:100]}")
        
        # Docker is unavailable—output detailed error information
        logging.warning("❌ Docker is not available")
        logging.warning("🔍 Attempted docker paths:")
        for error in errors[:5]:  # Show only the first five errors
            logging.warning(f"   - {error}")
        logging.warning("💡 Try: sudo usermod -aG docker $USER && newgrp docker")
        return None
        
    def is_docker_available(self) -> bool:
        """Check whether Docker is available"""
        return self.docker_cmd is not None
    
    def _run_docker_cmd(self, docker_args: list, **kwargs) -> subprocess.CompletedProcess:
        """Run a Docker command (automatically handle sudo)
        
        Args:
            docker_args: Docker command parameters (excluding 'docker' itself)
            **kwargs: Other parameters for subprocess.run
        
        Returns:
            subprocess.CompletedProcess
        """
        if not self.docker_cmd:
            raise RuntimeError("Docker not available")
        
        cmd = self.docker_cmd + docker_args
        return subprocess.run(cmd, **kwargs)
    
    def is_container_running(self) -> bool:
        """Check whether the shopping container is running"""
        if not self.is_docker_available():
            return False
        try:
            result = self._run_docker_cmd(
                ['ps', '--filter', f'name={self.docker_container}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.docker_container in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def container_exists(self) -> bool:
        """Check whether the container exists (running or stopped)"""
        if not self.is_docker_available():
            return False
        try:
            result = self._run_docker_cmd(
                ['ps', '-a', '--filter', f'name={self.docker_container}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.docker_container in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def create_container_if_not_exists(self) -> bool:
        """Create the container if it does not exist
        
        Returns:
            returns True on success, False on failure
        """
        if not self.is_docker_available():
            logging.warning("Docker is unavailable; skip container creation")
            return False
        
        # If the container already exists and is running, no need to create it
        if self.is_container_running():
            logging.info(f"✅ Container {self.docker_container} is already running on port {self.host_port}")
            return True
        
        # If the container exists but is not running, delete it first and then rebuild
        if self.container_exists():
            logging.info(f"⚠️  Container {self.docker_container} exists but not running, will recreate")
            logging.info(f"📞 Triggered by the call stack shown above")
            self._run_docker_cmd(
                ['rm', '-f', self.docker_container],
                capture_output=True,
                timeout=10
            )
        
        try:
            logging.info(f"🔨 Creating new container: {self.docker_container} on port {self.host_port}")
            print(f"\n🔨 Creating Shopping container for emulator-{self.console_port}...", flush=True)
            print(f"   Container: {self.docker_container}", flush=True)
            print(f"   Port: {self.host_port}:80", flush=True)
            
            start_time = time.time()
            
            # Create and start the container
            result = self._run_docker_cmd(
                ['run', '--name', self.docker_container, 
                 '-p', f'{self.host_port}:80', '-d', self.docker_image],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.error(f"Container creation failed: {result.stderr}")
                print(f"   ❌ Failed to create container: {result.stderr[:200]}", flush=True)
                return False
            
            print(f"   ✅ Container created, waiting for services to start...", flush=True)
            
            # etc. Wait for the container to start
            time.sleep(60)
            
            # configurationbase_url
            print(f"   🔧 Configuring Magento base_url...", flush=True)
            host_ip = self._get_host_ip()
            
            # update base_url
            self._run_docker_cmd(
                ['exec', self.docker_container,
                 'mysql', '-u', self.db_user, f'-p{self.db_password}',
                 self.db_name, '-e',
                 f"UPDATE core_config_data SET value='http://{host_ip}:{self.host_port}/' "
                 f"WHERE path IN ('web/unsecure/base_url','web/secure/base_url');"],
                capture_output=True,
                timeout=10
            )
            
            # refreshcache
            self._run_docker_cmd(
                ['exec', self.docker_container,
                 '/var/www/magento2/bin/magento', 'cache:flush'],
                capture_output=True,
                timeout=30
            )
            
            # Restart the web service
            self._run_docker_cmd(
                ['exec', self.docker_container,
                 'supervisorctl', 'restart', 'nginx', 'php-fpm'],
                capture_output=True,
                timeout=30
            )
            
            elapsed = time.time() - start_time
            print(f"   ✅ Container ready! (took {elapsed:.1f}s)", flush=True)
            print(f"   🌐 Shopping URL: http://{host_ip}:{self.host_port}/", flush=True)
            
            logging.info(f"✅ Container {self.docker_container} created and configured successfully")
            return True
            
        except Exception as e:
            logging.error(f"Container creation failed: {e}")
            print(f"   ❌ Error: {e}", flush=True)
            import traceback
            logging.error(traceback.format_exc())
            return False
    
    def _get_host_ip(self) -> str:
        """Get the host IP address
        
        Priority order:
        1. Parse from the environment variable SHOPPING
        2. Automatically get using hostname -I
        3. Attempt other methods
        """
        from urllib.parse import urlparse
        import socket
        
        # Method 1: Parse the IP address from the environment variable SHOPPING
        shopping_url = os.environ.get('SHOPPING', '')
        if shopping_url:
            try:
                parsed = urlparse(shopping_url)
                if parsed.hostname:
                    logging.info(f"📍 [Method 1] Got host IP address from environment variable SHOPPING: {parsed.hostname}")
                    return parsed.hostname
            except Exception as e:
                logging.warning(f"⚠️  [Method 1] Failed to parse from environment variable: {e}")
        else:
            logging.info(f"⚠️  [Method 1] Environment variable SHOPPING is not set up")
        
        # Method 2: Use hostname -I
        try:
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                ip = result.stdout.strip().split()[0]
                logging.info(f"📍 [Method 2] Got host IP address using hostname -I: {ip}")
                return ip
            else:
                logging.warning(f"⚠️  [Method 2] hostname -I failed: returncode={result.returncode}, stdout='{result.stdout}'")
        except Exception as e:
            logging.warning(f"⚠️  [Method 2] hostname -I exception: {e}")
        
        # Method 3: Attempt to read from the network interface
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            logging.info(f"📍 [Method 3] Got host IP address using socket: {ip}")
            return ip
        except Exception as e:
            logging.warning(f"⚠️  [Method 3] socket methodfailed: {e}")
        
        # Final default value
        logging.warning(f"❌ All methods failed; using default value localhost")
        logging.warning(f"💡 Suggestion: First run './init_shopping_environment.sh -e 5554' in the same shell")
        return "localhost"
    
    def rebuild_container(self) -> bool:
        """Completely rebuild the container (delete and recreate)
        
        This is the fastest status restoration method (~2 minutes)
        
        Returns:
            returns True on success, False on failure
        """
        # ⏱️  Cooldown check: Avoid repeated rebuilds within a short time (using class variable, shared across all instances)
        now = time.time()
        last_rebuild = self._last_rebuild_times.get(self.docker_container, 0.0)
        time_since_last_rebuild = now - last_rebuild
        
        if last_rebuild > 0 and time_since_last_rebuild < self._rebuild_cooldown:
            logging.info(f"⏱️  Skipping container rebuild: Only {time_since_last_rebuild:.1f} seconds since last rebuild (cooldown period: {self._rebuild_cooldown} seconds)")
            print(f"⏱️  Skipping container rebuild (only {time_since_last_rebuild:.1f} seconds since last)", flush=True)
            return True  # Return True because the container is already in a clean state
        
        if not self.is_docker_available():
            logging.warning("Docker is unavailable; skipping container rebuild")
            print("⚠️  Docker is unavailable (possibly running on a local Mac)", flush=True)
            return False
        
        try:
            logging.info("startrebuildcontainer...")
            print(f"\n🔄 Rebuilding container (restoring initial state)...", flush=True)
            
            start_time = time.time()
            
            # step1: stopcontainer
            print(f"   1/6 stopcontainer...", flush=True)
            self._run_docker_cmd(
                ['stop', self.docker_container],
                capture_output=True,
                timeout=30
            )
            
            # step2: deletecontainer
            print(f"   2/6 deletecontainer...", flush=True)
            self._run_docker_cmd(
                ['rm', self.docker_container],
                capture_output=True,
                timeout=10
            )
            
            # Step 3: Create a new container
            print(f"   3/6 Creating new container...", flush=True)
            result = self._run_docker_cmd(
                ['run', '--name', self.docker_container, 
                 '-p', f'{self.host_port}:80', '-d', self.docker_image],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.error(f"containercreatefailed: {result.stderr}")
                print(f"   ❌ containercreatefailed: {result.stderr[:200]}", flush=True)
                return False
            
            # Step 4: etc. Wait for the container to start
            print(f"   4/6 Waiting for container to start (60 seconds)...", flush=True)
            time.sleep(60)
            
            # step5: configurationbase_url
            print(f"   5/6 configurationMagento base_url...", flush=True)
            host_ip = self._get_host_ip()
            
            # update base_url
            self._run_docker_cmd([
                'exec', self.docker_container,
                'mysql', '-u', self.db_user, f'-p{self.db_password}', self.db_name, '-e',
                f"UPDATE core_config_data SET value='http://{host_ip}:{self.host_port}/' WHERE path IN ('web/unsecure/base_url','web/secure/base_url');"
            ], capture_output=True, timeout=30)
            
            # Disable forced HTTPS
            self._run_docker_cmd([
                'exec', self.docker_container,
                'mysql', '-u', self.db_user, f'-p{self.db_password}', self.db_name, '-e',
                "UPDATE core_config_data SET value='0' WHERE path IN ('web/secure/use_in_frontend','web/secure/use_in_adminhtml');"
            ], capture_output=True, timeout=30)
            
            # Remove cookie_domain restrictions
            self._run_docker_cmd([
                'exec', self.docker_container,
                'mysql', '-u', self.db_user, f'-p{self.db_password}', self.db_name, '-e',
                "DELETE FROM core_config_data WHERE path='web/cookie/cookie_domain';"
            ], capture_output=True, timeout=30)
            
            # Step 6: Refresh cache and restart services
            print(f"   6/6 refreshcache...", flush=True)
            self._run_docker_cmd([
                'exec', self.docker_container,
                '/var/www/magento2/bin/magento', 'cache:flush'
            ], capture_output=True, timeout=60)
            
            self._run_docker_cmd([
                'exec', self.docker_container,
                'supervisorctl', 'restart', 'nginx', 'php-fpm'
            ], capture_output=True, timeout=30)
            
            elapsed = time.time() - start_time
            
            # Update the last rebuild time (class variable, shared across all instances)
            self._last_rebuild_times[self.docker_container] = time.time()
            
            logging.info(f"Container rebuild succeeded (took: {elapsed:.1f} seconds)")
            print(f"✅ Container rebuild succeeded (took: {elapsed:.1f} seconds, ~{elapsed/60:.1f} minutes)", flush=True)
            print(f"   Access address: http://{host_ip}:{self.host_port}/", flush=True)
            return True
            
        except subprocess.TimeoutExpired:
            logging.error("containerrebuildtimeout")
            print(f"❌ containerrebuildtimeout", flush=True)
            return False
        except Exception as e:
            logging.error(f"container rebuild failed: {e}")
            print(f"❌ container rebuild failed: {e}", flush=True)
            return False
    
    def task_modifies_state(self, task_intent: str, task_eval_types: list = None) -> bool:
        """Judge whether the task will modify the system state
        
        Args:
            task_intent: task goal description
            task_eval_types: evaluation type list (optional)
            
        Returns:
            Return True if the task modifies the status; otherwise, return False
        """
        # Keywords that modify the status (including multiple variants)
        modifying_keywords = [
            # Purchase-related
            'buy', 'purchase', 'order', 'place order', 'place an order',
            
            # Add to shopping cart/favorites
            'add to cart', 'add to the cart', 'add to my cart',
            'add to wishlist', 'add to wish list', 'add to my wishlist', 'add to my wish list',
            'add a', 'add an',  # "add a product" etc.
            
            # Review
            'add review', 'write review', 'post review', 'leave review',
            
            # cancel/delete
            'cancel', 'delete', 'remove', 'clear',
            
            # Modify
            'change', 'update', 'modify', 'edit',
            
            # Checkout
            'checkout', 'pay', 'payment', 'complete purchase'
        ]
        
        # Normalize: remove extra whitespace and convert to lowercase
        intent_normalized = ' '.join(task_intent.lower().split())
        
        # Check keywords
        for keyword in modifying_keywords:
            if keyword in intent_normalized:
                return True
        
        # Additional check: if eval_type includes program_html, it is more likely to modify the status
        # Because such tasks typically involve form submission, operations, etc.
        if task_eval_types and 'program_html' in task_eval_types:
            # Check whether action verbs are included
            action_verbs = ['add', 'remove', 'delete', 'create', 'submit', 'send', 'post', 'cancel']
            for verb in action_verbs:
                if verb in intent_normalized:
                    return True
        
        return False


# Global singleton
_container_manager: Optional[ShoppingContainerManager] = None


def get_container_manager() -> ShoppingContainerManager:
    """Get the global container manager instance"""
    global _container_manager
    if _container_manager is None:
        _container_manager = ShoppingContainerManager()
    return _container_manager


# Provide an alias for backward compatibility with legacy code
ShoppingSnapshotManager = ShoppingContainerManager
get_snapshot_manager = get_container_manager

