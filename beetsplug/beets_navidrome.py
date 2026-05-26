"""
Beets Plugin for Navidrome
"""

from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets import config
from confuse import ConfigError
import requests
import json
import hashlib
import random
import string


class BeetsNavidromePlugin(BeetsPlugin):
    name = "beets_navidrome"

    def __init__(self):
        super(BeetsNavidromePlugin, self).__init__()

        # Default plugin configuration
        config["beets_navidrome"].add(
            {
                "host": "localhost",
                "port": "4533",
                "secure": False,
                "username": "admin",
                "password": "admin",
                "api_version": "1.16.1",
            }
        )
        
        self.host = config["beets_navidrome"]["host"].as_str()
        self.port = config["beets_navidrome"]["port"].as_str()
        self.username = config["beets_navidrome"]["username"].as_str()
        self.password = config["beets_navidrome"]["password"].as_str()
        self.api_version = config["beets_navidrome"]["api_version"].as_str()
        
        if config["beets_navidrome"]["secure"].get():
            self.proto = "https"
        else:
            self.proto = "http"
            
        self.base_url = f"{self.proto}://{self.host}:{self.port}/rest"
        self.register_listener("import", self._rescan_library)
        

    def commands(self):
        """
        Function to hold command definitions
        """
        # Initiate a Navidrome Library Scan
        rescan_library_cmd = Subcommand(
            "navrescan", help="Issue a startScan command to Navidrome"
        )

        def rescan_library(lib, opts, args):
            self._rescan_library()

        rescan_library_cmd.func = rescan_library

        # Print if Navidrome is currently running a scan
        scan_status_cmd = Subcommand("navstatus", help="Is Navidrome currently scanning?")

        def scan_status(lib, opts, args):
            self._scan_status()

        scan_status_cmd.func = scan_status

        return [rescan_library_cmd, scan_status_cmd]

    def _generate_salt(self, length=8):
        """
        Generate a random salt for authentication
        """
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def _get_auth_params(self):
        """
        Generate authentication parameters for Subsonic API
        Using token-based authentication as described in Subsonic API
        As far as I know we have to use md5
        """
        salt = self._generate_salt()
        token = hashlib.md5((self.password + salt).encode()).hexdigest()
        
        return {
            "u": self.username,
            "t": token,
            "s": salt,
            "v": self.api_version,
            "c": "beets",
            "f": "json"
        }

    def _rescan_library(self, **kwargs):
        """
        Trigger a rescan in Navidrome
        """
        if self.is_currently_scanning():
            self._log.info("Navidrome library scan already in progress. Skipping rescan.")
        else:
            self.trigger_rescan()

    def _scan_status(self):
        """
        Check and display the current scanning status
        """
        status = self.get_scan_status()
        if status.get("scanning", False):
            self._log.info(f"Navidrome scan in progress: {status.get('count', 0)} items processed")
        else:
            last_scan = status.get('lastScan', 'unknown')
            self._log.info(f"Navidrome not currently scanning. Last scan: {last_scan}")

    def get_scan_status(self):
        """
        Get the current scanning status from Navidrome using the Subsonic API
        """
        url = f"{self.base_url}/getScanStatus"
        params = self._get_auth_params()
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if "subsonic-response" in result and result["subsonic-response"]["status"] == "ok":
                return result["subsonic-response"]["scanStatus"]
            else:
                error = result.get("subsonic-response", {}).get("error", {}).get("message", "Unknown error")
                self._log.error(f"Error getting scan status: {error}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self._log.error(f"Failed to check scan status: {e}")
            return {}

    def is_currently_scanning(self):
        """
        Returns true if Navidrome is currently scanning the library
        """
        status = self.get_scan_status()
        return status.get("scanning", False)

    def trigger_rescan(self):
        """
        Initiates a rescan of the Navidrome library using the Subsonic API
        """
        url = f"{self.base_url}/startScan"
        params = self._get_auth_params()
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if "subsonic-response" in result and result["subsonic-response"]["status"] == "ok":
                self._log.info(f"Navidrome scan triggered successfully.")
                return True
            else:
                error = result.get("subsonic-response", {}).get("error", {}).get("message", "Unknown error")
                self._log.error(f"Error triggering scan: {error}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._log.error(f"Failed to trigger Navidrome scan: {e}")
            return False
