"""Tests for cli_extensions/repo_commands.py - Repository CLI commands."""

from unittest.mock import Mock, patch

import pytest

from agent_manager.cli_extensions.repo_commands import RepoCommands


class TestRepoCommandsAddCliArguments:
    """Test cases for add_cli_arguments method."""

    def test_adds_update_parser(self):
        """Test that add_cli_arguments adds update parser."""
        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_subparsers.add_parser.return_value = mock_parser

        RepoCommands.add_cli_arguments(mock_subparsers)

        mock_subparsers.add_parser.assert_called_once()
        call_args = mock_subparsers.add_parser.call_args
        assert call_args[0][0] == "update"
        assert "Update all repositories" in call_args[1]["help"]

    def test_adds_force_argument(self):
        """Test that update parser includes force argument."""
        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_subparsers.add_parser.return_value = mock_parser

        RepoCommands.add_cli_arguments(mock_subparsers)

        # Verify force argument was added
        mock_parser.add_argument.assert_called_once()
        call_args = mock_parser.add_argument.call_args
        assert call_args[0][0] == "--force"
        assert call_args[1]["action"] == "store_true"


class TestRepoCommandsProcessCliCommand:
    """Test cases for process_cli_command method."""

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_update_command(self, mock_update):
        """Test processing of update command without force."""
        args = Mock()
        args.force = False
        config_data = {"hierarchy": [{"name": "org", "repo": Mock()}]}

        RepoCommands.process_cli_command(args, config_data)

        mock_update.assert_called_once_with(config_data, force=False)

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_update_command_with_force(self, mock_update):
        """Test processing of update command with force flag."""
        args = Mock()
        args.force = True
        config_data = {"hierarchy": [{"name": "org", "repo": Mock()}]}

        RepoCommands.process_cli_command(args, config_data)

        mock_update.assert_called_once_with(config_data, force=True)

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_update_command_empty_hierarchy(self, mock_update):
        """Test processing of update command with empty hierarchy."""
        args = Mock()
        args.force = False
        config_data = {"hierarchy": []}

        RepoCommands.process_cli_command(args, config_data)

        mock_update.assert_called_once_with(config_data, force=False)

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_update_command_multiple_repos(self, mock_update):
        """Test processing of update command with multiple repositories."""
        args = Mock()
        args.force = False
        config_data = {
            "hierarchy": [
                {"name": "org", "repo": Mock()},
                {"name": "team", "repo": Mock()},
                {"name": "personal", "repo": Mock()},
            ]
        }

        RepoCommands.process_cli_command(args, config_data)

        mock_update.assert_called_once_with(config_data, force=False)


class TestRepoCommandsEdgeCases:
    """Test cases for edge cases and special scenarios."""

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_command_with_missing_force_attribute(self, mock_update):
        """Test processing when args doesn't have force attribute."""
        args = Mock(spec=[])  # No attributes
        config_data = {"hierarchy": []}

        RepoCommands.process_cli_command(args, config_data)

        # Should default to False when force attribute is missing
        mock_update.assert_called_once_with(config_data, force=False)

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_processes_command_handles_update_error(self, mock_update):
        """Test handling of errors from update_repositories."""
        mock_update.side_effect = Exception("Update failed")

        args = Mock()
        args.force = False
        config_data = {"hierarchy": []}

        # Should propagate the exception
        with pytest.raises(Exception, match="Update failed"):
            RepoCommands.process_cli_command(args, config_data)


class TestRepoCommandsIntegration:
    """Integration tests for repo commands."""

    def test_add_and_process_workflow(self):
        """Test complete workflow of adding arguments and processing."""
        import argparse

        # Create parser
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")

        # Add arguments
        RepoCommands.add_cli_arguments(subparsers)

        # Parse update command
        args = parser.parse_args(["update"])
        assert args.command == "update"
        assert args.force is False

        # Parse update with force
        args = parser.parse_args(["update", "--force"])
        assert args.command == "update"
        assert args.force is True

    @patch("agent_manager.cli_extensions.repo_commands.update_repositories")
    def test_full_command_flow(self, mock_update):
        """Test full command flow from argparse to execution."""
        import argparse

        # Set up parser
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        RepoCommands.add_cli_arguments(subparsers)

        # Parse and process
        args = parser.parse_args(["update", "--force"])
        config_data = {"hierarchy": [{"name": "org", "repo": Mock()}]}

        RepoCommands.process_cli_command(args, config_data)

        # Verify execution
        mock_update.assert_called_once_with(config_data, force=True)
