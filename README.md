# GitHub Organization Management CLI

A powerful command-line tool for batch managing GitHub organization operations including user invitations, team management, and repository creation.

## ✨ Features

* 🎯 **Batch User Invitations** — Invite multiple users from a CSV file
* 👥 **Team Management** — Automatically add invited users to teams
* 📦 **Repository Creation** — Create multiple repositories with custom configurations
* 🏷️ **Release Tag Validation** — Fetch latest release tags and verify allowed assets
* 🔐 **Token Management** — Generate GitHub tokens with Device Flow authentication
* 💾 **Smart .env Management** — Automatically save/update tokens in `.env` files
* 🚀 **Dry Run Mode** — Preview changes before executing
* ⚡ **Rate Limit Handling** — Automatic rate limit detection and sleep/retry logic
* 📊 **Detailed Logging** — Clear, color-coded output with progress indicators and warnings

## 📋 Requirements

* Python 3.9+
* GitHub organization admin access
* GitHub Personal Access Token with scopes:

  * `admin:org` — Manage organization invitations
  * `read:user` — Read user profile data
  * `repo` — Create repositories and read tags/releases

## 🚀 Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/yourusername/github-tool.git
cd github-tool
poetry install
poetry shell
github-tool --help
```

### Using pip

```bash
git clone https://github.com/yourusername/github-tool.git
cd github-tool
pip install -r requirements.txt
pip install -e .
```

### Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.31.0"
typer = {extras = ["all"], version = "^0.9.0"}
python-dotenv = "^1.0.0"
loguru = "^0.7.0"
```

## 🔧 Setup

Create a `.env` file:

```env
GITHUB_ORG=my-org
GITHUB_TOKEN=ghp_your_token_here
```

## 📖 Usage

### Invite Users

```bash
github-tool invite --csv users.csv --org myorg
github-tool invite --csv users.csv --org myorg --team devs
github-tool invite --csv users.csv --org myorg --dry-run
```

**CSV Example**

```csv
username
alice
bob@example.com
charlie
```

### Create Repositories

```bash
github-tool repos --csv repos.csv --org myorg
github-tool repos --csv repos.csv --org myorg --public --auto-init
github-tool repos --csv repos.csv --org myorg --gitignore Python --license mit
github-tool repos --csv repos.csv --org myorg --dry-run
```

**Example repos.csv**

```csv
name,description,private,auto_init,gitignore_template,license_template
core-api,Main API,true,true,Python,mit
frontend-app,Web UI,false,true,Node,apache-2.0
```

### Fetch Release Tags

```python
from core.github_client import GitHubClient

client = GitHubClient("ghp_token")
latest_tag = client.fetch_tags("myorg/my-repo", disallowed_exts=[".exe", ".bat"])
print(latest_tag)
```

### Generate Token

```bash
github-tool token --save
```

## 🏗️ Project Structure

```
github-tool/
├── cli/
│   └── app.py
├── core/
│   ├── github_client.py
│   ├── csv_processor.py
│   └── token_manager.py
└── tests/
```

## 🔌 Library Usage Example

```python
from core.github_client import GitHubClient, RepositoryConfig

client = GitHubClient("ghp_token")
client.invite_user("myorg", "alice")
client.add_to_team("myorg", "devs", "alice")

repo_cfg = RepositoryConfig(
    name="new-repo",
    description="Automation test",
    private=True,
    auto_init=True,
    gitignore_template="Python",
    license_template="mit"
)
client.create_repository("myorg", repo_cfg)
```

## 🐛 Troubleshooting

**Rate Limits:** The client automatically waits and retries.
**Auth Errors:** Ensure correct token scopes (`admin:org,repo,read:user`).
**CSV Errors:** Verify UTF-8 encoding and required headers.

## 🤝 Contributing

Fork, branch, commit, and open a pull request.

## 📝 License

MIT License.
