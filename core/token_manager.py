# ============================================================================
# File: token_manager.py
"""GitHub token generation and management."""
import time
from pathlib import Path
from typing import Optional

import requests
import typer
from loguru import logger

DEVICE_AUTH_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
CLIENT_ID = "Ov23liovKKCp6J6CJdoh"
DEFAULT_SCOPES = "admin:org,read:user,repo"


class TokenManager:
    """Manage GitHub token generation and storage."""

    @staticmethod
    def generate_token(scopes: str = DEFAULT_SCOPES) -> Optional[str]:
        """Generate GitHub token using Device Flow."""
        headers = {"Accept": "application/json"}
        data = {
            "client_id": CLIENT_ID,
            "scope": scopes,
        }

        # Step 1: Request device and user codes
        logger.info("Requesting device authorization...")
        resp = requests.post(DEVICE_AUTH_URL, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        payload = resp.json()

        # Display instructions
        typer.echo("\n" + "=" * 60)
        typer.echo("GitHub Device Authentication")
        typer.echo("=" * 60)
        typer.echo("\n1. Visit this URL in your browser:")
        typer.secho(f"   {payload['verification_uri']}", fg="green", bold=True)
        typer.echo("\n2. Enter this code:")
        typer.secho(f"   {payload['user_code']}", fg="yellow", bold=True)
        typer.echo("\n3. Waiting for authorization...")
        typer.echo("   (Press Ctrl+C to cancel)\n")

        # Step 2: Poll for authorization
        interval = payload.get("interval", 5)
        max_attempts = 100

        for attempt in range(max_attempts):
            time.sleep(interval)

            poll_data = {
                "client_id": CLIENT_ID,
                "device_code": payload["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }

            poll = requests.post(TOKEN_URL, data=poll_data, headers=headers, timeout=10)
            result = poll.json()

            if "error" in result:
                error_type = result["error"]

                if error_type == "authorization_pending":
                    typer.echo(".", nl=False)
                    continue
                elif error_type == "slow_down":
                    interval += 5
                    continue
                elif error_type in ("expired_token", "access_denied"):
                    logger.error(f"Authorization failed: {error_type}")
                    return None
                else:
                    logger.error(f"Error: {result.get('error_description', error_type)}")
                    return None
            else:
                return result["access_token"]

        logger.error("Maximum polling attempts reached")
        return None

    @staticmethod
    def save_to_env(token: str, env_file: Path) -> None:
        """Save or update GITHUB_TOKEN in .env file."""
        token_key = "GITHUB_TOKEN"
        token_line = f"{token_key}={token}\n"

        existing_lines = []
        token_found = False

        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()

            for i, line in enumerate(existing_lines):
                stripped = line.strip()
                if stripped.startswith(f"{token_key}=") or stripped.startswith(f"export {token_key}="):
                    existing_lines[i] = token_line
                    token_found = True
                    logger.info(f"Updated existing {token_key} in {env_file}")
                    break

        if not token_found:
            if existing_lines and not existing_lines[-1].endswith("\n"):
                existing_lines.append("\n")
            existing_lines.append(token_line)
            logger.info(f"Appended {token_key} to {env_file}")

        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(existing_lines)

        # Set secure permissions
        try:
            import stat
            env_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception as e:
            logger.debug(f"Could not set file permissions: {e}")