"""Tests for mergers/merger_registry.py - Merger registry system."""

from pathlib import Path

from agent_manager.core.merger_registry import MergerRegistry
from agent_manager.plugins.mergers.copy_merger import CopyMerger
from agent_manager.plugins.mergers.json_merger import JsonMerger
from agent_manager.plugins.mergers.markdown_merger import MarkdownMerger
from agent_manager.plugins.mergers.text_merger import TextMerger
from agent_manager.plugins.mergers.yaml_merger import YamlMerger


class TestMergerRegistry:
    """Test cases for MergerRegistry."""

    def test_init_default_merger_is_copy(self):
        """Test that default merger is CopyMerger."""
        registry = MergerRegistry()

        assert registry.default_merger == CopyMerger

    def test_register_filename(self):
        """Test registering merger for specific filename."""
        registry = MergerRegistry()

        registry.register_filename("config.json", JsonMerger)

        assert "config.json" in registry.filename_mergers
        assert registry.filename_mergers["config.json"] == JsonMerger

    def test_register_extension(self):
        """Test registering merger for file extension."""
        registry = MergerRegistry()

        registry.register_extension(".json", JsonMerger)

        assert ".json" in registry.extension_mergers
        assert registry.extension_mergers[".json"] == JsonMerger

    def test_register_extension_without_dot(self):
        """Test registering extension without leading dot adds it."""
        registry = MergerRegistry()

        registry.register_extension("json", JsonMerger)

        assert ".json" in registry.extension_mergers
        assert registry.extension_mergers[".json"] == JsonMerger

    def test_set_default_merger(self):
        """Test setting default fallback merger."""
        registry = MergerRegistry()

        registry.set_default_merger(TextMerger)

        assert registry.default_merger == TextMerger

    def test_get_merger_by_filename_priority(self):
        """Test that filename match has highest priority."""
        registry = MergerRegistry()
        registry.register_filename("mcp.json", MarkdownMerger)  # Specific
        registry.register_extension(".json", JsonMerger)  # Generic

        file_path = Path("mcp.json")
        merger = registry.get_merger(file_path)

        # Should use filename-specific merger
        assert merger == MarkdownMerger

    def test_get_merger_by_extension(self):
        """Test getting merger by extension."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)

        file_path = Path("config.json")
        merger = registry.get_merger(file_path)

        assert merger == JsonMerger

    def test_get_merger_falls_back_to_default(self):
        """Test fallback to default merger for unknown files."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)

        file_path = Path("unknown.xyz")
        merger = registry.get_merger(file_path)

        assert merger == CopyMerger  # Default

    def test_get_merger_with_multiple_extensions(self):
        """Test getting mergers for different extensions."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)
        registry.register_extension(".yaml", YamlMerger)
        registry.register_extension(".md", MarkdownMerger)

        assert registry.get_merger(Path("file.json")) == JsonMerger
        assert registry.get_merger(Path("file.yaml")) == YamlMerger
        assert registry.get_merger(Path("file.md")) == MarkdownMerger

    def test_get_merger_with_path_in_subdirectory(self):
        """Test that get_merger works with paths in subdirectories."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)

        file_path = Path("configs/subfolder/config.json")
        merger = registry.get_merger(file_path)

        assert merger == JsonMerger

    def test_list_registered_mergers(self):
        """Test listing all registered mergers."""
        registry = MergerRegistry()
        registry.register_filename("mcp.json", JsonMerger)
        registry.register_extension(".yaml", YamlMerger)
        registry.register_extension(".md", MarkdownMerger)

        registered = registry.list_registered_mergers()

        assert "mcp.json" in registered["filenames"]
        assert ".yaml" in registered["extensions"]
        assert ".md" in registered["extensions"]
        assert registered["default"] == "CopyMerger"

    def test_override_extension_merger(self):
        """Test that registering same extension twice overrides."""
        registry = MergerRegistry()
        registry.register_extension(".txt", TextMerger)
        registry.register_extension(".txt", MarkdownMerger)  # Override

        merger = registry.get_merger(Path("file.txt"))

        assert merger == MarkdownMerger  # Should use latest

    def test_override_filename_merger(self):
        """Test that registering same filename twice overrides."""
        registry = MergerRegistry()
        registry.register_filename("special.json", JsonMerger)
        registry.register_filename("special.json", YamlMerger)  # Override

        merger = registry.get_merger(Path("special.json"))

        assert merger == YamlMerger  # Should use latest

    def test_get_merger_with_no_extension(self):
        """Test getting merger for file with no extension."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)

        file_path = Path("README")  # No extension
        merger = registry.get_merger(file_path)

        assert merger == CopyMerger  # Falls back to default

    def test_get_merger_case_sensitive(self):
        """Test that extension matching is case-sensitive."""
        registry = MergerRegistry()
        registry.register_extension(".json", JsonMerger)

        # .JSON (uppercase) should not match
        file_path = Path("file.JSON")
        merger = registry.get_merger(file_path)

        # Will fall back to default since .JSON != .json
        assert merger == CopyMerger

    def test_register_multiple_extensions_for_same_merger(self):
        """Test registering multiple extensions for same merger."""
        registry = MergerRegistry()
        registry.register_extension(".yaml", YamlMerger)
        registry.register_extension(".yml", YamlMerger)

        assert registry.get_merger(Path("config.yaml")) == YamlMerger
        assert registry.get_merger(Path("config.yml")) == YamlMerger

    def test_empty_registry_uses_default(self):
        """Test that empty registry always returns default merger."""
        registry = MergerRegistry()

        merger1 = registry.get_merger(Path("file.json"))
        merger2 = registry.get_merger(Path("file.yaml"))
        merger3 = registry.get_merger(Path("README.md"))

        assert merger1 == CopyMerger
        assert merger2 == CopyMerger
        assert merger3 == CopyMerger
