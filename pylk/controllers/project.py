# pylk/controllers/project.py
"""Project controller for managing pulsar data."""

from __future__ import annotations

from qtpy.QtCore import QObject, Signal

from ..models.pulsar import PulsarModel


class ProjectController(QObject):
    """Controller for managing project state and coordinating model/view."""

    # Signals
    projectLoaded = Signal(object)  # PulsarModel
    projectClosed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._model: PulsarModel | None = None

    @property
    def model(self) -> PulsarModel | None:
        """The current pulsar model."""
        return self._model

    @property
    def is_project_open(self) -> bool:
        """True if a project is currently open."""
        return self._model is not None and self._model.is_loaded

    def open_project(
        self, par_path: str, tim_path: str, fitter: str = "auto", ephem: str | None = None
    ) -> PulsarModel:
        """Open a project with PAR and TIM files.

        Args:
            par_path: Path to PAR file
            tim_path: Path to TIM file
            fitter: Fitter type (default: "auto")
            ephem: Ephemeris to use (default: None for PINT default)

        Returns:
            The loaded PulsarModel

        Raises:
            ImportError: If PINT is not available
            Exception: If loading fails
        """
        # Close any existing project
        self.close_project()

        # Create new model
        self._model = PulsarModel(self)

        # Load the project
        self._model.load(par_path, tim_path, fitter, ephem)

        # Emit signal
        self.projectLoaded.emit(self._model)

        return self._model

    def close_project(self) -> None:
        """Close the current project."""
        if self._model:
            self._model.clear()
            self._model = None
            self.projectClosed.emit()
