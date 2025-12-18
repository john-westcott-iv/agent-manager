"""Tests for mergers/dict_merger.py - Dictionary merger with strategies."""

import pytest

from agent_manager.plugins.mergers.dict_merger import (
    DictMerger,
    ExtendListStrategy,
    MergeStrategy,
    ReplaceStrategy,
)


class TestMergeStrategy:
    """Test cases for the default MergeStrategy."""

    def test_merge_dict_deep_merges_nested_dicts(self):
        """Test that nested dictionaries are deep merged."""
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        new = {"a": {"c": 3, "e": 4}, "f": 5}

        result = MergeStrategy.merge_dict(base, new)

        # Should deep merge nested dict 'a'
        assert result["a"]["b"] == 1  # From base
        assert result["a"]["c"] == 3  # Overridden by new
        assert result["a"]["e"] == 4  # From new
        assert result["d"] == 3  # From base
        assert result["f"] == 5  # From new

    def test_merge_dict_overwrites_non_dict_values(self):
        """Test that non-dict values are overwritten."""
        base = {"a": 1, "b": 2}
        new = {"b": 3, "c": 4}

        result = MergeStrategy.merge_dict(base, new)

        assert result["a"] == 1
        assert result["b"] == 3  # Overwritten
        assert result["c"] == 4

    def test_merge_dict_with_empty_base(self):
        """Test merge with empty base dict."""
        base = {}
        new = {"a": 1, "b": 2}

        result = MergeStrategy.merge_dict(base, new)

        assert result == new

    def test_merge_dict_with_empty_new(self):
        """Test merge with empty new dict."""
        base = {"a": 1, "b": 2}
        new = {}

        result = MergeStrategy.merge_dict(base, new)

        assert result == base

    def test_merge_list_replaces_by_default(self):
        """Test that lists are replaced by default."""
        base = [1, 2, 3]
        new = [4, 5]

        result = MergeStrategy.merge_list(base, new)

        assert result == [4, 5]
        assert result != base

    def test_merge_list_with_empty_new(self):
        """Test list merge with empty new list."""
        base = [1, 2, 3]
        new = []

        result = MergeStrategy.merge_list(base, new)

        assert result == []

    def test_merge_value_replaces(self):
        """Test that values are replaced."""
        result = MergeStrategy.merge_value("old", "new")
        assert result == "new"

        result = MergeStrategy.merge_value(123, 456)
        assert result == 456

    def test_merge_dict_with_complex_nesting(self):
        """Test deep merging with complex nesting."""
        base = {
            "level1": {
                "level2": {"level3": {"a": 1, "b": 2}, "c": 3},
                "d": 4,
            }
        }
        new = {
            "level1": {
                "level2": {"level3": {"b": 20, "e": 5}, "f": 6},
                "g": 7,
            }
        }

        result = MergeStrategy.merge_dict(base, new)

        assert result["level1"]["level2"]["level3"]["a"] == 1  # Preserved
        assert result["level1"]["level2"]["level3"]["b"] == 20  # Overridden
        assert result["level1"]["level2"]["level3"]["e"] == 5  # Added
        assert result["level1"]["level2"]["c"] == 3  # Preserved
        assert result["level1"]["level2"]["f"] == 6  # Added
        assert result["level1"]["d"] == 4  # Preserved
        assert result["level1"]["g"] == 7  # Added


class TestExtendListStrategy:
    """Test cases for ExtendListStrategy."""

    def test_merge_list_extends_and_deduplicates(self):
        """Test that lists are extended and deduplicated."""
        base = [1, 2, 3]
        new = [3, 4, 5]

        result = ExtendListStrategy.merge_list(base, new)

        assert result == [1, 2, 3, 4, 5]
        assert len(result) == 5  # No duplicate 3

    def test_merge_list_preserves_order(self):
        """Test that order is preserved (base first, then new)."""
        base = ["a", "b"]
        new = ["c", "d"]

        result = ExtendListStrategy.merge_list(base, new)

        assert result == ["a", "b", "c", "d"]

    def test_merge_list_with_string_items(self):
        """Test extending lists with strings."""
        base = ["auth", "api"]
        new = ["ui", "auth"]  # "auth" is duplicate

        result = ExtendListStrategy.merge_list(base, new)

        assert result == ["auth", "api", "ui"]

    def test_merge_list_with_empty_base(self):
        """Test extend with empty base."""
        base = []
        new = [1, 2, 3]

        result = ExtendListStrategy.merge_list(base, new)

        assert result == [1, 2, 3]

    def test_merge_list_with_empty_new(self):
        """Test extend with empty new list."""
        base = [1, 2, 3]
        new = []

        result = ExtendListStrategy.merge_list(base, new)

        assert result == [1, 2, 3]

    def test_merge_dict_still_deep_merges(self):
        """Test that ExtendListStrategy still deep merges dicts."""
        base = {"a": {"b": 1}, "c": 2}
        new = {"a": {"d": 3}, "e": 4}

        result = ExtendListStrategy.merge_dict(base, new)

        # Should inherit deep merge behavior from parent
        assert result["a"]["b"] == 1
        assert result["a"]["d"] == 3
        assert result["c"] == 2
        assert result["e"] == 4


class TestReplaceStrategy:
    """Test cases for ReplaceStrategy."""

    def test_merge_dict_replaces_entirely(self):
        """Test that dicts are replaced entirely (no deep merge)."""
        base = {"a": 1, "b": 2, "c": 3}
        new = {"d": 4, "e": 5}

        result = ReplaceStrategy.merge_dict(base, new)

        # Should only have new dict's keys
        assert result == {"d": 4, "e": 5}
        assert "a" not in result
        assert "b" not in result
        assert "c" not in result

    def test_merge_dict_with_nested_values(self):
        """Test replace with nested dicts."""
        base = {"config": {"port": 8080, "host": "localhost"}}
        new = {"config": {"timeout": 30}}

        result = ReplaceStrategy.merge_dict(base, new)

        # Should replace, not merge
        assert result == {"config": {"timeout": 30}}
        assert "port" not in result["config"]
        assert "host" not in result["config"]

    def test_merge_list_still_replaces(self):
        """Test that ReplaceStrategy still replaces lists."""
        base = [1, 2, 3]
        new = [4, 5]

        result = ReplaceStrategy.merge_list(base, new)

        assert result == [4, 5]


class TestDictMerger:
    """Test cases for DictMerger base class."""

    def test_get_merge_strategy_returns_default(self):
        """Test that default strategy is returned."""
        strategy = DictMerger.get_merge_strategy()

        assert strategy == MergeStrategy

    def test_deserialize_not_implemented(self):
        """Test that deserialize raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            DictMerger.deserialize("{}")

    def test_serialize_not_implemented(self):
        """Test that serialize raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            DictMerger.serialize({})

    def test_merge_handles_non_dict_content(self):
        """Test that merge handles non-dict content gracefully."""
        # We can't test DictMerger.merge directly because it calls
        # deserialize/serialize which aren't implemented.
        # This is tested in the concrete implementations (JsonMerger, YamlMerger)
        pass


class TestMergeStrategyPathParameter:
    """Test that strategies accept path parameter for debugging."""

    def test_merge_dict_accepts_path(self):
        """Test that merge_dict accepts path parameter."""
        base = {"a": 1}
        new = {"b": 2}

        # Should not raise an error
        result = MergeStrategy.merge_dict(base, new, path="root")

        assert result == {"a": 1, "b": 2}

    def test_merge_list_accepts_path(self):
        """Test that merge_list accepts path parameter."""
        base = [1, 2]
        new = [3, 4]

        # Should not raise an error
        result = MergeStrategy.merge_list(base, new, path="root.items")

        assert result == [3, 4]

    def test_merge_value_accepts_path(self):
        """Test that merge_value accepts path parameter."""
        # Should not raise an error
        result = MergeStrategy.merge_value("old", "new", path="root.field")

        assert result == "new"
