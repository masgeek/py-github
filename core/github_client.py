# File: github_client.py
"""GitHub API client for organization management."""

import time
from typing import Optional, Dict, Any, List
import requests
from loguru import logger

from core.dto import RepositoryConfig

GITHUB_API_BASE = "https://api.github.com"


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


class GitHubClient:
    """Client for interacting with the GitHub API."""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Pause if rate limit is reached."""
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_seconds = max(reset - int(time.time()), 0)
            logger.warning(f"Rate limit exceeded. Sleeping for {wait_seconds} seconds.")
            time.sleep(wait_seconds + 1)

    def _safe_json(self, response: requests.Response) -> Dict[str, Any]:
        """Safely parse JSON response."""
        try:
            return response.json()
        except ValueError:
            logger.error("Invalid JSON in GitHub API response.")
            return {}

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Execute HTTP request with retry and error handling."""
        kwargs.setdefault("timeout", 10)
        kwargs.setdefault("headers", self.headers)

        try:
            resp = requests.request(method, url, **kwargs)
            self._handle_rate_limit(resp)
            return resp
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e

    def get_user_id(self, username: str) -> Optional[int]:
        """Resolve GitHub username to user ID."""
        url = f"{GITHUB_API_BASE}/users/{username}"
        resp = self._request("GET", url)
        data = self._safe_json(resp)

        if resp.status_code == 200:
            return data.get("id")
        if resp.status_code == 404:
            logger.warning(f"User '{username}' not found.")
        else:
            logger.warning(f"Could not resolve '{username}': {resp.status_code}")
        return None

    def invite_user(self, org: str, identifier: str) -> bool:
        """Invite a GitHub user (by username or email) to an organization."""
        url = f"{GITHUB_API_BASE}/orgs/{org}/invitations"
        payload: Dict[str, Any] = {"role": "direct_member"}

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
                logger.debug(f"Fallback to email invitation for: {identifier}")

        resp = self._request("POST", url, json=payload)
        data = self._safe_json(resp)

        if resp.status_code in (201, 202):
            logger.success(f"Invited: {identifier}")
            return True

        msg = data.get("message", "")
        if resp.status_code == 422 and "already a member" in msg.lower():
            logger.info(f"{identifier} is already a member.")
            return True

        logger.error(f"Failed to invite {identifier}: {msg or resp.status_code}")
        return False

    def add_to_team(self, org: str, team_slug: str, username: str) -> bool:
        """Add a user to a team."""
        url = f"{GITHUB_API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
        resp = self._request("PUT", url, json={"role": "member"})
        data = self._safe_json(resp)

        if resp.status_code in (200, 201):
            logger.info(f"Added {username} to team '{team_slug}'.")
            return True

        logger.warning(f"Could not add {username} to team '{team_slug}': {data.get('message', resp.status_code)}")
        return False

    def create_repository(self, org: str, config: RepositoryConfig) -> bool:
        """Create a repository under an organization."""
        url = f"{GITHUB_API_BASE}/orgs/{org}/repos"
        payload: Dict[str, Any] = {
            "name": config.name,
            "private": config.private,
            "auto_init": config.auto_init,
        }

        optional_fields = {
            "description": config.description,
            "gitignore_template": config.gitignore_template,
            "license_template": config.license_template,
        }
        payload.update({k: v for k, v in optional_fields.items() if v})

        resp = self._request("POST", url, json=payload)
        data = self._safe_json(resp)
        msg = data.get("message", "")

        if resp.status_code == 201:
            repo_url = data.get("html_url", "")
            logger.success(f"Created repository '{config.name}' → {repo_url}")
            return True
        if resp.status_code == 422 and "already exists" in msg.lower():
            logger.info(f"Repository '{config.name}' already exists.")
            return True

        logger.error(f"Failed to create '{config.name}': {msg or resp.status_code}")
        return False

    def fetch_tags(self, repo: str, disallowed_exts: Optional[List[str]] = None) -> Optional[str]:
        """Fetch the latest release tag and validate asset extensions."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/releases/latest"
        resp = self._request("GET", url)

        if resp.status_code != 200:
            logger.error(f"Failed to fetch release for {repo}: {resp.status_code}")
            return None

        release = self._safe_json(resp)
        tag = release.get("tag_name")
        assets = [a.get("name", "") for a in release.get("assets", [])]

        if disallowed_exts:
            for name in assets:
                if any(name.endswith(ext) for ext in disallowed_exts):
                    logger.error(f"Disallowed asset found in release {tag}: {name}")
        return tag
