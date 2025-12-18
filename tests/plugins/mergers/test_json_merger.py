"""Tests for mergers/json_merger.py - JSON file merger."""

import json

import pytest

from agent_manager.plugins.mergers.json_merger import JsonMerger


class TestJsonMerger:
    """Test cases for JsonMerger."""

    def test_merge_simple_json_objects(self):
        """Test merging simple JSON objects."""
        base = '{"name": "App", "version": "1.0"}'
        new = '{"version": "2.0", "author": "John"}'
        source = "team"
        sources = ["org"]

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        assert data["name"] == "App"  # Preserved
        assert data["version"] == "2.0"  # Overridden
        assert data["author"] == "John"  # Added

    def test_merge_nested_json_objects(self):
        """Test deep merging of nested JSON objects."""
        base = '{"config": {"port": 8080, "host": "localhost"}}'
        new = '{"config": {"port": 9000, "timeout": 30}}'
        source = "personal"
        sources = ["org", "team"]

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        # Deep merge should preserve host, override port, add timeout
        assert data["config"]["host"] == "localhost"
        assert data["config"]["port"] == 9000
        assert data["config"]["timeout"] == 30

    def test_merge_with_lists_replaces_by_default(self):
        """Test that lists are replaced by default (MergeStrategy)."""
        base = '{"features": ["auth", "api"]}'
        new = '{"features": ["ui", "admin"]}'
        source = "team"
        sources = ["org"]

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        # Default strategy replaces lists
        assert data["features"] == ["ui", "admin"]

    def test_merge_with_custom_indent(self):
        """Test merge with custom indentation setting."""
        base = '{"a": 1}'
        new = '{"b": 2}'
        source = "org"
        sources = []

        result = JsonMerger.merge(base, new, source, sources, indent=4)

        # Result should use 4-space indent
        assert "    " in result  # 4 spaces
        data = json.loads(result)
        assert data == {"a": 1, "b": 2}

    def test_merge_with_sort_keys(self):
        """Test merge with sorted keys."""
        base = '{"zebra": 1, "apple": 2}'
        new = '{"banana": 3}'
        source = "team"
        sources = ["org"]

        result = JsonMerger.merge(base, new, source, sources, sort_keys=True)

        # Keys should be alphabetically sorted
        data = json.loads(result)
        keys = list(data.keys())
        assert keys == sorted(keys)
        assert keys == ["apple", "banana", "zebra"]

    def test_merge_with_empty_base(self):
        """Test merge with empty base JSON."""
        base = "{}"
        new = '{"key": "value"}'
        source = "org"
        sources = []

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        assert data == {"key": "value"}

    def test_merge_with_complex_nested_structure(self):
        """Test merge with complex nested JSON."""
        base = json.dumps(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "admin"},
                },
                "cache": {"enabled": True},
            }
        )
        new = json.dumps(
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

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        # Verify deep merge
        assert data["database"]["host"] == "localhost"  # Preserved
        assert data["database"]["port"] == 5433  # Overridden
        assert data["database"]["credentials"]["user"] == "admin"  # Preserved
        assert data["database"]["credentials"]["password"] == "secret"  # Added
        assert data["database"]["pool_size"] == 10  # Added
        assert data["cache"]["enabled"] is True  # Preserved
        assert data["logging"]["level"] == "INFO"  # Added

    def test_merge_with_invalid_json_fallback(self):
        """Test that invalid JSON falls back to copy strategy."""
        base = '{"valid": "json"}'
        new = "not valid json{{"
        source = "team"
        sources = ["org"]

        # Should not raise exception, fallback to copy
        result = JsonMerger.merge(base, new, source, sources)

        # Should return the new content as-is (copy strategy)
        assert result == new

    def test_merge_with_non_dict_json(self):
        """Test merge when JSON is not a dict (e.g., array)."""
        base = '["item1", "item2"]'
        new = '["item3", "item4"]'
        source = "team"
        sources = ["org"]

        # Should handle gracefully (replace since can't deep merge arrays at root)
        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        assert data == ["item3", "item4"]

    def test_deserialize_valid_json(self):
        """Test deserialize with valid JSON."""
        content = '{"key": "value", "number": 42}'

        result = JsonMerger.deserialize(content)

        assert result == {"key": "value", "number": 42}

    def test_deserialize_invalid_json(self):
        """Test deserialize with invalid JSON raises error."""
        content = "not valid json"

        with pytest.raises(json.JSONDecodeError):
            JsonMerger.deserialize(content)

    def test_serialize_dict(self):
        """Test serialize converts dict to JSON."""
        data = {"name": "Test", "value": 123}

        result = JsonMerger.serialize(data)

        assert json.loads(result) == data

    def test_serialize_with_custom_settings(self):
        """Test serialize with custom formatting."""
        data = {"z": 1, "a": 2}

        result = JsonMerger.serialize(data, indent=4, sort_keys=True)

        # Should be formatted
        assert "    " in result
        # Should be sorted
        assert result.index('"a"') < result.index('"z"')

    def test_file_extensions(self):
        """Test that JsonMerger declares .json extension."""
        assert ".json" in JsonMerger.FILE_EXTENSIONS

    def test_merge_preferences_structure(self):
        """Test that merge preferences are properly defined."""
        prefs = JsonMerger.merge_preferences()

        assert "indent" in prefs
        assert prefs["indent"]["type"] == "int"
        assert prefs["indent"]["default"] == 2
        assert prefs["indent"]["min"] == 0
        assert prefs["indent"]["max"] == 8

        assert "sort_keys" in prefs
        assert prefs["sort_keys"]["type"] == "bool"
        assert prefs["sort_keys"]["default"] is False

    def test_merge_preserves_json_types(self):
        """Test that JSON types are preserved (bool, null, etc)."""
        base = '{"enabled": true, "count": null, "value": 0}'
        new = '{"enabled": false, "name": null}'
        source = "team"
        sources = ["org"]

        result = JsonMerger.merge(base, new, source, sources)
        data = json.loads(result)

        assert data["enabled"] is False
        assert data["count"] is None
        assert data["value"] == 0
        assert data["name"] is None
