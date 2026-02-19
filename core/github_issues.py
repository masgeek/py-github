import json
from pathlib import Path
from typing import List, Optional

from loguru import logger


class Issue:
    def __init__(self, title: str, description: Optional[str] = None, priority: Optional[str] = None,
                 labels: Optional[List[str]] = None):
        self.title = title
        self.priority = priority or ""
        self.description = description or ""
        self.labels = labels or []

    def __repr__(self):
        return f"Issue(title={self.title!r}, priority={self.priority!r}, labels={self.labels!r})"


def create_issues_from_json_file(json_file: Path) -> List[Issue]:
    """
    Read a JSON file containing an 'Issues' object with an array of issues
    and return a list of Issue objects.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            issues_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file '{json_file}': {e}")
        return []

    # Expecting {"Issues": [ ... ]}
    issues_list = issues_data.get("Issues", [])
    issue_objects: List[Issue] = []

    for issue_dict in issues_list:
        try:
            issue_obj = Issue(**issue_dict)
            issue_objects.append(issue_obj)
        except TypeError as e:
            logger.error(f"Invalid issue data {issue_dict}: {e}")
            continue

    return issue_objects
