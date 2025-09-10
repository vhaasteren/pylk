# pylk/models/pulsar.py
"""Pulsar data model using PINT."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

import numpy as np
from qtpy.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

# Try to import PINT, handle gracefully if not available
try:
    import pint  # type: ignore[import-untyped]
    from pint.models import get_model_and_toas  # type: ignore[import-untyped]
    from pint.residuals import Residuals  # type: ignore[import-untyped]

    PINT_AVAILABLE = True
except ImportError:
    PINT_AVAILABLE = False

    # Create dummy classes for type hints
    class _DummyPint:
        class models:
            @staticmethod
            def get_model_and_toas(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
                raise ImportError("PINT not available")

        class residuals:
            class Residuals:
                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    raise ImportError("PINT not available")

    # Create module-like objects
    pint = _DummyPint()
    get_model_and_toas = pint.models.get_model_and_toas
    Residuals = pint.residuals.Residuals


class PulsarModel(QObject):
    """Model for pulsar data loaded from PAR+TIM files."""

    # Signals
    modelChanged = Signal()
    toasChanged = Signal()
    residualsChanged = Signal(dict)  # payload: {mjd, res, err, rms_us, n}

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._model: Any = None
        self._toas: Any = None
        self._residuals: Any = None
        self._par_path: str | None = None
        self._tim_path: str | None = None

    @property
    def model(self) -> Any:
        """The loaded timing model."""
        return self._model

    @property
    def toas(self) -> Any:
        """The loaded TOAs."""
        return self._toas

    @property
    def residuals(self) -> Any:
        """The pre-fit residuals."""
        return self._residuals

    @property
    def par_path(self) -> str | None:
        """Path to the loaded PAR file."""
        return self._par_path

    @property
    def tim_path(self) -> str | None:
        """Path to the loaded TIM file."""
        return self._tim_path

    @property
    def is_loaded(self) -> bool:
        """True if both PAR and TIM files are loaded."""
        return self._model is not None and self._toas is not None

    def load(
        self, par_path: str, tim_path: str, fitter: str = "auto", ephem: str | None = None
    ) -> None:
        """Load PAR and TIM files using PINT.

        Args:
            par_path: Path to PAR file
            tim_path: Path to TIM file
            fitter: Fitter type (default: "auto")
            ephem: Ephemeris to use (default: None for PINT default)
        """
        if not PINT_AVAILABLE:
            raise ImportError("PINT is not available")

        try:
            par_path = str(Path(par_path).resolve())
            tim_path = str(Path(tim_path).resolve())

            logger.info(f"Loading PAR file: {par_path}")
            logger.info(f"Loading TIM file: {tim_path}")

            # Use PINT's robust loading function
            self._model, self._toas = get_model_and_toas(par_path, tim_path)

            self._par_path = par_path
            self._tim_path = tim_path

            logger.info(f"Successfully loaded model: {self._model.PSR.value}")
            logger.info(f"Loaded {len(self._toas)} TOAs")

            # Emit signals
            self.modelChanged.emit()
            self.toasChanged.emit()

            # Compute and emit residuals
            self.compute_prefit_residuals()

        except Exception as e:
            logger.error(f"Failed to load project: {e}", exc_info=True)
            self.clear()
            raise

    def compute_prefit_residuals(self) -> dict[str, Any]:
        """Compute pre-fit residuals and emit residualsChanged signal.

        Returns:
            dict with keys: mjd, res, err, rms_us, n
        """
        if not self.is_loaded:
            logger.warning("No model or TOAs loaded")
            return {}

        try:
            # Compute residuals
            self._residuals = Residuals(self._toas, self._model)

            # Extract data as plain numpy arrays
            mjd = self._toas.get_mjds().value  # Convert to plain numpy array
            res_us = self._residuals.time_resids.to("us").value  # Convert to microseconds
            err_us = self._toas.get_errors().to("us").value  # Convert to microseconds

            # Compute RMS
            rms_us = float(np.sqrt(np.mean(res_us**2)))
            n = len(mjd)

            payload = {"mjd": mjd, "res": res_us, "err": err_us, "rms_us": rms_us, "n": n}

            logger.info(f"Computed residuals: {n} points, RMS = {rms_us:.2f} μs")
            self.residualsChanged.emit(payload)
            return payload

        except Exception as e:
            logger.error(f"Failed to compute residuals: {e}", exc_info=True)
            return {}

    def clear(self) -> None:
        """Clear loaded data."""
        self._model = None
        self._toas = None
        self._residuals = None
        self._par_path = None
        self._tim_path = None

    def hash_model_params(self) -> str:
        """Compute hash of model parameters."""
        if not self._model:
            return ""

        try:
            # Get model parameters as string and hash
            model_str = str(self._model.params)
            return hashlib.md5(model_str.encode()).hexdigest()[:8]
        except Exception:
            return ""

    def hash_toas(self) -> str:
        """Compute hash of TOAs."""
        if not self._toas:
            return ""

        try:
            # Hash based on MJDs and errors
            mjd_str = str(self._toas.get_mjds().value)
            err_str = str(self._toas.get_errors().value)
            combined = mjd_str + err_str
            return hashlib.md5(combined.encode()).hexdigest()[:8]
        except Exception:
            return ""

    def hash_residuals(self) -> str:
        """Compute hash of residuals."""
        if not self._residuals:
            return ""

        try:
            res_str = str(self._residuals.time_resids.value)
            return hashlib.md5(res_str.encode()).hexdigest()[:8]
        except Exception:
            return ""
