"""Tests for utils/discovery.py - Generic plugin discovery utilities."""

from unittest.mock import Mock, patch

from agent_manager.utils.discovery import (
    discover_external_plugins,
    load_plugin_class,
    _discover_by_package_prefix,
    _discover_by_entry_points,
)


class TestDiscoverByPackagePrefix:
    """Test cases for _discover_by_package_prefix function."""

    @patch("agent_manager.utils.discovery.importlib.metadata.distributions")
    def test_discovers_single_plugin(self, mock_distributions):
        """Test discovery of single plugin by prefix."""
        mock_dist = Mock()
        mock_dist.name = "am-agent-claude"
        mock_distributions.return_value = [mock_dist]

        result = _discover_by_package_prefix("agent", "am_agent_")

        assert "claude" in result
        assert result["claude"]["package_name"] == "am_agent_claude"
        assert result["claude"]["source"] == "package"

    @patch("agent_manager.utils.discovery.importlib.metadata.distributions")
    def test_discovers_multiple_plugins(self, mock_distributions):
        """Test discovery of multiple plugins."""
        mock_dist1 = Mock()
        mock_dist1.name = "am-agent-claude"
        mock_dist2 = Mock()
        mock_dist2.name = "am-agent-custom"
        mock_dist3 = Mock()
        mock_dist3.name = "other-module"  # Should be ignored

        mock_distributions.return_value = [mock_dist1, mock_dist2, mock_dist3]

        result = _discover_by_package_prefix("agent", "am_agent_")

        assert len(result) == 2
        assert "claude" in result
        assert "custom" in result

    @patch("agent_manager.utils.discovery.importlib.metadata.distributions")
    def test_discovers_no_plugins(self, mock_distributions):
        """Test discovery when no matching plugins."""
        mock_dist = Mock()
        mock_dist.name = "other-module"
        mock_distributions.return_value = [mock_dist]

        result = _discover_by_package_prefix("agent", "am_agent_")

        assert result == {}

    @patch("agent_manager.utils.discovery.importlib.metadata.distributions")
    def test_normalizes_package_names(self, mock_distributions):
        """Test that hyphens are converted to underscores."""
        mock_dist = Mock()
        mock_dist.name = "am-agent-my-custom-plugin"
        mock_distributions.return_value = [mock_dist]

        result = _discover_by_package_prefix("agent", "am_agent_")

        assert "my_custom_plugin" in result
        assert result["my_custom_plugin"]["package_name"] == "am_agent_my_custom_plugin"

    @patch("agent_manager.utils.discovery.importlib.metadata.distributions")
    def test_handles_exception(self, mock_distributions):
        """Test that exceptions are handled gracefully."""
        mock_distributions.side_effect = Exception("Discovery failed")

        with patch("agent_manager.utils.discovery.message"):
            result = _discover_by_package_prefix("agent", "am_agent_")

        assert result == {}


class TestDiscoverByEntryPoints:
    """Test cases for _discover_by_entry_points function."""

    @patch("agent_manager.utils.discovery.importlib.metadata.entry_points")
    def test_discovers_via_entry_points(self, mock_entry_points):
        """Test discovery via entry points."""
        # Create a real class hierarchy for issubclass check
        class BaseClass:
            pass

        class MockClass(BaseClass):
            pass

        mock_ep = Mock()
        mock_ep.name = "smart_markdown"
        mock_ep.value = "am_merger_smart_markdown:SmartMarkdownMerger"
        mock_ep.load.return_value = MockClass

        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps

        with patch("agent_manager.utils.discovery.message"):
            result = _discover_by_entry_points("merger", "agent_manager.mergers", BaseClass)

        assert "smart_markdown" in result
        assert result["smart_markdown"]["class"] == MockClass
        assert result["smart_markdown"]["source"] == "entry_point"

    @patch("agent_manager.utils.discovery.importlib.metadata.entry_points")
    def test_handles_invalid_class(self, mock_entry_points):
        """Test handling of entry point that doesn't point to valid class."""
        mock_ep = Mock()
        mock_ep.name = "invalid"
        mock_ep.load.return_value = "not a class"

        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps

        base_class = type("BaseClass", (), {})

        with patch("agent_manager.utils.discovery.message"):
            result = _discover_by_entry_points("merger", "agent_manager.mergers", base_class)

        assert result == {}

    @patch("agent_manager.utils.discovery.importlib.metadata.entry_points")
    def test_handles_load_error(self, mock_entry_points):
        """Test handling of entry point load error."""
        mock_ep = Mock()
        mock_ep.name = "broken"
        mock_ep.load.side_effect = Exception("Load failed")

        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps

        with patch("agent_manager.utils.discovery.message"):
            result = _discover_by_entry_points("merger", "agent_manager.mergers", None)

        assert result == {}


class TestDiscoverExternalPlugins:
    """Test cases for discover_external_plugins function."""

    @patch("agent_manager.utils.discovery._discover_by_entry_points")
    @patch("agent_manager.utils.discovery._discover_by_package_prefix")
    def test_combines_both_methods(self, mock_prefix, mock_entry_points):
        """Test that both discovery methods are used."""
        mock_prefix.return_value = {"agent1": {"package_name": "am_agent_agent1", "source": "package"}}
        mock_entry_points.return_value = {"merger1": {"package_name": "am_merger_merger1", "source": "entry_point"}}

        result = discover_external_plugins(
            plugin_type="test",
            package_prefix="am_test_",
            entry_point_group="agent_manager.test",
        )

        assert "agent1" in result
        assert "merger1" in result

    @patch("agent_manager.utils.discovery._discover_by_entry_points")
    @patch("agent_manager.utils.discovery._discover_by_package_prefix")
    def test_only_package_prefix(self, mock_prefix, mock_entry_points):
        """Test with only package prefix method."""
        mock_prefix.return_value = {"agent1": {"package_name": "am_agent_agent1", "source": "package"}}

        result = discover_external_plugins(
            plugin_type="test",
            package_prefix="am_test_",
        )

        mock_prefix.assert_called_once()
        mock_entry_points.assert_not_called()
        assert "agent1" in result

    @patch("agent_manager.utils.discovery._discover_by_entry_points")
    @patch("agent_manager.utils.discovery._discover_by_package_prefix")
    def test_only_entry_points(self, mock_prefix, mock_entry_points):
        """Test with only entry points method."""
        mock_entry_points.return_value = {"merger1": {"package_name": "am_merger_merger1", "source": "entry_point"}}

        result = discover_external_plugins(
            plugin_type="test",
            entry_point_group="agent_manager.test",
        )

        mock_prefix.assert_not_called()
        mock_entry_points.assert_called_once()
        assert "merger1" in result


class TestLoadPluginClass:
    """Test cases for load_plugin_class function."""

    def test_returns_preloaded_class(self):
        """Test that preloaded class is returned directly."""
        mock_class = Mock()
        plugin_info = {"package_name": "some_package", "class": mock_class, "source": "entry_point"}

        result = load_plugin_class(plugin_info)

        assert result == mock_class

    @patch("agent_manager.utils.discovery.importlib.import_module")
    def test_imports_and_returns_class(self, mock_import):
        """Test that module is imported and class is retrieved."""
        mock_agent_class = Mock()
        mock_module = Mock()
        mock_module.Agent = mock_agent_class
        mock_import.return_value = mock_module

        plugin_info = {"package_name": "am_agent_claude", "source": "package"}

        result = load_plugin_class(plugin_info, "Agent")

        mock_import.assert_called_once_with("am_agent_claude")
        assert result == mock_agent_class

    @patch("agent_manager.utils.discovery.importlib.import_module")
    def test_raises_on_import_error(self, mock_import):
        """Test that ImportError is raised on failure."""
        mock_import.side_effect = ImportError("Module not found")

        plugin_info = {"package_name": "nonexistent", "source": "package"}

        with pytest.raises(ImportError):
            load_plugin_class(plugin_info, "Agent")


# Import pytest for the raises check
import pytest

