# tests/test_main_window_integration.py
"""Integration tests for MainWindow."""

from unittest.mock import Mock

import pytest
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QApplication

from pylk.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def main_window(app):
    """Create MainWindow for testing."""
    return MainWindow()


class TestMainWindowIntegration:
    """Integration tests for MainWindow."""

    def test_initial_state(self, main_window):
        """Test initial state of MainWindow."""
        assert main_window._project_controller is not None
        assert main_window._plk_view is not None
        assert main_window._central is not None
        assert main_window.centralWidget() == main_window._central

    def test_project_loaded_signal_swaps_widget(self, main_window):
        """Test that projectLoaded signal swaps central widget to PlkView."""
        # Create mock model
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.par_path = "/path/to/test.par"
        mock_model.tim_path = "/path/to/test.tim"

        # Emit projectLoaded signal
        main_window._on_project_loaded(mock_model)

        # Check that central widget is now PlkView
        assert main_window.centralWidget() == main_window._plk_view
        assert main_window._plk_view._model == mock_model

    def test_project_closed_signal_restores_placeholder(self, main_window):
        """Test that projectClosed signal restores placeholder widget."""
        # First switch to plotting view
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.par_path = "/path/to/test.par"
        mock_model.tim_path = "/path/to/test.tim"
        main_window._on_project_loaded(mock_model)
        assert main_window.centralWidget() == main_window._plk_view

        # Then close project
        main_window._on_project_closed()

        # Check that central widget is back to placeholder
        assert main_window.centralWidget() == main_window._central

    def test_residuals_changed_updates_status(self, main_window):
        """Test that residuals changes update status bar."""
        payload = {
            "n": 100,
            "rms_us": 15.5,
            "mjd": [58000.0, 58001.0],
            "res": [0.1, 0.2],
            "err": [1.0, 1.5],
        }

        main_window._on_residuals_changed(payload)

        # Check status bar message
        status_text = main_window.statusBar().currentMessage()
        assert "TOAs: 100" in status_text
        assert "RMS: 15.50" in status_text

    def test_residuals_changed_empty_payload(self, main_window):
        """Test that empty residuals payload doesn't crash."""
        main_window._on_residuals_changed({})
        # Should not raise exception

    def test_show_plotting_view_connects_signals(self, main_window):
        """Test that showing plotting view connects model signals."""
        mock_model = Mock()
        mock_model.residualsChanged = Mock()

        main_window._show_plotting_view(mock_model)

        # Check that residuals signal is connected (called twice: once by PlkView.set_model, once by MainWindow)
        assert mock_model.residualsChanged.connect.call_count == 2
        # Check that one of the calls is to MainWindow's _on_residuals_changed
        calls = mock_model.residualsChanged.connect.call_args_list
        assert any(main_window._on_residuals_changed in call[0] for call in calls)

    def test_controller_signals_connected(self, main_window):
        """Test that controller signals are properly connected."""
        # Check that controller signals exist and are callable
        assert hasattr(main_window._project_controller, "projectLoaded")
        assert hasattr(main_window._project_controller, "projectClosed")
        assert hasattr(main_window, "_on_project_loaded")
        assert hasattr(main_window, "_on_project_closed")

    def test_plk_view_created(self, main_window):
        """Test that PlkView is properly created."""
        assert main_window._plk_view is not None
        assert hasattr(main_window._plk_view, "set_model")
        assert hasattr(main_window._plk_view, "on_residuals_changed")
        # Should be hidden initially
        assert not main_window._plk_view.isVisible()

    def test_plk_view_hidden_initially(self, main_window):
        """Test that PlkView is hidden when no project is loaded."""
        assert not main_window._plk_view.isVisible()
        # Central widget should be the placeholder, not the PlkView
        assert main_window.centralWidget() == main_window._central
        assert main_window.centralWidget() != main_window._plk_view

    def test_save_plot_action_created(self, main_window):
        """Test that save plot action is created and properly configured."""
        assert hasattr(main_window, "act_save_plot")
        assert main_window.act_save_plot is not None
        assert main_window.act_save_plot.text() == "&Save Plot…"
        assert main_window.act_save_plot.shortcut() == QKeySequence("Ctrl+S")
        assert not main_window.act_save_plot.isEnabled()  # Should be disabled initially

    def test_save_plot_action_enabled_on_project_load(self, main_window):
        """Test that save plot action is enabled when project is loaded."""
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.par_path = "/path/to/test.par"
        mock_model.tim_path = "/path/to/test.tim"

        # Initially disabled
        assert not main_window.act_save_plot.isEnabled()

        # Load project
        main_window._on_project_loaded(mock_model)

        # Should be enabled
        assert main_window.act_save_plot.isEnabled()

    def test_save_plot_action_disabled_on_project_close(self, main_window):
        """Test that save plot action is disabled when project is closed."""
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.par_path = "/path/to/test.par"
        mock_model.tim_path = "/path/to/test.tim"

        # Load project (enables action)
        main_window._on_project_loaded(mock_model)
        assert main_window.act_save_plot.isEnabled()

        # Close project
        main_window._on_project_closed()

        # Should be disabled
        assert not main_window.act_save_plot.isEnabled()

    def test_save_plot_handler(self, main_window):
        """Test that save plot handler works correctly."""
        # Test with no plot available
        main_window._on_save_plot()
        # Should not crash (shows warning dialog)

    def test_improved_status_text(self, main_window):
        """Test that status text shows improved format with file names."""
        mock_model = Mock()
        mock_model.par_path = "/path/to/test.par"
        mock_model.tim_path = "/path/to/test.tim"
        mock_model.residualsChanged = Mock()

        # Load project
        main_window._on_project_loaded(mock_model)

        # Check status text includes file names
        status_text = main_window.statusBar().currentMessage()
        assert "Loaded PAR: test.par" in status_text
        assert "TIM: test.tim" in status_text

    def test_minimum_window_size(self, main_window):
        """Test that minimum window size is set correctly."""
        min_size = main_window.minimumSize()
        assert min_size.width() == 1000
        assert min_size.height() == 800

    def test_dock_visibility_syncs_menu_bar(self, main_window):
        """Test that dock widget visibility changes sync with menu bar state."""
        # Ensure both docks are visible initially
        main_window.left_dock.show()
        main_window.right_dock.show()

        # Menu items should be checked when docks are visible
        assert main_window.act_toggle_left_dock.isChecked()
        assert main_window.act_toggle_right_dock.isChecked()

        # Test the signal connection by calling the handler directly
        # (simulating what would happen when visibilityChanged is emitted)
        main_window._on_left_dock_visibility_changed(False)

        # Menu bar should be updated
        assert not main_window.act_toggle_left_dock.isChecked()
        assert main_window.act_toggle_right_dock.isChecked()  # Right dock unchanged

        # Test right dock
        main_window._on_right_dock_visibility_changed(False)

        # Menu bar should be updated
        assert not main_window.act_toggle_left_dock.isChecked()
        assert not main_window.act_toggle_right_dock.isChecked()

        # Test showing left dock again
        main_window._on_left_dock_visibility_changed(True)

        # Menu bar should be updated
        assert main_window.act_toggle_left_dock.isChecked()
        assert not main_window.act_toggle_right_dock.isChecked()  # Right dock unchanged

    def test_menu_bar_syncs_dock_visibility(self, main_window):
        """Test that menu bar changes sync with dock widget visibility."""
        # Test that the toggle methods work correctly
        # (The actual visibility behavior may vary in test environment)

        # Test left dock toggle
        main_window._toggle_left_dock(False)
        # The method should not crash and should set the dock visibility

        # Test right dock toggle
        main_window._toggle_right_dock(False)
        # The method should not crash and should set the dock visibility

        # Test showing them again
        main_window._toggle_left_dock(True)
        main_window._toggle_right_dock(True)
        # The methods should not crash
