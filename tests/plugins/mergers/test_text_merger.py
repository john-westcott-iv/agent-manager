"""Tests for mergers/text_merger.py - Text file merger."""

from agent_manager.plugins.mergers.text_merger import TextMerger


class TestTextMerger:
    """Test cases for TextMerger."""

    def test_merge_concatenates_with_separator(self):
        """Test that merge concatenates content with source marker."""
        base = "Base content"
        new = "New content"
        source = "team"
        sources = ["org"]

        result = TextMerger.merge(base, new, source, sources)

        assert "Base content" in result
        assert "New content" in result
        assert f"From: {source}" in result
        assert result.startswith(base)

    def test_merge_creates_proper_separator(self):
        """Test that separator is properly formatted."""
        base = "First"
        new = "Second"
        source = "personal"
        sources = ["org", "team"]

        result = TextMerger.merge(base, new, source, sources)

        # Should have the separator with source name
        assert "---" in result
        assert "From: personal" in result

    def test_merge_with_empty_base(self):
        """Test merge when base is empty."""
        base = ""
        new = "New content"
        source = "org"
        sources = []

        result = TextMerger.merge(base, new, source, sources)

        assert "New content" in result
        assert f"From: {source}" in result

    def test_merge_with_multiple_levels(self):
        """Test merging through multiple hierarchy levels."""
        # Simulate org -> team -> personal
        base1 = ""
        new1 = "Organization rules"
        result1 = TextMerger.merge(base1, new1, "org", [])

        new2 = "Team rules"
        result2 = TextMerger.merge(result1, new2, "team", ["org"])

        new3 = "Personal rules"
        result3 = TextMerger.merge(result2, new3, "personal", ["org", "team"])

        # All three should be present
        assert "Organization rules" in result3
        assert "Team rules" in result3
        assert "Personal rules" in result3

        # Check all source markers
        assert "From: org" in result3
        assert "From: team" in result3
        assert "From: personal" in result3

    def test_merge_preserves_newlines(self):
        """Test that newlines are properly preserved."""
        base = "Line 1\nLine 2"
        new = "Line 3\nLine 4"
        source = "team"
        sources = ["org"]

        result = TextMerger.merge(base, new, source, sources)

        assert "Line 1\nLine 2" in result
        assert "Line 3\nLine 4" in result

    def test_file_extensions(self):
        """Test that TextMerger declares .txt extension."""
        assert ".txt" in TextMerger.FILE_EXTENSIONS

    def test_merge_preferences_returns_empty(self):
        """Test that TextMerger has no configurable preferences."""
        prefs = TextMerger.merge_preferences()

        assert prefs == {}
