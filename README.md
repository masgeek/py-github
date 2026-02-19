# GitHub Organization Management CLI

A powerful command-line tool for batch managing GitHub organization operations including user invitations, team management, and repository creation.

## ✨ Features

* 🎯 **Batch User Invitations** — Invite multiple users from a CSV file  
* 👥 **Team Management** — Automatically add invited users to teams  
* 📦 **Repository Creation** — Create repositories for **organizations** and **personal accounts**  
* 🏷️ **Release Tag Validation** — Fetch latest release tags and verify allowed assets  
* 🔐 **Token Management** — Generate GitHub tokens with Device Flow authentication  
* 💾 **Smart .env Management** — Automatically save/update tokens in `.env` files  
* 🚀 **Dry Run Mode** — Preview changes before executing  
* ⚡ **Rate Limit Handling** — Automatic rate limit detection and sleep/retry logic  
* 📊 **Detailed Logging** — Clear, color-coded output with progress indicators and warnings  

## 📋 Requirements

* Python 3.9+  
* GitHub organization admin access (for org actions)  
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

---

### Create Repositories

You can now create repositories for both **organizations** and **personal accounts** directly from the CLI.

#### 🏢 Organization Repositories

```bash
github-tool repos --csv repos.csv --org myorg
```

#### 👤 Personal Repositories

If you omit `--org`, repositories are created under your personal GitHub account.

```bash
github-tool repos --csv repos.csv
```

#### ⚙️ Advanced CLI Options

```bash
# Create public repositories
github-tool repos --csv repos.csv --org myorg --public

# Initialize with README
github-tool repos --csv repos.csv --org myorg --auto-init

# Add templates
github-tool repos --csv repos.csv --org myorg --gitignore Python --license mit

# Test configuration (no changes)
github-tool repos --csv repos.csv --org myorg --dry-run
```

**Example repos.csv**

```csv
name,description,private,auto_init,gitignore_template,license_template
core-api,Main API,true,true,Python,mit
frontend-app,Web UI,false,true,Node,apache-2.0
```

#### Behavior

- `--org` → creates under that organization.  
- No `--org` → creates under authenticated user’s personal account.  
- The client uses `.env` `GITHUB_ORG` if no flag is passed.  
- Logs creation URLs and handles “already exists” automatically.  
- Returns success (`0`) or error exit codes for CI/CD pipelines.

---

### Fetch Release Tags

```python
from core.github_client import GitHubClient

client = GitHubClient("ghp_token")
latest_tag = client.fetch_tags("myorg/my-repo", disallowed_exts=[".exe", ".bat"])
print(latest_tag)
```

---

### Generate Token

```bash
github-tool token --save
```

---

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

---

## 🔌 Library Usage Example

```python
from core.github_client import GitHubClient, RepositoryConfig

client = GitHubClient("ghp_token")

# Invite user
client.invite_user("myorg", "alice")

# Add to team
client.add_to_team("myorg", "devs", "alice")

# Create repository (org or user)
repo_cfg = RepositoryConfig(
    name="new-repo",
    description="Automation test",
    private=True,
    auto_init=True,
    gitignore_template="Python",
    license_template="mit"
)
client.create_repository("myorg", repo_cfg)       # Organization repo
client.create_repository(None, repo_cfg)          # Personal repo
```

---

## 🐛 Troubleshooting

**Rate Limits:** Automatically handled with retry logic.  
**Auth Errors:** Ensure correct token scopes (`admin:org,repo,read:user`).  
**CSV Errors:** Ensure UTF-8 encoding and correct headers.  

---

## 🤝 Contributing

Fork, branch, commit, and open a pull request.  

---

## 📝 License

MIT License
