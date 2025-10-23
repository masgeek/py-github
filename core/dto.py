from dataclasses import dataclass

@dataclass
class RepositoryConfig:
    """Configuration for creating a repository."""
    name: str
    description: str = ""
    private: bool = True
    auto_init: bool = False
    gitignore_template: str = ""
    license_template: str = ""
