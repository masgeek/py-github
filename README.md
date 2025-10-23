# GitHub Organization Management CLI

A powerful command-line tool for batch managing GitHub organization operations including user invitations, team management, and repository creation.

## ✨ Features

- 🎯 **Batch User Invitations** - Invite multiple users from a CSV file
- 👥 **Team Management** - Automatically add invited users to teams
- 📦 **Repository Creation** - Create multiple repositories with custom configurations
- 🔐 **Token Management** - Generate GitHub tokens with Device Flow authentication
- 💾 **Smart .env Management** - Automatically save/update tokens in .env files
- 🚀 **Dry Run Mode** - Preview changes before executing
- ⚡ **Rate Limit Handling** - Automatic rate limit detection and waiting
- 📊 **Detailed Logging** - Clear, color-coded output with progress indicators

## 📋 Requirements

- Python 3.9+
- GitHub organization admin access
- GitHub Personal Access Token with scopes:
  - `admin:org` - Manage organization invitations
  - `read:user` - Read user profile data
  - `repo` - Create repositories and read tags/releases

## 🚀 Installation

### From Source (Using Poetry - Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/github-tool.git
cd github-tool

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell

# The CLI will be available as 'github-tool'
github-tool --help
```

### Alternative: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/github-tool.git
cd github-tool

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Dependencies (pyproject.toml)

```toml
[tool.poetry]
name = "github-tool"
version = "2.0.0"
description = "GitHub Organization Management CLI Tool"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.31.0"
typer = {extras = ["all"], version = "^0.9.0"}
python-dotenv = "^1.0.0"
loguru = "^0.7.0"

[tool.poetry.scripts]
github-tool = "cli.app:app"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Requirements.txt (for pip users)

```txt
requests>=2.31.0
typer[all]>=0.9.0
python-dotenv>=1.0.0
loguru>=0.7.0
```

## 🔧 Setup

### 1. Generate a GitHub Token

```bash
github-invite token
```

This will:
1. Open GitHub's device authentication flow
2. Display a URL and code to authorize
3. Automatically save the token to `.env`

### 2. Configure Environment Variables

Create a `.env` file or let the token command create it:

```env
GITHUB_ORG=your-organization-name
GITHUB_TOKEN=ghp_your_token_here
```

## 📖 Usage

### Invite Users

Invite users from a CSV file to your organization:

```bash
    # Basic invitation
github-tool invite --csv users.csv --org myorg

# Invite and add to a team
github-tool invite --csv users.csv --org myorg --team developers

# Dry run (preview without executing)
github-tool invite --csv users.csv --org myorg --dry-run
```

**CSV Format (users.csv):**
```csv
username
alice
bob@example.com
charlie
```

Or with header:
```csv
email
alice@example.com
bob@example.com
charlie@example.com
```

### Create Repositories

Batch create repositories from a CSV file:

```bash
# Create private repositories
github-tool repos --csv repos.csv --org myorg

# Create public repositories with auto-initialization
github-tool repos --csv repos.csv --org myorg --public --auto-init

# Set default templates
github-tool repos --csv repos.csv --org myorg --gitignore Python --license mit

# Dry run
github-tool repos --csv repos.csv --org myorg --dry-run
```

**CSV Format (repos.csv):**

Simple format:
```csv
name
my-api
frontend-app
data-pipeline
```

Full format with all options:
```csv
name,description,private,auto_init,gitignore_template,license_template
my-api,Backend API service,true,true,Python,mit
frontend-app,React frontend application,false,true,Node,apache-2.0
data-pipeline,ETL data pipeline,,true,Python,
internal-tool,Internal automation tool,true,false,,
```

**Available Templates:**
- **Gitignore**: Python, Node, Java, Go, Ruby, Rust, etc.
- **License**: mit, apache-2.0, gpl-3.0, bsd-3-clause, etc.

### Generate Token

Generate a new GitHub Personal Access Token:

```bash
# Generate and save to .env
github-tool token

# Save to custom location
github-tool token --env-file /path/to/.env

# Just display, don't save
github-tool token --no-save

# Custom scopes
github-tool token --scopes "admin:org,repo,read:user"
```

### Version

Display version information:

```bash
github-tool version
```

## 🎯 Command Reference

### `invite` - Invite users to organization

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--csv` | `-c` | Path to CSV file with usernames/emails | Required |
| `--org` | `-o` | GitHub organization name | `$GITHUB_ORG` |
| `--token` | `-t` | GitHub access token | `$GITHUB_ORG_TOKEN` |
| `--team` | | Team slug to add members to | None |
| `--dry-run` | | Preview without executing | `false` |
| `--skip-header` | | Skip first row if it's a header | `true` |

### `repos` - Create repositories

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--csv` | `-c` | Path to CSV file with repository details | Required |
| `--org` | `-o` | GitHub organization name | `$GITHUB_ORG` |
| `--token` | `-t` | GitHub access token | `$GITHUB_ORG_TOKEN` |
| `--private/--public` | | Repository visibility | `--private` |
| `--auto-init` | | Initialize with README | `false` |
| `--gitignore` | | Default .gitignore template | None |
| `--license` | | Default license template | None |
| `--dry-run` | | Preview without executing | `false` |

### `token` - Generate GitHub token

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--scopes` | `-s` | Comma-separated list of scopes | `admin:org,read:user,repo` |
| `--save/--no-save` | | Save token to .env file | `--save` |
| `--env-file` | | Path to .env file | `.env` |

## 💡 Examples

### Example 1: Onboard New Team Members

```bash
# 1. Create CSV with new members
cat > new-members.csv << EOF
username
alice
bob
charlie
EOF

# 2. Invite them and add to team
github-tool invite \
  --csv new-members.csv \
  --org mycompany \
  --team engineering

# Output:
# ✓ Invited: alice
# ✓ Added alice to team 'engineering'
# ✓ Invited: bob
# ✓ Added bob to team 'engineering'
```

### Example 2: Setup Platform Repositories

This example creates all AgWise platform repositories. The CLI scripts live in `agwise-api`, while the core R packages are in `agwise-core`.

```bash
# 1. Create CSV with repository details
cat > agwise-repos.csv << EOF
name,description,private,auto_init,gitignore_template,license_template
agwise-core,Core R packages and statistical models,true,true,R,mit
agwise-data,Data management and processing pipelines,true,true,R,mit
agwise-soil-health,Soil health analysis and recommendations,true,true,R,mit
agwise-planting-date-and-cultivar,Planting date and cultivar optimization,true,true,R,mit
agwise-cropping-innovation,Cropping innovation research modules,true,true,R,mit
agwise-organic-fertilizer,Organic fertilizer optimization algorithms,true,true,R,mit
agwise-fertilizer,Fertilizer recommendation system,true,true,R,mit
agwise-farm-bundled-advisories,Farm bundled advisory generation,true,true,R,mit
agwise-dashboard,Interactive dashboard and visualization,true,true,R,mit
agwise-api,REST API and CLI tools (Python/Poetry),true,true,Python,mit
agwise-docs,Platform documentation and guides,false,true,,cc-by-4.0
EOF

# 2. Create all repositories
github-invite repos \
  --csv agwise-repos.csv \
  --org agwise

# Output:
# ✓ Created: agwise-core → https://github.com/agwise/agwise-core
# ✓ Created: agwise-data → https://github.com/agwise/agwise-data
# ✓ Created: agwise-soil-health → https://github.com/agwise/agwise-soil-health
# ✓ Created: agwise-planting-date-and-cultivar → https://github.com/agwise/agwise-planting-date-and-cultivar
# ✓ Created: agwise-cropping-innovation → https://github.com/agwise/agwise-cropping-innovation
# ✓ Created: agwise-organic-fertilizer → https://github.com/agwise/agwise-organic-fertilizer
# ✓ Created: agwise-fertilizer → https://github.com/agwise/agwise-fertilizer
# ✓ Created: agwise-farm-bundled-advisories → https://github.com/agwise/agwise-farm-bundled-advisories
# ✓ Created: agwise-dashboard → https://github.com/agwise/agwise-dashboard
# ✓ Created: agwise-api → https://github.com/agwise/agwise-api
# ✓ Created: agwise-docs → https://github.com/agwise/agwise-docs

# 3. Now you can clone and set up the API with CLI tools
git clone https://github.com/agwise/agwise-api.git
cd agwise-api
poetry install
```

### Example 3: Dry Run Before Execution

```bash
# Preview what would happen
github-invite invite --csv users.csv --org myorg --dry-run

# Output:
# [DRY RUN] Would invite: alice
# [DRY RUN] Would invite: bob@example.com
# Processing complete!
#   Successful: 2
#   Total processed: 2
```

## 🏗️ Project Structure

```
github-tool/
├── cli/                       # CLI interface package
│   ├── __init__.py
│   └── app.py                 # Command-line interface with Typer
├── core/                      # Core functionality package
│   ├── __init__.py
│   ├── github_client.py       # GitHub API client
│   ├── csv_processor.py       # CSV file processing
│   └── token_manager.py       # Token generation & management
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_github_client.py
│   ├── test_csv_processor.py
│   └── test_token_manager.py
├── examples/                  # Example CSV files
│   ├── users.csv
│   └── repos.csv
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Poetry configuration
├── requirements.txt          # Pip requirements
├── LICENSE                   # MIT License
└── README.md                 # This file
```

### Package Organization

**`cli/`** - Command-line interface
- **`__init__.py`** - Package initialization
- **`app.py`** - Typer CLI application with all commands (invite, repos, token, version)

**`core/`** - Core business logic
- **`__init__.py`** - Exports main classes and version
- **`github_client.py`** - GitHubClient, RepositoryConfig, API interactions
- **`csv_processor.py`** - CSVProcessor for reading and parsing CSV files
- **`token_manager.py`** - TokenManager for OAuth and .env management

## 🔌 Using as a Library

You can also use the modules programmatically in your own Python projects:

```python
from github_cli import GitHubClient, RepositoryConfig, CSVProcessor, TokenManager

# Initialize client
client = GitHubClient(token="ghp_your_token")

# Invite a user
client.invite_user("myorg", "alice")
client.invite_user("myorg", "bob@example.com")

# Add user to team
client.add_to_team("myorg", "developers", "alice")

# Create a repository
config = RepositoryConfig(
    name="my-repo",
    description="My new repository",
    private=True,
    auto_init=True,
    gitignore_template="Python",
    license_template="mit"
)
client.create_repository("myorg", config)

# Process CSV files
identifiers = CSVProcessor.read_identifiers("users.csv")
repos = CSVProcessor.read_repositories("repos.csv")

# Generate and save token
token = TokenManager.generate_token()
TokenManager.save_to_env(token, Path(".env"))
```

### Installing as a Library

```bash
# Install from PyPI (when published)
pip install github-org-cli

# Or install from source
pip install git+https://github.com/yourusername/github-org-cli.git

# Or with Poetry
poetry add git+https://github.com/yourusername/github-org-cli.git
```

## 🐛 Troubleshooting

### Rate Limiting

If you hit GitHub's rate limits, the tool will automatically wait and retry. You can see rate limit status:

```bash
# The tool will display warnings like:
# Rate limit exceeded. Waiting 120 seconds...
```

### Authentication Errors

If you get authentication errors:

1. Regenerate your token: `github-invite token`
2. Ensure token has correct scopes: `admin:org`, `read:user`, `repo`
3. Check token is saved: `cat .env | grep GITHUB_ORG_TOKEN`

### CSV Format Issues

Common CSV issues:
- Ensure UTF-8 encoding
- Check for blank rows (they're automatically skipped)
- Verify column names for repositories CSV (must have `name` column)
- Use `--no-skip-header` if your CSV has no header row

### Permission Errors

Ensure you have:
- Organization admin/owner access
- Correct token scopes
- Team admin permissions (for `--team` option)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) - CLI framework
- Logging powered by [Loguru](https://github.com/Delgan/loguru)
- Environment management with [python-dotenv](https://github.com/theskumar/python-dotenv)

## 📧 Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation above

## 🗺️ Roadmap

- [ ] Add support for organization settings configuration
- [ ] Team creation and management commands
- [ ] Repository archiving and deletion
- [ ] Member role management
- [ ] Export organization data to CSV
- [ ] GitHub Actions workflow generation
- [ ] Webhook management
- [ ] Branch protection rules configuration

---

Made with ❤️ for efficient GitHub organization management