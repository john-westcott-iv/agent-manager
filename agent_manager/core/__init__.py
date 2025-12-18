"""Core infrastructure for agent-manager plugin system."""

from .merger_registry import MergerRegistry
from .mergers import create_default_merger_registry, discover_merger_classes
from .repos import create_repo, discover_repo_types, get_repo_type_map, update_repositories

__all__ = [
    "MergerRegistry",
    "create_default_merger_registry",
    "discover_merger_classes",
    "create_repo",
    "discover_repo_types",
    "get_repo_type_map",
    "update_repositories",
]
