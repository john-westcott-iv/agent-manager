"""Tests for mergers/yaml_merger.py - YAML file merger."""

import pytest
import yaml

from agent_manager.plugins.mergers.yaml_merger import YamlMerger


class TestYamlMerger:
    """Test cases for YamlMerger."""

    def test_merge_simple_yaml_objects(self):
        """Test merging simple YAML objects."""
        base = "name: App\nversion: '1.0'\n"
        new = "version: '2.0'\nauthor: John\n"
        source = "team"
        sources = ["org"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        assert data["name"] == "App"  # Preserved
        assert data["version"] == "2.0"  # Overridden
        assert data["author"] == "John"  # Added

    def test_merge_nested_yaml_objects(self):
        """Test deep merging of nested YAML objects."""
        base = "config:\n  port: 8080\n  host: localhost\n"
        new = "config:\n  port: 9000\n  timeout: 30\n"
        source = "personal"
        sources = ["org", "team"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        # Deep merge should preserve host, override port, add timeout
        assert data["config"]["host"] == "localhost"
        assert data["config"]["port"] == 9000
        assert data["config"]["timeout"] == 30

    def test_merge_with_lists_replaces_by_default(self):
        """Test that lists are replaced by default (MergeStrategy)."""
        base = "features:\n  - auth\n  - api\n"
        new = "features:\n  - ui\n  - admin\n"
        source = "team"
        sources = ["org"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        # Default strategy replaces lists
        assert data["features"] == ["ui", "admin"]

    def test_merge_with_custom_indent(self):
        """Test merge with custom indentation setting."""
        base = "a: 1\n"
        new = "b: 2\n"
        source = "org"
        sources = []

        result = YamlMerger.merge(base, new, source, sources, indent=4)

        # Result should be valid YAML
        data = yaml.safe_load(result)
        assert data == {"a": 1, "b": 2}

    def test_merge_with_custom_width(self):
        """Test merge with custom line width setting."""
        base = "a: 1\n"
        new = "b: 2\n"
        source = "team"
        sources = ["org"]

        result = YamlMerger.merge(base, new, source, sources, width=80)

        # Result should be valid YAML
        data = yaml.safe_load(result)
        assert data == {"a": 1, "b": 2}

    def test_merge_with_empty_base(self):
        """Test merge with empty base YAML."""
        base = "{}"
        new = "key: value\n"
        source = "org"
        sources = []

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        assert data == {"key": "value"}

    def test_merge_with_complex_nested_structure(self):
        """Test merge with complex nested YAML."""
        base = yaml.dump(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "admin"},
                },
                "cache": {"enabled": True},
            }
        )
        new = yaml.dump(
            {
                "database": {
                    "port": 5433,
                    "credentials": {"password": "secret"},
                    "pool_size": 10,
                },
                "logging": {"level": "INFO"},
            }
        )
        source = "personal"
        sources = ["org", "team"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        # Verify deep merge
        assert data["database"]["host"] == "localhost"  # Preserved
        assert data["database"]["port"] == 5433  # Overridden
        assert data["database"]["credentials"]["user"] == "admin"  # Preserved
        assert data["database"]["credentials"]["password"] == "secret"  # Added
        assert data["database"]["pool_size"] == 10  # Added
        assert data["cache"]["enabled"] is True  # Preserved
        assert data["logging"]["level"] == "INFO"  # Added

    def test_merge_with_invalid_yaml_fallback(self):
        """Test that invalid YAML falls back to copy strategy."""
        base = "valid: yaml\n"
        new = "not: valid: yaml::\n"
        source = "team"
        sources = ["org"]

        # Should not raise exception, fallback to copy
        result = YamlMerger.merge(base, new, source, sources)

        # Should return the new content as-is (copy strategy)
        assert result == new

    def test_merge_with_yaml_arrays_at_root(self):
        """Test merge when YAML is an array at root."""
        base = "- item1\n- item2\n"
        new = "- item3\n- item4\n"
        source = "team"
        sources = ["org"]

        # Should handle gracefully (replace since can't deep merge arrays at root)
        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        assert data == ["item3", "item4"]

    def test_deserialize_valid_yaml(self):
        """Test deserialize with valid YAML."""
        content = "key: value\nnumber: 42\n"

        result = YamlMerger.deserialize(content)

        assert result == {"key": "value", "number": 42}

    def test_deserialize_invalid_yaml(self):
        """Test deserialize with invalid YAML raises error."""
        content = "not: valid: yaml::\n"

        with pytest.raises(yaml.YAMLError):
            YamlMerger.deserialize(content)

    def test_serialize_dict(self):
        """Test serialize converts dict to YAML."""
        data = {"name": "Test", "value": 123}

        result = YamlMerger.serialize(data)

        assert yaml.safe_load(result) == data

    def test_serialize_with_custom_settings(self):
        """Test serialize with custom formatting."""
        data = {"key": "value", "nested": {"a": 1, "b": 2}}

        result = YamlMerger.serialize(data, indent=4, width=80)

        # Should be valid YAML
        assert yaml.safe_load(result) == data

    def test_file_extensions(self):
        """Test that YamlMerger declares proper extensions."""
        assert ".yaml" in YamlMerger.FILE_EXTENSIONS
        assert ".yml" in YamlMerger.FILE_EXTENSIONS

    def test_merge_preferences_structure(self):
        """Test that merge preferences are properly defined."""
        prefs = YamlMerger.merge_preferences()

        assert "indent" in prefs
        assert prefs["indent"]["type"] == "int"
        assert prefs["indent"]["default"] == 2
        assert prefs["indent"]["min"] == 2
        assert prefs["indent"]["max"] == 8

        assert "width" in prefs
        assert prefs["width"]["type"] == "int"
        assert prefs["width"]["default"] == 120
        assert prefs["width"]["min"] == 60
        assert prefs["width"]["max"] == 200

    def test_merge_preserves_yaml_types(self):
        """Test that YAML types are preserved (bool, null, etc)."""
        base = "enabled: true\ncount: null\nvalue: 0\n"
        new = "enabled: false\nname: null\n"
        source = "team"
        sources = ["org"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        assert data["enabled"] is False
        assert data["count"] is None
        assert data["value"] == 0
        assert data["name"] is None

    def test_merge_with_yaml_multiline_strings(self):
        """Test merge with YAML multiline strings."""
        base = "description: |\n  Line 1\n  Line 2\n"
        new = "description: |\n  New Line 1\n  New Line 2\n"
        source = "team"
        sources = ["org"]

        result = YamlMerger.merge(base, new, source, sources)
        data = yaml.safe_load(result)

        assert "New Line 1" in data["description"]
        assert "New Line 2" in data["description"]
