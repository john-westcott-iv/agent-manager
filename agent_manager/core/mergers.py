"""Merger utilities for agent-manager."""

import importlib
import inspect
import pkgutil
from pathlib import Path

from agent_manager.output import MessageType, VerbosityLevel, message


def discover_merger_classes():
    """Dynamically discover all merger classes in the mergers package.

    Scans the plugins.mergers package for all classes that inherit from AbstractMerger
    (excluding AbstractMerger itself and CopyMerger which is the default fallback).

    Returns:
        List of merger classes
    """
    from agent_manager.plugins.mergers import AbstractMerger

    merger_classes = []

    # Get the mergers package path
    import agent_manager.plugins.mergers as mergers_package

    mergers_package_path = Path(mergers_package.__file__).parent

    # Iterate through all Python files in the mergers directory
    for module_info in pkgutil.iter_modules([str(mergers_package_path)]):
        module_name = module_info.name

        # Skip private modules, __init__, abstract_merger, dict_merger (base class), copy_merger, and manager
        if module_name.startswith("_") or module_name in [
            "abstract_merger",
            "dict_merger",  # Base class for JSON/YAML mergers
            "copy_merger",
            "manager",
            "merger_registry",
        ]:
            continue

        try:
            # Import the module
            module = importlib.import_module(f"agent_manager.plugins.mergers.{module_name}")

            # Find all classes in the module
            for _name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a subclass of AbstractMerger
                # (but not AbstractMerger itself)
                if issubclass(obj, AbstractMerger) and obj is not AbstractMerger and obj.__module__ == module.__name__:
                    merger_classes.append(obj)

        except ImportError:
            # Skip modules that can't be imported (e.g., missing dependencies)
            continue

    return merger_classes


def create_default_merger_registry():
    """Create a merger registry with auto-discovered built-in mergers.

    Automatically discovers and registers all merger classes in the
    agent_manager.plugins.mergers package based on their FILE_EXTENSIONS attribute.

    Returns:
        MergerRegistry with default mergers registered
    """
    from .merger_registry import MergerRegistry

    registry = MergerRegistry()

    # Auto-discover merger classes
    merger_classes = discover_merger_classes()

    # Register each merger for its declared file extensions
    for merger_class in merger_classes:
        if hasattr(merger_class, "FILE_EXTENSIONS") and merger_class.FILE_EXTENSIONS:
            for extension in merger_class.FILE_EXTENSIONS:
                registry.register_extension(extension, merger_class)
                message(
                    f"Auto-registered {merger_class.__name__} for extension: {extension}",
                    MessageType.DEBUG,
                    VerbosityLevel.DEBUG,
                )

    return registry
