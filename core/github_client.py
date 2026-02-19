# File: github_client.py
"""GitHub API client for organization management with reliability, governance, and observability features."""

import os
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Generator
from requests import Session, Response, RequestException
from loguru import logger

from core.dto import RepositoryConfig
from core.github_issues import Issue

GITHUB_API_BASE = "https://api.github.com"


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


class GitHubClient:
    """Advanced GitHub API client."""

    def __init__(
            self,
            token: str,
            org: Optional[str] = None,
            dry_run: bool = False,
            max_retries: int = 3,
            backoff_factor: float = 1.5,
    ):
        self.token = token
        self.org = org
        self.dry_run = dry_run
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        self.session = Session()
        self.session.headers.update(self.headers)
        logger.debug(f"GitHubClient initialized for org={self.org}, dry_run={self.dry_run}")

    # =======================
    # CORE NETWORK UTILITIES
    # =======================
    def _handle_rate_limit(self, response: Response, threshold: int = 50) -> None:
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        reset_epoch = int(response.headers.get("X-RateLimit-Reset", 0))
        if remaining <= threshold:
            wait_seconds = max(reset_epoch - int(time.time()), 0)
            reset_time = datetime.fromtimestamp(wait_seconds).isoformat()
            logger.warning(
                f"Approaching rate limit (remaining={remaining})"
                f"Waiting {wait_seconds} seconds until reset at {reset_time}"
            )
            time.sleep(wait_seconds)

    def _safe_json(self, response: Response) -> Dict[str, Any]:
        try:
            return response.json()
        except ValueError:
            logger.error("Invalid JSON in GitHub API response.")
            return {}

    def _request(self, method: str, url: str, **kwargs) -> Response | None:
        """Resilient HTTP request with retries, rate-limit handling, and dry-run support."""
        if self.dry_run and method != "GET":
            logger.info(f"[DRY RUN] {method} {url} → {json.dumps(kwargs.get('json', {}), indent=2)}")
            fake = Response()
            fake.status_code = 200
            return fake

        kwargs.setdefault("timeout", 10)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.request(method, url, **kwargs)
                self._handle_rate_limit(resp)
                return resp
            except RequestException as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise GitHubAPIError(f"Request failed after {self.max_retries} retries: {e}")
                sleep_time = self.backoff_factor * attempt
                time.sleep(sleep_time)
        return None

    # =======================
    # AUTH & VALIDATION
    # =======================
    def check_auth(self) -> bool:
        """Verify that the token is valid and print authenticated user info."""
        resp = self._request("GET", f"{GITHUB_API_BASE}/user")
        if resp.status_code == 200:
            data = self._safe_json(resp)
            logger.info(f"Authenticated as {data.get('login')} (id={data.get('id')})")
            return True
        logger.error(f"Invalid or unauthorized token: {resp.status_code}")
        return False

    def validate_token_scopes(self, required_scopes: List[str]) -> bool:
        """Check whether token has the required scopes."""
        resp = self._request("GET", f"{GITHUB_API_BASE}/user")
        scopes = resp.headers.get("X-OAuth-Scopes", "")
        scopes_list = [s.strip() for s in scopes.split(",") if s]
        missing = [s for s in required_scopes if s not in scopes_list]
        if missing:
            logger.warning(f"Missing scopes: {missing}")
            return False
        logger.info(f"Token scopes validated: {scopes_list}")
        return True

    # =======================
    # PAGINATION SUPPORT
    # =======================
    def paginate(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Generator[Dict[str, Any], None, None]:
        """Yield paginated results from GitHub API."""
        url = f"{GITHUB_API_BASE}{endpoint}"
        params = params or {}
        while url:
            resp = self._request("GET", url, params=params)
            data = self._safe_json(resp)
            if isinstance(data, list):
                for item in data:
                    yield item
            url = None
            if "next" in resp.links:
                url = resp.links["next"]["url"]

    # =======================
    # CORE OPERATIONS
    # =======================
    def get_user_id(self, username: str) -> Optional[int]:
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

    def invite_user(self, org: Optional[str], identifier: str) -> bool:
        org = org or self.org
        if not org:
            raise GitHubAPIError("Organization not specified.")

        url = f"{GITHUB_API_BASE}/orgs/{org}/invitations"
        payload: Dict[str, Any] = {"role": "direct_member"}

        if "@" in identifier:
            payload["email"] = identifier
        else:
            user_id = self.get_user_id(identifier)
            payload["invitee_id"] = user_id if user_id else None
            if not user_id:
                payload["email"] = identifier

        resp = self._request("POST", url, json=payload)
        data = self._safe_json(resp)

        if resp.status_code in (201, 202):
            logger.success(f"Invited: {identifier}")
            return True
        if resp.status_code == 422 and "already a member" in data.get("message", "").lower():
            logger.info(f"{identifier} is already a member.")
            return True
        logger.error(f"Failed to invite {identifier}: {data.get('message', resp.status_code)}")
        return False

    def bulk_invite(self, org: Optional[str], identifiers: List[str]) -> None:
        for idf in identifiers:
            self.invite_user(org, idf)
            time.sleep(0.5)

    def add_to_team(self, org: Optional[str], team_slug: str, username: str) -> bool:
        org = org or self.org
        url = f"{GITHUB_API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
        resp = self._request("PUT", url, json={"role": "member"})
        if resp.status_code in (200, 201):
            logger.info(f"Added {username} to team '{team_slug}'.")
            return True
        msg = self._safe_json(resp).get("message", "")
        logger.warning(f"Could not add {username} to team '{team_slug}': {msg}")
        return False

    def create_repository(self, org: Optional[str], config: RepositoryConfig) -> bool:
        """
        Create a GitHub repository under the specified organization or the authenticated user.
        """
        if org:
            url = f"{GITHUB_API_BASE}/orgs/{org}/repos"
        else:
            url = f"{GITHUB_API_BASE}/user/repos"

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

    def branch_protection(self, repo: str, rules: Dict[str, Any]) -> bool:
        """Configure branch protection for a repo."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/branches/main/protection"
        resp = self._request("PUT", url, json=rules)
        if resp.status_code in (200, 201):
            logger.info(f"Branch protection applied for {repo}.")
            return True
        logger.error(f"Failed to apply branch protection for {repo}: {resp.status_code}")
        return False

    def audit_logs(self, org: Optional[str], per_page: int = 50) -> List[Dict[str, Any]]:
        """Fetch organization audit logs."""
        org = org or self.org
        endpoint = f"/orgs/{org}/audit-log"
        return list(self.paginate(endpoint, {"per_page": per_page}))

    def fetch_tags(self, repo: str, disallowed_exts: Optional[List[str]] = None) -> Optional[str]:
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

    def create_issue(self, repo: str, issue: Issue) -> bool:
        """
        Create a single GitHub issue from an Issue object.

        Returns True if created successfully, False otherwise.
        """
        data = {
            "title": issue.title,
            "body": issue.description,
            "assignees": ["masgeek"],
            "labels": issue.labels
        }
        resp = self._request("POST", f"{GITHUB_API_BASE}/repos/{repo}/issues", json=data)
        if resp.status_code == 201:
            logger.info(f"Issue created: {issue.title}")
            return True
        else:
            logger.error(f"Failed to create issue '{issue.title}': {resp.json()}")
            return False

    def get_all_issues(self, repo: str) -> list[dict]:
        """
        Fetch all issues (open and closed) from GitHub with pagination.
        """
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues"
        page = 1
        params = {"state": "all", "per_page": 100, "page": page}
        all_issues = []
        while True:
            resp = self._request(method="GET", url=url, params=params)
            resp.raise_for_status()
            issues = self._safe_json(resp)
            if not issues:
                logger.info(f"No issues found for {repo}.")
                break
            logger.info(f"Found {len(issues)} issues for {repo}.")
            all_issues.extend(issues)
            params["page"] += 1

        return all_issues
