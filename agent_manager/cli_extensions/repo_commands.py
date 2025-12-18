"""CLI commands for managing repositories."""

from agent_manager.core import update_repositories


class RepoCommands:
    """Manages CLI commands for repository operations."""

    @staticmethod
    def add_cli_arguments(subparsers) -> None:
        """Add repository-related CLI arguments.

        Args:
            subparsers: The argparse subparsers to add to
        """
        # Update command
        update_parser = subparsers.add_parser(
            "update", help="Update all repositories in the hierarchy (does not update agent configs)"
        )
        update_parser.add_argument(
            "--force", action="store_true", help="Force update even if repository appears up to date"
        )

    @staticmethod
    def process_cli_command(args, config_data: dict) -> None:
        """Process the update command for repositories.

        Args:
            args: Parsed command-line arguments
            config_data: Configuration data with repo objects
        """
        force_update = getattr(args, "force", False)
        update_repositories(config_data, force=force_update)
