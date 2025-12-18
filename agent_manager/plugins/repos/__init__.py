"""Repository backend plugins for agent-manager."""

from .abstract_repo import AbstractRepo
from .git_repo import GitRepo
from .local_repo import LocalRepo

__all__ = [
    "AbstractRepo",
    "GitRepo",
    "LocalRepo",
]
