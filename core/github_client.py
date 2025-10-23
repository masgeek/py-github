# File: github_client.py
"""GitHub API client for organization management."""
import time
from typing import Optional
import requests
from loguru import logger

from core.dto import RepositoryConfig

GITHUB_API_BASE = "https://api.github.com"


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Check and handle rate limiting."""
        if response.status_code == 403:
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
            if rate_limit_remaining == "0":
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                wait_seconds = max(reset_time - int(time.time()), 0)
                logger.warning(f"Rate limit exceeded. Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds + 1)

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an API request with error handling."""
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('headers', self.headers)

        try:
            resp = requests.request(method, url, **kwargs)
            self._handle_rate_limit(resp)
            return resp
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}")

    def get_user_id(self, username: str) -> Optional[int]:
        """Fetch GitHub user ID from username."""
        url = f"{GITHUB_API_BASE}/users/{username}"
        resp = self._request("GET", url)

        if resp.status_code == 200:
            return resp.json().get("id")
        elif resp.status_code == 404:
            logger.warning(f"User '{username}' not found on GitHub")
        else:
            logger.warning(f"Could not resolve username '{username}': {resp.status_code}")

        return None

    def invite_user(self, org: str, identifier: str) -> bool:
        """Invite a user to the organization."""
        payload = {"role": "direct_member"}

        # Determine if identifier is email or username
        if "@" in identifier:
            payload["email"] = identifier
            logger.debug(f"Inviting by email: {identifier}")
        else:
            user_id = self.get_user_id(identifier)
            if user_id:
                payload["invitee_id"] = user_id
                logger.debug(f"Inviting by user ID: {user_id} ({identifier})")
            else:
                payload["email"] = identifier
                logger.debug(f"Falling back to email invitation: {identifier}")

        url = f"{GITHUB_API_BASE}/orgs/{org}/invitations"
        resp = self._request("POST", url, json=payload)

        if resp.status_code in (201, 202):
            logger.success(f"✓ Invited: {identifier}")
            return True
        elif resp.status_code == 422:
            msg = resp.json().get("message", "")
            if "already a member" in msg.lower():
                logger.info(f"ℹ {identifier} is already a member")
                return True
            else:
                logger.error(f"✗ Failed: {identifier} → {msg}")
                return False
        else:
            msg = resp.json().get("message", "unknown error")
            logger.error(f"✗ Failed: {identifier} → {msg}")
            return False

    def add_to_team(self, org: str, team_slug: str, username: str) -> bool:
        """Add user to a team."""
        url = f"{GITHUB_API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
        resp = self._request("PUT", url, json={"role": "member"})

        if resp.status_code in (200, 201):
            logger.info(f"✓ Added {username} to team '{team_slug}'")
            return True
        else:
            msg = resp.json().get("message", "unknown error")
            logger.warning(f"✗ Could not add {username} to team '{team_slug}': {msg}")
            return False

    def create_repository(self, org: str, config: RepositoryConfig) -> bool:
        """Create a repository in the organization."""
        url = f"{GITHUB_API_BASE}/orgs/{org}/repos"

        payload = {
            "name": config.name,
            "private": config.private,
            "auto_init": config.auto_init,
        }

        if config.description:
            payload["description"] = config.description
        if config.gitignore_template:
            payload["gitignore_template"] = config.gitignore_template
        if config.license_template:
            payload["license_template"] = config.license_template

        resp = self._request("POST", url, json=payload)

        if resp.status_code == 201:
            repo_data = resp.json()
            repo_url = repo_data.get("html_url", "")
            logger.success(f"✓ Created: {config.name} → {repo_url}")
            return True
        elif resp.status_code == 422:
            msg = resp.json().get("message", "")
            if "already exists" in msg.lower():
                logger.info(f"ℹ Repository '{config.name}' already exists")
                return True
            else:
                logger.error(f"✗ Failed to create '{config.name}': {msg}")
                return False
        else:
            msg = resp.json().get("message", "unknown error")
            logger.error(f"✗ Failed to create '{config.name}': {msg}")
            return False
