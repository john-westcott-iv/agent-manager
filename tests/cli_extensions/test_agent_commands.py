"""Tests for cli_extensions/agent_commands.py - Agent CLI commands."""

from unittest.mock import Mock, patch

import pytest

from agent_manager.cli_extensions.agent_commands import AgentCommands


class TestAgentCommandsAddCliArguments:
    """Test cases for add_cli_arguments method."""

    @patch("agent_manager.cli_extensions.agent_commands.get_agent_names")
    def test_adds_agents_and_run_parsers(self, mock_get_agent_names):
        """Test that add_cli_arguments adds both agents and run parsers."""
        mock_get_agent_names.return_value = ["claude"]

        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_agents_subparsers = Mock()
        mock_parser.add_subparsers.return_value = mock_agents_subparsers
        mock_subparsers.add_parser.return_value = mock_parser

        AgentCommands.add_cli_arguments(mock_subparsers)

        # Should add both "agents" and "run" parsers
        calls = [call[0][0] for call in mock_subparsers.add_parser.call_args_list]
        assert "agents" in calls
        assert "run" in calls

    @patch("agent_manager.cli_extensions.agent_commands.get_agent_names")
    def test_adds_agents_list_subcommand(self, mock_get_agent_names):
        """Test that add_cli_arguments adds list subcommand to agents."""
        mock_get_agent_names.return_value = ["claude"]

        mock_subparsers = Mock()
        mock_agents_parser = Mock()
        mock_agents_subparsers = Mock()
        mock_run_parser = Mock()

        def add_parser_side_effect(name, **kwargs):
            if name == "agents":
                return mock_agents_parser
            elif name == "run":
                return mock_run_parser
            return Mock()

        mock_subparsers.add_parser.side_effect = add_parser_side_effect
        mock_agents_parser.add_subparsers.return_value = mock_agents_subparsers

        AgentCommands.add_cli_arguments(mock_subparsers)

        # Check that list subcommand was added to agents
        mock_agents_subparsers.add_parser.assert_called_once_with("list", help="List available agent plugins")

    @patch("agent_manager.cli_extensions.agent_commands.get_agent_names")
    def test_adds_agent_argument_with_choices(self, mock_get_agent_names):
        """Test that agent argument includes discovered plugins."""
        mock_get_agent_names.return_value = ["claude", "custom"]

        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_parser.add_subparsers.return_value = Mock()
        mock_subparsers.add_parser.return_value = mock_parser

        AgentCommands.add_cli_arguments(mock_subparsers)

        # Check that add_argument was called with choices including discovered agents
        call_args = mock_parser.add_argument.call_args
        assert call_args[1]["choices"] == ["all", "claude", "custom"]

    @patch("agent_manager.cli_extensions.agent_commands.get_agent_names")
    def test_adds_agent_argument_with_no_plugins(self, mock_get_agent_names):
        """Test that agent argument works with no plugins."""
        mock_get_agent_names.return_value = []

        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_parser.add_subparsers.return_value = Mock()
        mock_subparsers.add_parser.return_value = mock_parser

        AgentCommands.add_cli_arguments(mock_subparsers)

        # Should still add argument with just "all"
        call_args = mock_parser.add_argument.call_args
        assert call_args[1]["choices"] == ["all"]


class TestAgentCommandsProcessCliCommand:
    """Test cases for process_cli_command method."""

    @patch("agent_manager.cli_extensions.agent_commands.run_agents")
    def test_processes_run_command_single_agent(self, mock_run_agents):
        """Test processing run command for single agent."""
        args = Mock()
        args.agent = "claude"
        config_data = {"hierarchy": []}

        AgentCommands.process_cli_command(args, config_data)

        mock_run_agents.assert_called_once_with(["claude"], config_data)

    @patch("agent_manager.cli_extensions.agent_commands.run_agents")
    def test_processes_run_command_all_agents(self, mock_run_agents):
        """Test processing run command for all agents."""
        args = Mock()
        args.agent = "all"
        config_data = {"hierarchy": []}

        AgentCommands.process_cli_command(args, config_data)

        mock_run_agents.assert_called_once_with(["all"], config_data)


class TestAgentCommandsProcessAgentsCommand:
    """Test cases for process_agents_command method."""

    def test_no_subcommand_specified(self):
        """Test error when no agents subcommand is specified."""
        args = Mock()
        args.agents_command = None

        with patch("agent_manager.cli_extensions.agent_commands.message"):
            with pytest.raises(SystemExit):
                AgentCommands.process_agents_command(args)

    def test_no_agents_command_attribute(self):
        """Test error when agents_command attribute is missing."""
        args = Mock(spec=[])  # Mock with no attributes

        with patch("agent_manager.cli_extensions.agent_commands.message"):
            with pytest.raises(SystemExit):
                AgentCommands.process_agents_command(args)

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.list_agents")
    def test_processes_list_command(self, mock_list_agents):
        """Test that list command calls list_agents."""
        args = Mock()
        args.agents_command = "list"

        AgentCommands.process_agents_command(args)

        mock_list_agents.assert_called_once()


class TestAgentCommandsListAgents:
    """Test cases for list_agents method."""

    @patch("agent_manager.cli_extensions.agent_commands.discover_agent_plugins")
    def test_list_agents_with_plugins(self, mock_discover):
        """Test listing agents when plugins are available."""
        mock_discover.return_value = {
            "claude": {"package_name": "am_agent_claude", "source": "package"},
            "custom": {"package_name": "am_agent_custom", "source": "package"},
        }

        messages = []

        def capture_message(text, *args, **kwargs):
            messages.append(text)

        with patch("agent_manager.cli_extensions.agent_commands.message", side_effect=capture_message):
            AgentCommands.list_agents()

        # Check that agents are listed
        output = "\n".join(messages)
        assert "claude" in output
        assert "am_agent_claude" in output
        assert "custom" in output
        assert "am_agent_custom" in output
        assert "Total: 2 agent(s)" in output

    @patch("agent_manager.cli_extensions.agent_commands.discover_agent_plugins")
    def test_list_agents_no_plugins(self, mock_discover):
        """Test listing agents when no plugins are available."""
        mock_discover.return_value = {}

        messages = []

        def capture_message(text, *args, **kwargs):
            messages.append(text)

        with patch("agent_manager.cli_extensions.agent_commands.message", side_effect=capture_message):
            AgentCommands.list_agents()

        # Check that appropriate message is shown
        output = "\n".join(messages)
        assert "No agent plugins found" in output
        assert "am_agent_" in output  # Should mention the plugin naming convention

    @patch("agent_manager.cli_extensions.agent_commands.discover_agent_plugins")
    def test_list_agents_sorted(self, mock_discover):
        """Test that agents are listed in sorted order."""
        mock_discover.return_value = {
            "zebra": {"package_name": "am_agent_zebra", "source": "package"},
            "alpha": {"package_name": "am_agent_alpha", "source": "package"},
            "middle": {"package_name": "am_agent_middle", "source": "package"},
        }

        messages = []

        def capture_message(text, *args, **kwargs):
            messages.append(text)

        with patch("agent_manager.cli_extensions.agent_commands.message", side_effect=capture_message):
            AgentCommands.list_agents()

        # Find lines that contain agent names
        agent_lines = [m for m in messages if "am_agent_" in m and "(" in m]

        # Should be in alphabetical order
        assert len(agent_lines) == 3
        assert "alpha" in agent_lines[0]
        assert "middle" in agent_lines[1]
        assert "zebra" in agent_lines[2]
