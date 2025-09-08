"""LeetCode authentication using cookies."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import requests

# LeetCode GraphQL endpoint
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Default auth file location
DEFAULT_AUTH_FILE = Path.home() / ".leetcode-picker" / "auth.json"


class LeetCodeAuth:
    """Handles LeetCode authentication using cookies."""

    def __init__(self, auth_file: Optional[Path] = None):
        """Initialize with optional custom auth file path."""
        self.auth_file = auth_file or DEFAULT_AUTH_FILE
        self.session_cookie: Optional[str] = None
        self.csrf_token: Optional[str] = None

    def save_cookies(self, session_cookie: str, csrf_token: str) -> None:
        """Save authentication cookies to file."""
        # Ensure directory exists with restrictive permissions
        self.auth_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.auth_file.parent.chmod(0o700)
        except OSError:
            pass

        auth_data = {
            "leetcode_session": session_cookie,
            "csrf_token": csrf_token,
        }

        with open(self.auth_file, "w") as f:
            json.dump(auth_data, f, indent=2)

        # Set restrictive permissions on auth file
        os.chmod(self.auth_file, 0o600)

        self.session_cookie = session_cookie
        self.csrf_token = csrf_token

    def load_cookies(self) -> bool:
        """Load authentication cookies from file. Returns True if successful."""
        if not self.auth_file.exists():
            return False

        # Enforce restrictive permissions at load time as well
        try:
            self.auth_file.parent.chmod(0o700)
        except OSError:
            pass
        try:
            os.chmod(self.auth_file, 0o600)
        except OSError:
            pass

        try:
            with open(self.auth_file, "r") as f:
                auth_data = json.load(f)

            self.session_cookie = auth_data.get("leetcode_session")
            self.csrf_token = auth_data.get("csrf_token")

            return bool(self.session_cookie and self.csrf_token)
        except (json.JSONDecodeError, KeyError, OSError):
            return False

    def get_authenticated_session(self) -> Optional[requests.Session]:
        """Get a requests session with authentication headers."""
        if not (self.session_cookie and self.csrf_token):
            if not self.load_cookies():
                return None

        # These should be loaded now
        assert self.session_cookie is not None
        assert self.csrf_token is not None

        session = requests.Session()
        session.cookies.set(
            "LEETCODE_SESSION", self.session_cookie, domain="leetcode.com"
        )
        session.cookies.set("csrftoken", self.csrf_token, domain="leetcode.com")
        session.headers.update(
            {
                "X-CSRFToken": self.csrf_token,
                "Referer": "https://leetcode.com/",
                "Content-Type": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
            }
        )

        return session

    def test_authentication(self) -> bool:
        """Test if current authentication is working with a simple query."""
        session = self.get_authenticated_session()
        if not session:
            return False

        # Simple GraphQL query to test authentication
        query = {
            "query": """
            query currentUser {
                user {
                    username
                    firstName
                    lastName
                }
            }
            """
        }

        try:
            response = session.post(LEETCODE_GRAPHQL_URL, json=query, timeout=10)
            response.raise_for_status()

            data = response.json()
            return (
                "data" in data
                and "user" in data["data"]
                and data["data"]["user"] is not None
            )
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            return False

    def get_user_info(self) -> Optional[Dict]:
        """Get basic user information to verify auth is working."""
        session = self.get_authenticated_session()
        if not session:
            return None

        query = {
            "query": """
            query currentUser {
                user {
                    username
                    firstName
                    lastName
                    profile {
                        userAvatar
                        ranking
                    }
                }
            }
            """
        }

        try:
            response = session.post(LEETCODE_GRAPHQL_URL, json=query, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "data" in data and "user" in data["data"] and data["data"]["user"]:
                return data["data"]["user"]
            return None
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            return None
