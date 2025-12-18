"""CLI commands for managing AI agent plugins."""

import argparse
import sys

from agent_manager.core import discover_agent_plugins, get_agent_names, run_agents
from agent_manager.output import MessageType, VerbosityLevel, message


class AgentCommands:
    """Manages CLI commands for AI agent plugins."""

    @classmethod
    def add_cli_arguments(cls, subparsers) -> None:
        """Add agent-related CLI arguments.

        Args:
            subparsers: The argparse subparsers to add to
        """
        # Discover available plugins for the choices
        agent_plugin_names = get_agent_names()

        # Agents command group
        agents_parser = subparsers.add_parser("agents", help="Manage agent plugins")
        agents_subparsers = agents_parser.add_subparsers(dest="agents_command", help="Agent commands")

        # agents list
        agents_subparsers.add_parser("list", help="List available agent plugins")

        # Run command (default action)
        run_parser = subparsers.add_parser("run", help="Run an agent (default command)")
        run_parser.add_argument(
            "--agent",
            type=str,
            default="all",
            choices=["all"] + agent_plugin_names,
            help="Agent plugin to use (default: all agents)",
        )

    @classmethod
    def process_agents_command(cls, args: argparse.Namespace) -> None:
        """Process agents-related CLI commands.

        Args:
            args: Parsed command-line arguments
        """
        if not hasattr(args, "agents_command") or args.agents_command is None:
            message("No agents subcommand specified", MessageType.ERROR, VerbosityLevel.ALWAYS)
            message("Available commands: list", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            sys.exit(1)

        if args.agents_command == "list":
            cls.list_agents()

    @classmethod
    def list_agents(cls) -> None:
        """List all available agent plugins."""
        message("\n=== Available Agent Plugins ===\n", MessageType.NORMAL, VerbosityLevel.ALWAYS)

        plugins = discover_agent_plugins()

        if not plugins:
            message("No agent plugins found.", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            message(
                "\nTo install an agent plugin, use: pip install <plugin-package>",
                MessageType.NORMAL,
                VerbosityLevel.ALWAYS,
            )
            message("Agent plugins have package names starting with 'am_agent_'", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            message("", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            return

        message("Installed agents:", MessageType.NORMAL, VerbosityLevel.ALWAYS)
        for agent_name in sorted(plugins.keys()):
            package_name = plugins[agent_name]["package_name"]
            message(f"  {agent_name} ({package_name})", MessageType.NORMAL, VerbosityLevel.ALWAYS)

        message("", MessageType.NORMAL, VerbosityLevel.ALWAYS)
        message(f"Total: {len(plugins)} agent(s) available", MessageType.NORMAL, VerbosityLevel.ALWAYS)
        message("", MessageType.NORMAL, VerbosityLevel.ALWAYS)

    @classmethod
    def process_cli_command(cls, args, config_data: dict) -> None:
        """Process the run command for agents.

        Args:
            args: Parsed command-line arguments
            config_data: Configuration data with repo objects
        """
        # Determine which agents to run
        agents_to_run = [args.agent] if args.agent != "all" else ["all"]

        # Use the core module to run agents
        run_agents(agents_to_run, config_data)
