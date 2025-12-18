"""Tests for mergers/copy_merger.py - Simple copy/replace merger."""

from agent_manager.plugins.mergers.copy_merger import CopyMerger


class TestCopyMerger:
    """Test cases for CopyMerger."""

    def test_merge_replaces_with_new_content(self):
        """Test that merge returns the new content, ignoring base."""
        base = "Old content from base"
        new = "New content to use"
        source = "personal"
        sources = ["org", "team"]

        result = CopyMerger.merge(base, new, source, sources)

        assert result == new
        assert result != base

    def test_merge_with_empty_base(self):
        """Test merge when base is empty."""
        base = ""
        new = "New content"
        source = "org"
        sources = []

        result = CopyMerger.merge(base, new, source, sources)

        assert result == new

    def test_merge_with_empty_new(self):
        """Test merge when new content is empty."""
        base = "Base content"
        new = ""
        source = "personal"
        sources = ["org"]

        result = CopyMerger.merge(base, new, source, sources)

        assert result == ""

    def test_merge_with_multiline_content(self):
        """Test merge with multiline content."""
        base = "Old Line A\nOld Line B\nOld Line C"
        new = "New Line 1\nNew Line 2"
        source = "team"
        sources = ["org"]

        result = CopyMerger.merge(base, new, source, sources)

        assert result == new
        assert "New Line 1" in result
        assert "Old Line A" not in result

    def test_merge_with_special_characters(self):
        """Test merge with special characters."""
        base = "Base with émojis 🎉"
        new = "New with spëcial çhars & symbols @#$%"
        source = "personal"
        sources = ["org", "team"]

        result = CopyMerger.merge(base, new, source, sources)

        assert result == new

    def test_merge_preferences_returns_empty(self):
        """Test that CopyMerger has no configurable preferences."""
        prefs = CopyMerger.merge_preferences()

        assert prefs == {}

    def test_file_extensions_attribute(self):
        """Test that CopyMerger defines FILE_EXTENSIONS."""
        assert hasattr(CopyMerger, "FILE_EXTENSIONS")
        assert isinstance(CopyMerger.FILE_EXTENSIONS, list)
