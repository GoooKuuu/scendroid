"""Database snapshot management module

Automatically saves and restores the OneStopShop database status before and after task execution.
"""

import logging
import subprocess
import os
import time
from typing import Optional


class ShoppingSnapshotManager:
    """Manages OneStopShop container rebuild and status restoration
    
    Uses the container rebuild strategy (faster: 2 minutes vs. snapshot restore taking 5 minutes)
    """
    
    def __init__(self, snapshot_file: str = "shopping_snapshot.sql", console_port: Optional[int] = None):
        """initializemanager
        
        Args:
            snapshot_file: Snapshot file path (retained for backward compatibility with legacy code but not used)
            console_port: Emulator console port (e.g., 5554, 5556)
                         Used to distinguish container instances across different emulators
        """
        self.snapshot_file = snapshot_file  # Retained for compatibility
        
        # Create an independent container instance based on console_port
        if console_port and console_port != 5554:
            # Create an independent container for non-default ports
            self.docker_container = f"shopping_{console_port}"
            self.host_port = 7770 + (console_port - 5554)  # 7770, 7772, 7774...
        else:
            # Default container (backward compatible)
            self.docker_container = "shopping"
            self.host_port = 7770
        
        self.docker_image = "shopping_final_0712"
        self.db_user = "magentouser"
        self.db_password = "MyPassword"
        self.db_name = "magentodb"
        self.console_port = console_port
        
    def is_docker_available(self) -> bool:
        """Check whether Docker is available"""
        try:
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def is_container_running(self) -> bool:
        """Check whether the shopping container is running"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.docker_container}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.docker_container in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def create_snapshot(self, force: bool = False) -> bool:
        """Empty method: Snapshots are no longer used; retained for backward compatibility with legacy code
        
        Args:
            force: Retained parameter for backward compatibility
            
        Returns:
            Always returns True
        """
        logging.info("Using container rebuild strategy; not creating snapshots")
        return True
    
    def restore_snapshot(self) -> bool:
        """Restore database snapshot
        
        Returns:
            returns True on success, False on failure
        """
        if not self.is_docker_available():
            logging.warning("Docker is unavailable; skipping snapshot restore")
            return False
        
        if not self.is_container_running():
            logging.warning(f"Container {self.docker_container} is not running; skipping snapshot restore")
            return False
        
        if not os.path.exists(self.snapshot_file):
            logging.error(f"Snapshot file does not exist: {self.snapshot_file}")
            print(f"❌ Snapshot file does not exist: {self.snapshot_file}", flush=True)
            return False
        
        try:
            # Get snapshot file size, used to estimate timeout duration
            file_size_mb = os.path.getsize(self.snapshot_file) / (1024 * 1024)
            # Dynamically set timeout based on file size (empirically: ~2 seconds per 10 MB; minimum 120 seconds, maximum 600 seconds)
            restore_timeout = min(600, max(120, int(file_size_mb / 10 * 2)))
            
            logging.info(f"Restoring database snapshot: {self.snapshot_file} ({file_size_mb:.2f} MB)")
            
            # Check whether snapshot is too large
            if file_size_mb > self.SNAPSHOT_SIZE_THRESHOLD:
                print(f"⚠️  Snapshot file is too large: {file_size_mb:.2f} MB", flush=True)
                print(f"💡 Suggestion: Rebuilding the container may be faster (approximately 2 minutes vs. estimated {restore_timeout//60} minutes)", flush=True)
                print(f"   Run: ./init_shopping_environment.sh", flush=True)
            
            estimated_min = restore_timeout // 60
            if estimated_min > 0:
                print(f"🔄 Restoring database snapshot... (size: {file_size_mb:.2f} MB, estimated duration ~ {estimated_min} minutes)", flush=True)
            else:
                print(f"🔄 Restoring database snapshot... (size: {file_size_mb:.2f} MB)", flush=True)
            
            # restoredatabase
            cmd = [
                'docker', 'exec', '-i', self.docker_container,
                'mysql',
                '-u', self.db_user,
                f'-p{self.db_password}',
                self.db_name
            ]
            
            start_time = time.time()
            
            with open(self.snapshot_file, 'r') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=restore_timeout
                )
            
            elapsed = time.time() - start_time
            
            if result.returncode != 0:
                logging.error(f"databaserestorefailed: {result.stderr}")
                print(f"❌ databaserestorefailed: {result.stderr[:200]}", flush=True)
                return False
            
            # Clear Magenta cache
            logging.info("Clearing Magenta cache")
            print(f"🧹 Clearing cache...", flush=True)
            cache_cmd = [
                'docker', 'exec', self.docker_container,
                '/var/www/magento2/bin/magento', 'cache:flush'
            ]
            
            subprocess.run(
                cache_cmd,
                capture_output=True,
                timeout=60  # Cache clearing takes at most 60 seconds
            )
            
            logging.info(f"Snapshot restore succeeded (took {elapsed:.1f} seconds)")
            print(f"✅ Database restore succeeded (took {elapsed:.1f} seconds)", flush=True)
            return True
            
        except subprocess.TimeoutExpired:
            logging.error(f"Snapshot restore timed out (exceeded {restore_timeout} seconds)")
            print(f"❌ Snapshot restore timed out (exceeded {restore_timeout} seconds)", flush=True)
            print(f"💡 Tip: The snapshot file may be too large ({file_size_mb:.2f} MB); consider optimizing the database or increasing the timeout", flush=True)
            return False
        except Exception as e:
            logging.error(f"Snapshot restore failed: {e}")
            print(f"❌ Snapshot restore failed: {e}", flush=True)
            return False
    
    def rebuild_container(self) -> bool:
        """Completely rebuild the container (delete and recreate)
        
        This is faster than snapshot restore (approximately 2 minutes vs. 5 minutes)
        
        Returns:
            returns True on success, False on failure
        """
        if not self.is_docker_available():
            logging.warning("Docker is unavailable, skipping container rebuild")
            return False
        
        try:
            logging.info("startrebuildcontainer...")
            print(f"\n🔄 Rebuilding container (faster than snapshot restore)...", flush=True)
            
            start_time = time.time()
            
            # step1: stopcontainer
            print(f"   1/5 stopcontainer...", flush=True)
            subprocess.run(
                ['docker', 'stop', self.docker_container],
                capture_output=True,
                timeout=30
            )
            
            # step2: deletecontainer
            print(f"   2/5 deletecontainer...", flush=True)
            subprocess.run(
                ['docker', 'rm', self.docker_container],
                capture_output=True,
                timeout=10
            )
            
            # Step 3: Create a new container
            print(f"   3/5 Creating new container...", flush=True)
            result = subprocess.run(
                ['docker', 'run', '--name', self.docker_container, 
                 '-p', f'{self.host_port}:80', '-d', self.docker_image],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.error(f"containercreatefailed: {result.stderr}")
                print(f"   ❌ Container creation failed", flush=True)
                return False
            
            # Step 4: etc. Wait for container to start
            print(f"   4/5 etc. Waiting for container to start (60 seconds)...", flush=True)
            time.sleep(60)
            
            # step5: configurationbase_url
            print(f"   5/5 configurationbase_url...", flush=True)
            if not self._configure_base_url():
                print(f"   ⚠️  Base URL configuration failed (manual configuration may be required)", flush=True)
            
            elapsed = time.time() - start_time
            
            logging.info(f"Container rebuild succeeded (time elapsed: {elapsed:.1f} seconds)")
            print(f"\n✅ Container rebuild complete (time elapsed: {elapsed:.1f} seconds)", flush=True)
            return True
            
        except subprocess.TimeoutExpired:
            logging.error("containerrebuildtimeout")
            print(f"❌ containerrebuildtimeout", flush=True)
            return False
        except Exception as e:
            logging.error(f"container rebuild failed: {e}")
            print(f"❌ container rebuild failed: {e}", flush=True)
            return False
    
    def _configure_base_url(self) -> bool:
        """configurationMagento base_url
        
        Returns:
            returns True on success, False on failure
        """
        try:
            # Get host IP
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                host_ip = result.stdout.strip().split()[0]
            else:
                host_ip = "localhost"  # default value
            
            port = self.host_port  # Use dynamically assigned port
            
            # 1. updatebase_url
            subprocess.run(
                ['docker', 'exec', self.docker_container,
                 'mysql', '-u', self.db_user, f'-p{self.db_password}',
                 self.db_name, '-e',
                 f"UPDATE core_config_data SET value='http://{host_ip}:{port}/' "
                 f"WHERE path IN ('web/unsecure/base_url','web/secure/base_url');"],
                capture_output=True,
                timeout=10
            )
            
            # 2. disabledHTTPS
            subprocess.run(
                ['docker', 'exec', self.docker_container,
                 'mysql', '-u', self.db_user, f'-p{self.db_password}',
                 self.db_name, '-e',
                 "UPDATE core_config_data SET value='0' "
                 "WHERE path IN ('web/secure/use_in_frontend','web/secure/use_in_adminhtml');"],
                capture_output=True,
                timeout=10
            )
            
            # 3. Delete cookie restrictions
            subprocess.run(
                ['docker', 'exec', self.docker_container,
                 'mysql', '-u', self.db_user, f'-p{self.db_password}',
                 self.db_name, '-e',
                 "DELETE FROM core_config_data WHERE path='web/cookie/cookie_domain';"],
                capture_output=True,
                timeout=10
            )
            
            # 4. refreshcache
            subprocess.run(
                ['docker', 'exec', self.docker_container,
                 '/var/www/magento2/bin/magento', 'cache:flush'],
                capture_output=True,
                timeout=30
            )
            
            # 5. Restart web service
            subprocess.run(
                ['docker', 'exec', self.docker_container,
                 'supervisorctl', 'restart', 'nginx', 'php-fpm'],
                capture_output=True,
                timeout=30
            )
            
            return True
            
        except Exception as e:
            logging.error(f"base_urlconfigurationfailed: {e}")
            return False
    
    def task_modifies_state(self, task_intent: str, task_eval_types: list = None) -> bool:
        """Determine whether a task modifies the system status
        
        Args:
            task_intent: Task goal description
            task_eval_types: List of evaluation types (optional)
            
        Returns:
            Returns True if the task modifies the status; otherwise, returns False
        """
        # Keywords indicating status modification
        modifying_keywords = [
            'buy', 'purchase', 'order', 'place order',
            'add to cart', 'add to wishlist', 'add review',
            'cancel', 'delete', 'remove',
            'change', 'update', 'modify',
            'checkout', 'pay', 'payment'
        ]
        
        intent_lower = task_intent.lower()
        
        # Check whether the intent contains keywords indicating status modification
        for keyword in modifying_keywords:
            if keyword in intent_lower:
                return True
        
        # Tasks of program_html type are more likely to modify the status
        # However, some such tasks only view pages, so keywords remain the primary criterion
        
        return False


# Global singleton
_snapshot_manager: Optional[ShoppingSnapshotManager] = None


def get_snapshot_manager() -> ShoppingSnapshotManager:
    """Get the global snapshot manager instance"""
    global _snapshot_manager
    if _snapshot_manager is None:
        _snapshot_manager = ShoppingSnapshotManager()
    return _snapshot_manager
