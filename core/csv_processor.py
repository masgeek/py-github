# ============================================================================
# File: csv_processor.py
"""CSV file processing utilities."""
import csv
from pathlib import Path
from loguru import logger

from core.dto import RepositoryConfig


class CSVProcessor:
    """Handle CSV file processing."""

    @staticmethod
    def read_identifiers(csv_file: Path, skip_header: bool = True) -> list[str]:
        """Read user identifiers from CSV."""
        identifiers = []
        processed = set()

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            for idx, row in enumerate(reader, start=1):
                if not row or not row[0].strip():
                    continue

                # Skip header row
                if skip_header and idx == 1:
                    header_value = row[0].strip().lower()
                    if header_value in ("username", "email", "user", "name"):
                        logger.debug(f"Skipping header row: {row[0]}")
                        continue

                identifier = row[0].strip()

                # Skip duplicates
                if identifier in processed:
                    logger.debug(f"Skipping duplicate: {identifier}")
                    continue

                processed.add(identifier)
                identifiers.append(identifier)

        return identifiers

    @staticmethod
    def read_repositories(csv_file: Path) -> list[RepositoryConfig]:
        """Read repository configurations from CSV."""
        repos = []
        processed = set()

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames or "name" not in reader.fieldnames:
                raise ValueError("CSV must have a 'name' column for repository names")

            for row in reader:
                repo_name = row.get("name", "").strip()

                if not repo_name or repo_name in processed:
                    continue

                processed.add(repo_name)

                # Parse boolean values
                private = CSVProcessor._parse_bool(row.get("private", ""), True)
                auto_init = CSVProcessor._parse_bool(row.get("auto_init", ""), False)

                config = RepositoryConfig(
                    name=repo_name,
                    description=row.get("description", "").strip(),
                    private=private,
                    auto_init=auto_init,
                    gitignore_template=row.get("gitignore_template", "").strip(),
                    license_template=row.get("license_template", "").strip()
                )
                repos.append(config)

        return repos

    @staticmethod
    def _parse_bool(value: str, default: bool) -> bool:
        """Parse boolean value from CSV."""
        if not value.strip():
            return default
        return value.strip().lower() in ("true", "yes", "1")
