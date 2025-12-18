"""Tests for cli_extensions/agent_commands.py - Agent CLI commands."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent_manager.cli_extensions.agent_commands import AgentCommands


class TestAgentCommandsDiscoverPlugins:
    """Test cases for discover_plugins method."""

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_single_plugin(self, mock_distributions):
        """Test discovery of single agent plugin."""
        mock_dist = Mock()
        mock_dist.name = "ai-agent-claude"
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        assert "claude" in plugins
        assert plugins["claude"] == "ai_agent_claude"

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_multiple_plugins(self, mock_distributions):
        """Test discovery of multiple agent plugins."""
        mock_dist1 = Mock()
        mock_dist1.name = "ai-agent-claude"
        mock_dist2 = Mock()
        mock_dist2.name = "ai-agent-custom"
        mock_dist3 = Mock()
        mock_dist3.name = "other-module"  # Should be ignored

        mock_distributions.return_value = [mock_dist1, mock_dist2, mock_dist3]

        plugins = AgentCommands.discover_plugins()

        assert "claude" in plugins
        assert plugins["claude"] == "ai_agent_claude"
        assert "custom" in plugins
        assert plugins["custom"] == "ai_agent_custom"
        assert len(plugins) == 2

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_no_plugins(self, mock_distributions):
        """Test discovery when no plugins found."""
        mock_dist = Mock()
        mock_dist.name = "other-module"
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        assert plugins == {}

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_handles_discovery_exception(self, mock_distributions):
        """Test handling of discovery exceptions."""
        mock_distributions.side_effect = Exception("Discovery failed")

        with patch("agent_manager.cli_extensions.agent_commands.message"):
            with pytest.raises(SystemExit):
                AgentCommands.discover_plugins()

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_editable_install(self, mock_distributions):
        """Test discovery works with editable installs (the fix for the bug)."""
        # This simulates an editable install which caused the original issue
        mock_dist = Mock()
        mock_dist.name = "ai-agent-claude"  # Editable installs use hyphenated names
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        # Should correctly convert hyphenated name to underscored module name
        assert "claude" in plugins
        assert plugins["claude"] == "ai_agent_claude"

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_normalizes_package_names(self, mock_distributions):
        """Test that package names are normalized (hyphens to underscores)."""
        mock_dist = Mock()
        mock_dist.name = "ai-agent-my-custom-plugin"
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        assert "my_custom_plugin" in plugins
        assert plugins["my_custom_plugin"] == "ai_agent_my_custom_plugin"


class TestAgentCommandsAddCliArguments:
    """Test cases for add_cli_arguments method."""

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_adds_agents_and_run_parsers(self, mock_discover):
        """Test that add_cli_arguments adds both agents and run parsers."""
        mock_discover.return_value = {"claude": "ai_agent_claude"}

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

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_adds_agents_list_subcommand(self, mock_discover):
        """Test that add_cli_arguments adds list subcommand to agents."""
        mock_discover.return_value = {"claude": "ai_agent_claude"}

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

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_adds_agent_argument_with_choices(self, mock_discover):
        """Test that agent argument includes discovered plugins."""
        mock_discover.return_value = {"claude": "ai_agent_claude", "custom": "ai_agent_custom"}

        mock_subparsers = Mock()
        mock_parser = Mock()
        mock_parser.add_subparsers.return_value = Mock()
        mock_subparsers.add_parser.return_value = mock_parser

        AgentCommands.add_cli_arguments(mock_subparsers)

        # Check that add_argument was called with choices including discovered agents
        call_args = mock_parser.add_argument.call_args
        assert call_args[1]["choices"] == ["all", "claude", "custom"]

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_adds_agent_argument_with_no_plugins(self, mock_discover):
        """Test that agent argument works with no plugins."""
        mock_discover.return_value = {}

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

    def test_processes_run_command_single_agent(self):
        """Test processing run command for single agent."""
        with patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins") as mock_discover:
            with patch("agent_manager.cli_extensions.agent_commands.importlib.import_module") as mock_import:
                # Mock discover_plugins to return consistently
                mock_discover.return_value = {"test": "ai_agent_test"}

                # Mock agent module and class
                mock_agent_class = Mock()
                mock_agent_instance = Mock()
                mock_agent_class.return_value = mock_agent_instance

                mock_module = Mock()
                mock_module.Agent = mock_agent_class
                mock_import.return_value = mock_module

                args = Mock()
                args.agent = "test"
                config_data = {"hierarchy": []}

                with patch("agent_manager.cli_extensions.agent_commands.message"):
                    AgentCommands.process_cli_command(args, config_data)

                # Check that import_module was called with our agent module
                assert any(call[0][0] == "ai_agent_test" for call in mock_import.call_args_list)
                mock_agent_instance.update.assert_called_once_with(config_data)

    def test_processes_run_command_all_agents(self):
        """Test processing run command for all agents."""
        with patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins") as mock_discover:
            with patch("agent_manager.cli_extensions.agent_commands.importlib.import_module") as mock_import:
                mock_discover.return_value = {"test1": "ai_agent_test1", "test2": "ai_agent_test2"}

                # Mock agent module and class
                mock_agent_instance = Mock()
                mock_module = Mock()
                mock_module.Agent = Mock(return_value=mock_agent_instance)
                mock_import.return_value = mock_module

                args = Mock()
                args.agent = "all"
                config_data = {"hierarchy": []}

                with patch("agent_manager.cli_extensions.agent_commands.message"):
                    AgentCommands.process_cli_command(args, config_data)

                # Should import and run both agents
                agent_calls = [
                    call for call in mock_import.call_args_list if call[0][0] in ["ai_agent_test1", "ai_agent_test2"]
                ]
                assert len(agent_calls) == 2
                assert mock_agent_instance.update.call_count == 2

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_processes_run_command_no_agents(self, mock_discover):
        """Test processing run command when no agents available."""
        mock_discover.return_value = {}

        args = Mock()
        args.agent = "all"
        config_data = {}

        with patch("agent_manager.cli_extensions.agent_commands.message"):
            with pytest.raises(SystemExit):
                AgentCommands.process_cli_command(args, config_data)

    def test_processes_run_command_import_error(self):
        """Test handling of agent import errors."""
        with patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins") as mock_discover:
            with patch("agent_manager.cli_extensions.agent_commands.importlib.import_module") as mock_import:
                mock_discover.return_value = {"test": "ai_agent_test"}

                # Only fail on ai_agent_test import, allow other imports
                def import_side_effect(name):
                    if name == "ai_agent_test":
                        raise Exception("Import failed")
                    return Mock()

                mock_import.side_effect = import_side_effect

                args = Mock()
                args.agent = "test"
                config_data = {}

                with patch("agent_manager.cli_extensions.agent_commands.message"):
                    with pytest.raises(SystemExit):
                        AgentCommands.process_cli_command(args, config_data)

    def test_processes_run_command_agent_error(self):
        """Test handling of agent initialization errors."""
        with patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins") as mock_discover:
            with patch("agent_manager.cli_extensions.agent_commands.importlib.import_module") as mock_import:
                mock_discover.return_value = {"test": "ai_agent_test"}

                mock_module = Mock()
                mock_module.Agent.side_effect = Exception("Init failed")
                mock_import.return_value = mock_module

                args = Mock()
                args.agent = "test"
                config_data = {}

                with patch("agent_manager.cli_extensions.agent_commands.message"):
                    with pytest.raises(SystemExit):
                        AgentCommands.process_cli_command(args, config_data)


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

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_list_agents_with_plugins(self, mock_discover):
        """Test listing agents when plugins are available."""
        mock_discover.return_value = {"claude": "ai_agent_claude", "custom": "ai_agent_custom"}

        messages = []

        def capture_message(text, *args, **kwargs):
            messages.append(text)

        with patch("agent_manager.cli_extensions.agent_commands.message", side_effect=capture_message):
            AgentCommands.list_agents()

        # Check that agents are listed
        output = "\n".join(messages)
        assert "claude" in output
        assert "ai_agent_claude" in output
        assert "custom" in output
        assert "ai_agent_custom" in output
        assert "Total: 2 agent(s)" in output

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
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
        assert "ai_agent_" in output  # Should mention the plugin naming convention

    @patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins")
    def test_list_agents_sorted(self, mock_discover):
        """Test that agents are listed in sorted order."""
        mock_discover.return_value = {"zebra": "ai_agent_zebra", "alpha": "ai_agent_alpha", "middle": "ai_agent_middle"}

        messages = []

        def capture_message(text, *args, **kwargs):
            messages.append(text)

        with patch("agent_manager.cli_extensions.agent_commands.message", side_effect=capture_message):
            AgentCommands.list_agents()

        # Find lines that contain agent names
        agent_lines = [m for m in messages if "ai_agent_" in m and "(" in m]

        # Should be in alphabetical order
        assert len(agent_lines) == 3
        assert "alpha" in agent_lines[0]
        assert "middle" in agent_lines[1]
        assert "zebra" in agent_lines[2]


class TestAgentCommandsEdgeCases:
    """Test cases for edge cases and special scenarios."""

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_plugins_with_underscores(self, mock_distributions):
        """Test discovery of plugins with multiple underscores."""
        mock_dist = Mock()
        mock_dist.name = "ai-agent-my-custom-agent"
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        assert "my_custom_agent" in plugins
        assert plugins["my_custom_agent"] == "ai_agent_my_custom_agent"

    @patch("agent_manager.cli_extensions.agent_commands.importlib.metadata.distributions")
    def test_discovers_plugins_with_numbers(self, mock_distributions):
        """Test discovery of plugins with numbers."""
        mock_dist = Mock()
        mock_dist.name = "ai-agent-gpt4"
        mock_distributions.return_value = [mock_dist]

        plugins = AgentCommands.discover_plugins()

        assert "gpt4" in plugins
        assert plugins["gpt4"] == "ai_agent_gpt4"

    def test_processes_agents_sequentially(self):
        """Test that agents are processed sequentially."""
        with patch("agent_manager.cli_extensions.agent_commands.AgentCommands.discover_plugins") as mock_discover:
            with patch("agent_manager.cli_extensions.agent_commands.importlib.import_module") as mock_import:
                mock_discover.return_value = {"agent1": "ai_agent_agent1", "agent2": "ai_agent_agent2"}

                call_order = []

                def track_import(module_name):
                    # Only track our agent imports
                    if module_name.startswith("ai_agent_"):
                        call_order.append(f"import_{module_name}")
                        mock_agent = Mock()
                        mock_agent.update = lambda _: call_order.append(f"update_{module_name}")
                        mock_module = Mock()
                        mock_module.Agent = Mock(return_value=mock_agent)
                        return mock_module
                    return Mock()

                mock_import.side_effect = track_import

                args = Mock()
                args.agent = "all"
                config_data = {}

                with patch("agent_manager.cli_extensions.agent_commands.message"):
                    AgentCommands.process_cli_command(args, config_data)

                # Verify sequential processing - should have 4 calls (import+update for each agent)
                assert len(call_order) == 4
                assert "import_ai_agent_agent1" in call_order
                assert "update_ai_agent_agent1" in call_order
                assert "import_ai_agent_agent2" in call_order
                assert "update_ai_agent_agent2" in call_order

                # Verify ordering - agent1 should complete before agent2 starts
                agent1_import_idx = call_order.index("import_ai_agent_agent1")
                agent1_update_idx = call_order.index("update_ai_agent_agent1")
                agent2_import_idx = call_order.index("import_ai_agent_agent2")
                assert agent1_import_idx < agent1_update_idx < agent2_import_idx
