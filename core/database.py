import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Callable

import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Any


class GitHubDatabase:
    DEFAULT_PATH = Path.cwd() / "github_data.db"

    def __init__(self, db_path: str | Path = None):
        self.db_path = str(db_path or self.DEFAULT_PATH)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS issues
                           (
                               id         INTEGER PRIMARY KEY,
                               number     INTEGER,
                               title      TEXT,
                               body       TEXT,
                               state      TEXT,
                               labels     TEXT,
                               created_at TEXT,
                               updated_at TEXT,
                               closed_at  TEXT,
                               hash       TEXT
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS pull_requests
                           (
                               id     INTEGER PRIMARY KEY,
                               number INTEGER,
                               title  TEXT,
                               body   TEXT,
                               state  TEXT,
                               merged INTEGER,
                               hash   TEXT
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS commits
                           (
                               sha     TEXT PRIMARY KEY,
                               message TEXT,
                               author  TEXT,
                               date    TEXT,
                               hash    TEXT
                           )
                           """)

            conn.commit()

    # ---------- Hash Helpers ----------
    @staticmethod
    def _hash_issue(issue: Dict[str, Any]) -> str:
        labels = ",".join([label["name"] for label in issue.get("labels", [])])
        raw = f"{issue['title']}|{issue.get('body', '')}|{labels}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_pr(pr: Dict[str, Any]) -> str:
        raw = f"{pr['title']}|{pr.get('body', '')}|{pr['state']}|{pr.get('merged', False)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_commit(commit: Dict[str, Any]) -> str:
        raw = f"{commit['sha']}|{commit['commit']['message']}|{commit['commit']['author']['name']}|{commit['commit']['author']['date']}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ---------- Upsert Methods ----------
    def upsert_issues(self, issues: List[Dict[str, Any]]):
        with self._connect() as conn:
            cursor = conn.cursor()
            for issue in issues:
                labels = ",".join([label["name"] for label in issue.get("labels", [])])
                issue_hash = self._hash_issue(issue)
                cursor.execute("""
                               INSERT INTO issues (id, number, title, body, state, labels, created_at, updated_at,
                                                   closed_at, hash)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                               ON CONFLICT(id) DO UPDATE SET number=excluded.number,
                                                             title=excluded.title,
                                                             body=excluded.body,
                                                             state=excluded.state,
                                                             labels=excluded.labels,
                                                             created_at=excluded.created_at,
                                                             updated_at=excluded.updated_at,
                                                             closed_at=excluded.closed_at,
                                                             hash=excluded.hash
                               """, (
                                   issue["id"],
                                   issue["number"],
                                   issue["title"],
                                   issue.get("body", ""),
                                   issue["state"],
                                   labels,
                                   issue.get("created_at"),
                                   issue.get("updated_at"),
                                   issue.get("closed_at"),
                                   issue_hash
                               ))
            conn.commit()

    def upsert_pull_requests(self, prs: List[Dict[str, Any]]):
        with self._connect() as conn:
            cursor = conn.cursor()
            for pr in prs:
                pr_hash = self._hash_pr(pr)
                cursor.execute("""
                               INSERT INTO pull_requests (id, number, title, body, state, merged, hash)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               ON CONFLICT(id) DO UPDATE SET number=excluded.number,
                                                             title=excluded.title,
                                                             body=excluded.body,
                                                             state=excluded.state,
                                                             merged=excluded.merged,
                                                             hash=excluded.hash
                               """, (
                                   pr["id"],
                                   pr["number"],
                                   pr["title"],
                                   pr.get("body", ""),
                                   pr["state"],
                                   int(pr.get("merged", False)),
                                   pr_hash
                               ))
            conn.commit()

    def upsert_commits(self, commits: List[Dict[str, Any]]):
        with self._connect() as conn:
            cursor = conn.cursor()
            for commit in commits:
                commit_hash = self._hash_commit(commit)
                cursor.execute("""
                               INSERT INTO commits (sha, message, author, date, hash)
                               VALUES (?, ?, ?, ?, ?)
                               ON CONFLICT(sha) DO UPDATE SET message=excluded.message,
                                                              author=excluded.author,
                                                              date=excluded.date,
                                                              hash=excluded.hash
                               """, (
                                   commit["sha"],
                                   commit["commit"]["message"],
                                   commit["commit"]["author"]["name"],
                                   commit["commit"]["author"]["date"],
                                   commit_hash
                               ))
            conn.commit()

    # ---------- Query ----------
    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def issue_exists(self, issue_title: str) -> bool:
        """Check if an issue already exists in the DB by hash."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM issues WHERE title = ?", (issue_title,))
            return cursor.fetchone() is not None
