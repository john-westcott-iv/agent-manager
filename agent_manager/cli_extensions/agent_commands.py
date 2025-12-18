"""CLI commands for managing AI agent plugins."""

import argparse
import importlib
import importlib.metadata
import sys

from agent_manager.output import MessageType, VerbosityLevel, message


class AgentCommands:
    """Manages CLI commands for AI agent plugins."""

    AGENT_PLUGIN_PREFIX = "ai_agent_"

    @classmethod
    def discover_plugins(cls) -> dict[str, str]:
        """Discover available agent plugins.

        Uses importlib.metadata to find installed packages that start with 'ai_agent_'.
        This works with both regular and editable installs.

        Returns:
            Dictionary mapping agent names to their full module names
        """
        plugins = {}
        try:
            # Get all installed distributions
            for dist in importlib.metadata.distributions():
                # Get the package name (normalized to use underscores)
                package_name = dist.name.replace("-", "_")

                if package_name.startswith(cls.AGENT_PLUGIN_PREFIX):
                    agent_name = package_name.replace(cls.AGENT_PLUGIN_PREFIX, "", 1)
                    plugins[agent_name] = package_name
                    message(
                        f"Discovered agent plugin: {agent_name} ({package_name})",
                        MessageType.DEBUG,
                        VerbosityLevel.DEBUG,
                    )
        except Exception as e:
            message(f"Failed to discover plugins: {e}", MessageType.ERROR, VerbosityLevel.ALWAYS)
            sys.exit(1)
        return plugins

    @classmethod
    def add_cli_arguments(cls, subparsers) -> None:
        """Add agent-related CLI arguments.

        Args:
            subparsers: The argparse subparsers to add to
        """
        # Discover available plugins for the choices
        available_plugins = cls.discover_plugins()
        agent_plugin_names = list(available_plugins.keys())

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

        plugins = cls.discover_plugins()

        if not plugins:
            message("No agent plugins found.", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            message(
                "\nTo install an agent plugin, use: pip install <plugin-package>",
                MessageType.NORMAL,
                VerbosityLevel.ALWAYS,
            )
            message("Agent plugins have package names starting with 'ai_agent_'", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            message("", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            return

        message("Installed agents:", MessageType.NORMAL, VerbosityLevel.ALWAYS)
        for agent_name, package_name in sorted(plugins.items()):
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
        # Discover available plugins
        available_plugins = cls.discover_plugins()
        agent_plugin_names = list(available_plugins.keys())

        # Determine which agents to run
        agents_to_run = agent_plugin_names if args.agent == "all" else [args.agent]

        # Check if we have any agents
        if not agents_to_run:
            message("No agent plugins found", MessageType.ERROR, VerbosityLevel.ALWAYS)
            message(
                "Please install an agent plugin (e.g., pip install -e ai_agent_claude)",
                MessageType.NORMAL,
                VerbosityLevel.ALWAYS,
            )
            sys.exit(1)

        # Run each agent
        for agent in agents_to_run:
            # Get the module name (guaranteed to exist due to argparse choices)
            agent_module_name = available_plugins[agent]

            message(f"\nInitializing agent: {agent}", MessageType.NORMAL, VerbosityLevel.ALWAYS)
            message(f"Loading agent plugin: {agent_module_name}", MessageType.DEBUG, VerbosityLevel.DEBUG)

            try:
                # Import the agent module
                agent_module = importlib.import_module(agent_module_name)

                # Initialize agent
                agent_class = agent_module.Agent()
                agent_class.update(config_data)

            except Exception as e:
                message(f"Failed to initialize agent '{agent}': {e}", MessageType.ERROR, VerbosityLevel.ALWAYS)
                sys.exit(1)
