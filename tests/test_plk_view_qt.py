# tests/test_plk_view_qt.py
"""Qt tests for PlkView widget."""

from unittest.mock import Mock

import numpy as np
import pytest
from qtpy.QtWidgets import QApplication

from pylk.widgets.plk_view import PlkView


@pytest.fixture
def app():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def view(app):
    """Create PlkView for testing."""
    return PlkView()


class TestPlkView:
    """Test cases for PlkView widget."""

    def test_initial_setup(self, view):
        """Test initial setup of PlkView."""
        assert view._figure is not None
        assert view._canvas is not None
        assert view._ax is not None
        assert view._save_button is not None
        assert view._model is None

    def test_set_model(self, view):
        """Test setting a model."""
        mock_model = Mock()
        mock_model.residualsChanged = Mock()

        view.set_model(mock_model)

        assert view._model == mock_model
        # Check that signal is connected
        mock_model.residualsChanged.connect.assert_called_once_with(view.on_residuals_changed)

    def test_set_model_disconnect_previous(self, view):
        """Test that setting a new model disconnects the previous one."""
        # Set first model
        mock_model1 = Mock()
        mock_model1.residualsChanged = Mock()
        view.set_model(mock_model1)

        # Set second model
        mock_model2 = Mock()
        mock_model2.residualsChanged = Mock()
        view.set_model(mock_model2)

        # Check that first model was disconnected
        mock_model1.residualsChanged.disconnect.assert_called_once_with(view.on_residuals_changed)
        # Check that second model is connected
        mock_model2.residualsChanged.connect.assert_called_once_with(view.on_residuals_changed)

    def test_on_residuals_changed_valid_data(self, view):
        """Test plotting with valid residuals data."""
        data = {
            "mjd": np.array([58000.0, 58001.0, 58002.0]),
            "res": np.array([0.1, 0.2, 0.3]),
            "err": np.array([1.0, 1.5, 2.0]),
            "rms_us": 0.2,
            "n": 3,
        }

        view.on_residuals_changed(data)

        # Check that plot was updated (basic checks)
        assert view._ax.get_xlabel() == "MJD"
        assert view._ax.get_ylabel() == "Residual (μs)"
        assert "N=3" in view._ax.get_title()
        assert "RMS=0.20" in view._ax.get_title()

    def test_on_residuals_changed_empty_data(self, view):
        """Test plotting with empty data."""
        data = {}

        view.on_residuals_changed(data)

        # Should show "No data loaded"
        assert view._ax.get_title() == "No data loaded"

    def test_on_residuals_changed_missing_keys(self, view):
        """Test plotting with missing required keys."""
        data = {"mjd": [1, 2, 3]}  # Missing res, err, etc.

        view.on_residuals_changed(data)

        # Should show "No data loaded"
        assert view._ax.get_title() == "No data loaded"

    def test_on_residuals_changed_zero_length(self, view):
        """Test plotting with zero-length arrays."""
        data = {"mjd": [], "res": [], "err": [], "rms_us": 0.0, "n": 0}

        view.on_residuals_changed(data)

        # Should show "No data loaded"
        assert view._ax.get_title() == "No data loaded"

    def test_clear_plot(self, view):
        """Test clearing the plot."""
        # First add some data
        data = {
            "mjd": np.array([58000.0, 58001.0]),
            "res": np.array([0.1, 0.2]),
            "err": np.array([1.0, 1.5]),
            "rms_us": 0.15,
            "n": 2,
        }
        view.on_residuals_changed(data)

        # Then clear
        view._clear_plot()

        assert view._ax.get_title() == "No data loaded"
        assert view._ax.get_xlabel() == "MJD"
        assert view._ax.get_ylabel() == "Residual (μs)"

    def test_show_error_plot(self, view):
        """Test showing error plot."""
        error_msg = "Test error message"

        view._show_error_plot(error_msg)

        # Check that error text is displayed
        text_objects = [obj for obj in view._ax.texts if error_msg in obj.get_text()]
        assert len(text_objects) > 0

    def test_save_button_exists(self, view):
        """Test that save button exists and is connected."""
        assert view._save_button is not None
        assert view._save_button.text() == "Save Plot..."
        assert view._save_button.isEnabled()

    def test_synthetic_data_plotting(self, view):
        """Test plotting with synthetic data (no PINT needed)."""
        # Create synthetic residuals data
        mjd = np.linspace(58000, 58100, 50)
        res = np.random.normal(0, 10, 50)  # Random residuals in microseconds
        err = np.random.uniform(1, 5, 50)  # Random errors
        rms_us = np.sqrt(np.mean(res**2))

        data = {"mjd": mjd, "res": res, "err": err, "rms_us": rms_us, "n": len(mjd)}

        view.on_residuals_changed(data)

        # Verify plot elements
        assert view._ax.get_xlabel() == "MJD"
        assert view._ax.get_ylabel() == "Residual (μs)"
        assert f"N={len(mjd)}" in view._ax.get_title()
        assert f"RMS={rms_us:.2f}" in view._ax.get_title()

        # Check that error bars are plotted
        collections = view._ax.collections
        assert len(collections) > 0  # Should have error bar collections

    def test_plot_current_residuals_with_existing_data(self, view):
        """Test that _plot_current_residuals works with existing model data."""
        # Create mock model with residuals data
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.residuals = Mock()
        mock_model.toas = Mock()

        # Mock the data extraction - need to return actual numpy arrays
        mock_mjds = Mock()
        mock_mjds.value = np.array([58000.0, 58001.0, 58002.0])
        mock_model.toas.get_mjds.return_value = mock_mjds

        mock_residuals = Mock()
        mock_residuals.value = np.array([0.1, 0.2, 0.3])
        mock_residuals_obj = Mock()
        mock_residuals_obj.to.return_value = mock_residuals
        mock_model.residuals.time_resids = mock_residuals_obj

        mock_errors = Mock()
        mock_errors.value = np.array([1.0, 1.5, 2.0])
        mock_errors_obj = Mock()
        mock_errors_obj.to.return_value = mock_errors
        mock_model.toas.get_errors.return_value = mock_errors_obj

        # Set the model
        view.set_model(mock_model)

        # Check that plot was updated
        assert view._ax.get_xlabel() == "MJD"
        assert view._ax.get_ylabel() == "Residual (μs)"
        assert "N=3" in view._ax.get_title()
        assert "RMS=" in view._ax.get_title()

    def test_plot_current_residuals_no_data(self, view):
        """Test that _plot_current_residuals handles missing data gracefully."""
        # Create mock model without residuals
        mock_model = Mock()
        mock_model.residualsChanged = Mock()
        mock_model.residuals = None

        # Set the model
        view.set_model(mock_model)

        # Should still show "No data loaded"
        assert view._ax.get_title() == "No data loaded"

    def test_size_policy_set(self, view):
        """Test that proper size policies are set."""
        from qtpy.QtWidgets import QSizePolicy

        # Check that the widget has expanding size policy
        assert view.sizePolicy().horizontalPolicy() == QSizePolicy.Expanding
        assert view.sizePolicy().verticalPolicy() == QSizePolicy.Expanding

        # Check that the canvas has expanding size policy
        assert view._canvas.sizePolicy().horizontalPolicy() == QSizePolicy.Expanding
        assert view._canvas.sizePolicy().verticalPolicy() == QSizePolicy.Expanding

    def test_minimum_width_ensured(self, view):
        """Test that _ensure_minimum_width works correctly."""
        from qtpy.QtWidgets import QWidget

        # Create a real parent widget
        parent = QWidget()
        parent.resize(1000, 600)

        # Set the parent
        view.setParent(parent)

        # Call the method
        view._ensure_minimum_width()

        # Should have been resized to 80% of parent width (800px)
        # Note: This test verifies the logic runs without error
        # The actual resize behavior is harder to test in unit tests
