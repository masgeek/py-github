import typer
import requests
from os import getenv
from dotenv import load_dotenv
from loguru import logger
from typing import Optional

load_dotenv()
app = typer.Typer()


def get_headers(token: str):
    return {"Authorization": f"token {token}"}


@app.command()
def fetch(
        repo: str = typer.Option(None, "--repo", "-r", help="GitHub repo in 'owner/repo' format",
                                 envvar="GITHUB_REPOSITORY"),
        token: str = typer.Option(None, "--token", "-t", help="GitHub token with repo scopes",
                                  envvar="GITHUB_TOKEN"),
        disallow: str = typer.Option("", "--token", "-t", help="Comma-separated disallowed extensions",
                                     envvar="DISALLOWED_ASSET_EXTS"),

):
    """

    Fetch the latest GitHub release tag, skipping if disallowed asset types (.apk, .aab, etc.) are present.
    """
    if not repo or not token:
        logger.error("Missing required environment variables: REPO_NAME and GITHUB_TOKEN.")
        raise typer.Exit(code=1)

    disallowed_exts = tuple(ext.strip() for ext in disallow.split(",") if ext.strip()) if disallow else None
    logger.info(f"Fetching latest release for {repo}")
    logger.info(f"Disallowed extensions: {disallowed_exts or 'None'}")

    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        resp = requests.get(url, headers=get_headers(token))
        resp.raise_for_status()
        release = resp.json()

        tag = release.get("tag_name")
        assets = [a.get("name", "") for a in release.get("assets", [])]

        if disallowed_exts:
            for name in assets:
                if any(name.endswith(ext) for ext in disallowed_exts):
                    logger.error(f"Disallowed asset found in release {tag}: {name}")
                    raise typer.Exit(code=2)

        # Output the tag to stdout for GitHub Actions to capture
        print(tag)
        logger.success(f"Release tag '{tag}' fetched successfully")

    except requests.RequestException as e:
        logger.error(f"Error fetching release: {e}")
        raise typer.Exit(code=3)


if __name__ == "__main__":
    app()
