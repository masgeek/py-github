# ============================================================================
# File: cli.py
"""Command-line interface for GitHub organization management."""
import os
import time
from os import getenv
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger

from cli import GitHubClient, CSVProcessor, TokenManager

load_dotenv()


app = typer.Typer(
    help="Batch invite users to a GitHub organization with team management.",
    no_args_is_help=True
)


@app.command(name="release")
def release_tag(
        repo: str = typer.Option(getenv("GITHUB_REPOSITORY"), "--repo", "-r",
                                 help="GitHub repo in 'owner/repo' format"),
        token: str = typer.Option(getenv("GITHUB_TOKEN"), "--token", "-t", help="GitHub token with repo scopes"),
        disallow: str = typer.Option(getenv("DISALLOWED_ASSET_EXTS"), "--exts", "-e",
                                     help="Comma-separated disallowed extensions"),

):
    """
    Fetch the latest GitHub release tag, skipping if disallowed asset types (.apk, .aab, etc.) are present.
    """
    if not repo:
        logger.error("Missing required environment variables: GITHUB_REPOSITORY")
        raise typer.Exit(code=1)
    if not token:
        logger.error("Missing required environment variables: GITHUB_TOKEN")
        raise typer.Exit(code=1)

    client = GitHubClient(token)
    disallowed_exts = tuple(ext.strip() for ext in disallow.split(",") if ext.strip()) if disallow else None
    logger.info(f"Fetching latest release for {repo}")
    logger.info(f"Disallowed extensions: {disallowed_exts or 'None'}")

    try:
        tag = client.fetch_tags(repo, disallowed_exts)
        # Output the tag to stdout for GitHub Actions to capture
        print(tag)
        logger.success(f"Release tag '{tag}' fetched successfully")

    except Exception as e:
        logger.error(f"Error fetching release: {e}")
        raise typer.Exit(code=1)


@app.command()
def invite(
        csv_file: Path = typer.Option(..., "--csv", "-c", help="Path to CSV file with GitHub usernames or emails",
                                      exists=True),
        org: str = typer.Option(None, "--org", "-o", help="GitHub organization name", envvar="GITHUB_ORG"),
        token: str = typer.Option(getenv("GITHUB_TOKEN"), "--token", "-t", help="GitHub token with admin:org scope"),
        team_slug: Optional[str] = typer.Option(None, "--team", help="Optional team slug to add invited members"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview invitations without sending them"),
        skip_header: bool = typer.Option(True, "--skip-header/--no-skip-header",
                                         help="Skip first row if it's a header"),
):
    """
    Batch-invite users to a GitHub organization from a CSV file.

    Example:
        github-invite invite --csv users.csv --org myorg --team developers
    """
    if not org:
        logger.error("Missing required parameters: org")
        raise typer.Exit(code=1)

    if not token:
        logger.error("Missing required parameters: token")
        raise typer.Exit(code=1)

    client = GitHubClient(token)

    logger.info(f"Organization: {org}")
    logger.info(f"CSV file: {csv_file}")
    if team_slug:
        logger.info(f"Target team: {team_slug}")
    if dry_run:
        logger.warning("DRY RUN MODE - No invitations will be sent")
    logger.info("-" * 50)

    try:
        identifiers = CSVProcessor.read_identifiers(csv_file, skip_header)
        success_count = 0
        failure_count = 0

        for identifier in identifiers:
            if dry_run:
                logger.info(f"[DRY RUN] Would invite: {identifier}")
                if team_slug and "@" not in identifier:
                    logger.info(f"[DRY RUN] Would add to team: {team_slug}")
                success_count += 1
            else:
                if client.invite_user(org, identifier):
                    success_count += 1
                    if team_slug and "@" not in identifier:
                        time.sleep(0.5)
                        client.add_to_team(org, team_slug, identifier)
                else:
                    failure_count += 1

            time.sleep(0.3)

        logger.info("-" * 50)
        logger.info(f"Processing complete!")
        logger.info(f"  Successful: {success_count}")
        if failure_count > 0:
            logger.info(f"  Failed: {failure_count}")
        logger.info(f"  Total processed: {success_count + failure_count}")

    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise typer.Exit(code=1)


@app.command()
def repos(
        csv_file: Path = typer.Option(..., "--csv", "-c", help="Path to CSV file with repository details", exists=True),
        org: str = typer.Option(None, "--org", "-o", help="GitHub organization name", envvar="GITHUB_ORG"),
        token: str = typer.Option(getenv("GITHUB_TOKEN"), "--token", "-t",
                                  help="GitHub token with admin:org and repo scopes"),
        private: bool = typer.Option(True, "--private/--public",
                                     help="Create repositories as private (default) or public"),
        auto_init: bool = typer.Option(False, "--auto-init/--no-auto-init", help="Initialize repositories with README"),
        gitignore: Optional[str] = typer.Option(None, "--gitignore", help="Default .gitignore template"),
        license: Optional[str] = typer.Option(None, "--license", help="Default license template"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview repository creation"),
):
    """
    Batch-create repositories in a GitHub organization from a CSV file.

    CSV Format: name,description,private,auto_init,gitignore_template,license_template

    Example:
        github-invite repos --csv repos.csv --org myorg --private --auto-init
    """
    if not token:
        logger.error("Missing required parameters: token")
        raise typer.Exit(code=1)

    client = GitHubClient(token)

    logger.info(f"Organization: {org}")
    logger.info(f"CSV file: {csv_file}")
    logger.info(f"Default visibility: {'Private' if private else 'Public'}")
    if dry_run:
        logger.warning("DRY RUN MODE - No repositories will be created")
    logger.info("-" * 50)

    try:
        repo_configs = CSVProcessor.read_repositories(csv_file)
        success_count = 0
        failure_count = 0

        for config in repo_configs:
            # Apply command-line defaults where CSV doesn't specify
            if not config.gitignore_template and gitignore:
                config.gitignore_template = gitignore
            if not config.license_template and license:
                config.license_template = license

            config.auto_init = auto_init

            if dry_run:
                logger.info(f"[DRY RUN] Would create: {config.name}")
                if config.description:
                    logger.info(f"           Description: {config.description}")
                logger.info(f"           Private: {config.private}, Auto-init: {config.auto_init}")
                success_count += 1
            else:
                if client.create_repository(org, config):
                    success_count += 1
                else:
                    failure_count += 1

            time.sleep(0.3)

        logger.info("-" * 50)
        logger.info(f"Processing complete!")
        logger.info(f"  Successful: {success_count}")
        if failure_count > 0:
            logger.info(f"  Failed: {failure_count}")
        logger.info(f"  Total processed: {success_count + failure_count}")

    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise typer.Exit(code=1)


@app.command()
def token(
        scopes: str = typer.Option("admin:org,read:user,repo", "--scopes", "-s", help="Comma-separated list of scopes"),
        save_to_env: bool = typer.Option(True, "--save/--no-save", help="Save token to .env file"),
        env_file: Path = typer.Option(Path(".env"), "--env-file", help="Path to .env file"),
):
    """
    Generate a GitHub personal access token using Device Flow.

    Example:
        github-invite token
        github-invite token --env-file /path/to/.env
    """
    try:
        access_token = TokenManager.generate_token(scopes)

        if not access_token:
            logger.error("Failed to generate token")
            raise typer.Exit(code=1)

        typer.echo("\n")
        typer.secho("=" * 60, fg="green")
        typer.secho("✓ Token Generated Successfully!", fg="green", bold=True)
        typer.secho("=" * 60, fg="green")
        typer.echo(f"\nAccess Token: {access_token}")

        if save_to_env:
            try:
                TokenManager.save_to_env(access_token, env_file)
                typer.echo(f"\n✓ Token saved to {env_file}")
            except Exception as e:
                logger.error(f"Failed to save token: {e}")
                typer.echo("\n⚠ Could not save to .env file. Please save manually:")
                typer.secho(f"  GITHUB_TOKEN={access_token}", fg="cyan")
        else:
            typer.echo("\n⚠ Token not saved. Add to your .env file:")
            typer.secho(f"  GITHUB_TOKEN={access_token}", fg="cyan")

        typer.echo("\n" + "=" * 60 + "\n")

    except KeyboardInterrupt:
        logger.warning("\nToken generation cancelled by user")
        raise typer.Exit(code=130)


@app.command()
def version():
    """Display version information."""
    typer.echo("GitHub Organization Invite CLI v2.0")
    typer.echo("Enhanced with repo scope for tags and releases")


if __name__ == "__main__":
    app()
