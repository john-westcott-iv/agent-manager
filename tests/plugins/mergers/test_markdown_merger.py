"""Tests for mergers/markdown_merger.py - Markdown file merger."""

from agent_manager.plugins.mergers.markdown_merger import MarkdownMerger


class TestMarkdownMerger:
    """Test cases for MarkdownMerger."""

    def test_merge_with_default_separator(self):
        """Test merge with default horizontal_rule separator."""
        base = "# Base Content"
        new = "# New Content"
        source = "team"
        sources = ["org"]

        result = MarkdownMerger.merge(base, new, source, sources)

        assert "# Base Content" in result
        assert "# New Content" in result
        assert "---" in result  # horizontal rule
        assert "Note to AI Agent" in result

    def test_merge_includes_ai_override_note(self):
        """Test that AI override note is included."""
        base = "Base"
        new = "New"
        source = "personal"
        sources = ["org", "team"]

        result = MarkdownMerger.merge(base, new, source, sources)

        assert "Note to AI Agent" in result
        assert f"from '{source}' overrides" in result

    def test_merge_with_heading_separator(self):
        """Test merge with heading separator style."""
        base = "Base content"
        new = "New content"
        source = "team"
        sources = ["org"]

        result = MarkdownMerger.merge(base, new, source, sources, separator_style="heading")

        assert f"## Configuration from: {source}" in result
        assert "Note to AI Agent" in result

    def test_merge_with_comment_separator(self):
        """Test merge with comment separator style."""
        base = "Base content"
        new = "New content"
        source = "personal"
        sources = ["org", "team"]

        result = MarkdownMerger.merge(base, new, source, sources, separator_style="comment")

        assert f"<!-- Configuration from: {source} -->" in result
        assert "Note to AI Agent" in result

    def test_merge_with_horizontal_rule_separator(self):
        """Test merge with explicit horizontal_rule separator."""
        base = "Base"
        new = "New"
        source = "org"
        sources = []

        result = MarkdownMerger.merge(base, new, source, sources, separator_style="horizontal_rule")

        assert "---" in result
        # Should have two --- (one separator, one in override note)
        assert result.count("---") >= 2

    def test_merge_hierarchical_content(self):
        """Test merging through multiple hierarchy levels."""
        # Org level
        base1 = ""
        new1 = "# Organization Standards"
        result1 = MarkdownMerger.merge(base1, new1, "org", [])

        # Team level
        new2 = "## Team Guidelines"
        result2 = MarkdownMerger.merge(result1, new2, "team", ["org"])

        # Personal level
        new3 = "### Personal Preferences"
        result3 = MarkdownMerger.merge(result2, new3, "personal", ["org", "team"])

        # All content should be present
        assert "# Organization Standards" in result3
        assert "## Team Guidelines" in result3
        assert "### Personal Preferences" in result3

        # Should have override notes for team and personal
        assert "from 'team' overrides" in result3
        assert "from 'personal' overrides" in result3

    def test_merge_preserves_markdown_formatting(self):
        """Test that markdown formatting is preserved."""
        base = "**Bold** and *italic* and `code`"
        new = "[Link](url) and ![image](img.png)"
        source = "team"
        sources = ["org"]

        result = MarkdownMerger.merge(base, new, source, sources)

        assert "**Bold**" in result
        assert "*italic*" in result
        assert "`code`" in result
        assert "[Link](url)" in result
        assert "![image](img.png)" in result

    def test_file_extensions(self):
        """Test that MarkdownMerger declares proper extensions."""
        assert ".md" in MarkdownMerger.FILE_EXTENSIONS
        assert ".markdown" in MarkdownMerger.FILE_EXTENSIONS

    def test_merge_preferences_structure(self):
        """Test that merge preferences are properly defined."""
        prefs = MarkdownMerger.merge_preferences()

        assert "separator_style" in prefs
        assert prefs["separator_style"]["type"] == "str"
        assert prefs["separator_style"]["default"] == "horizontal_rule"
        assert "choices" in prefs["separator_style"]
        assert "horizontal_rule" in prefs["separator_style"]["choices"]
        assert "heading" in prefs["separator_style"]["choices"]
        assert "comment" in prefs["separator_style"]["choices"]

    def test_merge_with_invalid_separator_uses_default(self):
        """Test that invalid separator style falls back gracefully."""
        base = "Base"
        new = "New"
        source = "team"
        sources = ["org"]

        # Should not raise an error, will use default behavior
        result = MarkdownMerger.merge(base, new, source, sources, separator_style="invalid_style")

        # Should still produce valid output
        assert "Base" in result
        assert "New" in result
