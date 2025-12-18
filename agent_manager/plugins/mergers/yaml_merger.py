"""YAML merger with deep dictionary merging."""

from typing import Any

import yaml

from .dict_merger import DictMerger


class YamlMerger(DictMerger):
    """Merger for YAML files with deep dictionary merging."""

    FILE_EXTENSIONS = [".yaml", ".yml"]

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define YAML merger preferences."""
        return {
            "indent": {
                "type": "int",
                "default": 2,
                "description": "Number of spaces for YAML indentation",
                "min": 2,
                "max": 8,
            },
            "width": {
                "type": "int",
                "default": 120,
                "description": "Maximum line width for YAML output",
                "min": 60,
                "max": 200,
            },
        }

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Deserialize YAML content.

        Args:
            content: YAML string

        Returns:
            Python object

        Raises:
            yaml.YAMLError: If content is invalid YAML
        """
        return yaml.safe_load(content)

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Serialize Python object to YAML.

        Args:
            data: Python object
            **settings: YAML formatting settings (indent, width)

        Returns:
            YAML string
        """
        # Get preferences with defaults
        prefs = cls.merge_preferences()
        indent = settings.get("indent", prefs["indent"]["default"])
        width = settings.get("width", prefs["width"]["default"])

        return yaml.dump(data, default_flow_style=False, sort_keys=False, indent=indent, width=width)
