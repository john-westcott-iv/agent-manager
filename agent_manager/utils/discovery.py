"""Generic plugin discovery utilities for agent-manager."""

import importlib
import importlib.metadata

from agent_manager.output import MessageType, VerbosityLevel, message


def discover_external_plugins(
    plugin_type: str,
    package_prefix: str | None = None,
    entry_point_group: str | None = None,
    base_class: type | None = None,
) -> dict[str, dict]:
    """Discover external plugins via package prefix and/or entry points.

    This is a generic utility that can discover plugins using two methods:
    1. Package prefix: Finds installed packages starting with a specific prefix
       (e.g., 'am_agent_' for agent plugins)
    2. Entry points: Finds plugins registered under a specific entry point group
       (e.g., 'agent_manager.mergers' for merger plugins)

    Args:
        plugin_type: Human-readable name for logging (e.g., "agent", "merger")
        package_prefix: Package name prefix to search for (e.g., "am_agent_")
        entry_point_group: Entry point group name (e.g., "agent_manager.mergers")
        base_class: Optional base class to validate loaded classes against

    Returns:
        Dictionary mapping plugin names to plugin info dicts:
        {
            "plugin_name": {
                "package_name": "full_package_name",
                "class": <class object> (if entry point),
                "source": "package" | "entry_point"
            }
        }
    """
    plugins = {}

    # === Method 1: Discover by package prefix ===
    if package_prefix:
        plugins.update(
            _discover_by_package_prefix(
                plugin_type=plugin_type,
                package_prefix=package_prefix,
            )
        )

    # === Method 2: Discover by entry points ===
    if entry_point_group:
        plugins.update(
            _discover_by_entry_points(
                plugin_type=plugin_type,
                entry_point_group=entry_point_group,
                base_class=base_class,
            )
        )

    return plugins


def _discover_by_package_prefix(
    plugin_type: str,
    package_prefix: str,
) -> dict[str, dict]:
    """Discover plugins by scanning installed packages with a specific prefix.

    Args:
        plugin_type: Human-readable name for logging
        package_prefix: Package name prefix to search for

    Returns:
        Dictionary mapping plugin names to plugin info
    """
    plugins = {}

    try:
        for dist in importlib.metadata.distributions():
            # Normalize package name (hyphens to underscores)
            package_name = dist.name.replace("-", "_")

            if package_name.startswith(package_prefix):
                # Extract plugin name by removing the prefix
                plugin_name = package_name[len(package_prefix) :]

                plugins[plugin_name] = {
                    "package_name": package_name,
                    "source": "package",
                }

                message(
                    f"Discovered {plugin_type} plugin: {plugin_name} ({package_name})",
                    MessageType.DEBUG,
                    VerbosityLevel.DEBUG,
                )

    except Exception as e:
        message(
            f"Failed to discover {plugin_type} plugins by package prefix: {e}",
            MessageType.DEBUG,
            VerbosityLevel.DEBUG,
        )

    return plugins


def _discover_by_entry_points(
    plugin_type: str,
    entry_point_group: str,
    base_class: type | None = None,
) -> dict[str, dict]:
    """Discover plugins via entry points.

    Args:
        plugin_type: Human-readable name for logging
        entry_point_group: Entry point group name
        base_class: Optional base class to validate against

    Returns:
        Dictionary mapping plugin names to plugin info
    """
    plugins = {}

    try:
        entry_points = importlib.metadata.entry_points()

        # Get entry points for the specified group
        # Python 3.10+ uses select(), older versions use get()
        if hasattr(entry_points, "select"):
            eps = entry_points.select(group=entry_point_group)
        else:
            eps = entry_points.get(entry_point_group, [])

        for ep in eps:
            try:
                # Load the class from the entry point
                loaded_class = ep.load()

                # Validate against base class if provided
                if base_class is not None:
                    if not (isinstance(loaded_class, type) and issubclass(loaded_class, base_class)):
                        message(
                            f"Entry point '{ep.name}' does not point to a valid {plugin_type} class",
                            MessageType.WARNING,
                            VerbosityLevel.VERBOSE,
                        )
                        continue

                plugins[ep.name] = {
                    "package_name": ep.value.split(":")[0] if ":" in ep.value else ep.value,
                    "class": loaded_class,
                    "source": "entry_point",
                }

                message(
                    f"Discovered external {plugin_type} plugin: {ep.name}",
                    MessageType.DEBUG,
                    VerbosityLevel.DEBUG,
                )

            except Exception as e:
                message(
                    f"Failed to load {plugin_type} plugin '{ep.name}': {e}",
                    MessageType.WARNING,
                    VerbosityLevel.VERBOSE,
                )

    except Exception as e:
        message(
            f"Failed to discover {plugin_type} plugins via entry points: {e}",
            MessageType.DEBUG,
            VerbosityLevel.DEBUG,
        )

    return plugins


def load_plugin_class(plugin_info: dict, class_name: str = "Agent"):
    """Load a class from a plugin.

    Args:
        plugin_info: Plugin info dict from discover_external_plugins
        class_name: Name of the class to load from the module

    Returns:
        The loaded class

    Raises:
        ImportError: If the module or class cannot be loaded
    """
    # If class was already loaded via entry point, return it
    if "class" in plugin_info:
        return plugin_info["class"]

    # Otherwise, import the module and get the class
    module = importlib.import_module(plugin_info["package_name"])
    return getattr(module, class_name)

