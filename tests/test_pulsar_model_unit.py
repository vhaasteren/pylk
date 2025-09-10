# tests/test_pulsar_model_unit.py
"""Unit tests for PulsarModel."""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from pylk.models.pulsar import PINT_AVAILABLE, PulsarModel


class TestPulsarModel:
    """Test cases for PulsarModel."""

    def test_initial_state(self):
        """Test initial state of PulsarModel."""
        model = PulsarModel()

        assert model.model is None
        assert model.toas is None
        assert model.residuals is None
        assert model.par_path is None
        assert model.tim_path is None
        assert not model.is_loaded

    def test_clear(self):
        """Test clearing model data."""
        model = PulsarModel()

        # Set some dummy data
        model._model = Mock()
        model._toas = Mock()
        model._residuals = Mock()
        model._par_path = "test.par"
        model._tim_path = "test.tim"

        model.clear()

        assert model.model is None
        assert model.toas is None
        assert model.residuals is None
        assert model.par_path is None
        assert model.tim_path is None

    def test_hash_methods_empty(self):
        """Test hash methods when no data is loaded."""
        model = PulsarModel()

        assert model.hash_model_params() == ""
        assert model.hash_toas() == ""
        assert model.hash_residuals() == ""

    def test_hash_methods_with_data(self):
        """Test hash methods with mock data."""
        model = PulsarModel()

        # Mock model with params
        mock_model = Mock()
        mock_model.params = {"F0": 1.0, "F1": -1e-15}
        model._model = mock_model

        # Mock TOAs
        mock_toas = Mock()
        mock_toas.get_mjds.return_value.value = np.array([58000.0, 58001.0])
        mock_toas.get_errors.return_value.value = np.array([1.0, 1.5])
        model._toas = mock_toas

        # Mock residuals
        mock_residuals = Mock()
        mock_residuals.time_resids.value = np.array([0.1, 0.2])
        model._residuals = mock_residuals

        # Test hash methods
        model_hash = model.hash_model_params()
        toas_hash = model.hash_toas()
        res_hash = model.hash_residuals()

        assert len(model_hash) == 8
        assert len(toas_hash) == 8
        assert len(res_hash) == 8
        assert model_hash != ""
        assert toas_hash != ""
        assert res_hash != ""

    @pytest.mark.xfail(not PINT_AVAILABLE, reason="PINT not available")
    def test_load_with_pint(self):
        """Test loading with PINT (xfail if PINT not available)."""
        model = PulsarModel()

        # This test would require actual PINT files
        # For now, just test that the method exists and raises ImportError when PINT unavailable
        if not PINT_AVAILABLE:
            with pytest.raises(ImportError, match="PINT is not available"):
                model.load("test.par", "test.tim")
        else:
            # If PINT is available, we'd need real test files
            pytest.skip("Need real PAR/TIM files for integration test")

    @pytest.mark.xfail(not PINT_AVAILABLE, reason="PINT not available")
    def test_compute_prefit_residuals_with_pint(self):
        """Test computing residuals with PINT (xfail if PINT not available)."""
        model = PulsarModel()

        if not PINT_AVAILABLE:
            # Test that it returns empty dict when not loaded
            result = model.compute_prefit_residuals()
            assert result == {}
        else:
            # If PINT is available, we'd need real test files
            pytest.skip("Need real PAR/TIM files for integration test")

    def test_compute_prefit_residuals_not_loaded(self):
        """Test computing residuals when no data is loaded."""
        model = PulsarModel()

        result = model.compute_prefit_residuals()
        assert result == {}

    @patch("pylk.models.pulsar.logger")
    def test_compute_prefit_residuals_error_handling(self, mock_logger):
        """Test error handling in compute_prefit_residuals."""
        model = PulsarModel()

        # Mock is_loaded to return True but set up for error
        model._model = Mock()
        model._toas = Mock()
        model._toas.get_mjds.return_value.value = np.array([58000.0])
        model._toas.get_errors.return_value.value = np.array([1.0])

        # Mock residuals to raise an error
        with patch("pylk.models.pulsar.Residuals", side_effect=Exception("Test error")):
            result = model.compute_prefit_residuals()
            assert result == {}
            mock_logger.error.assert_called()
