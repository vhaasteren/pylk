# pylk/main_window.py
from __future__ import annotations

from qtpy.QtCore import QByteArray, QSettings, Qt
from qtpy.QtGui import QAction, QKeySequence
from qtpy.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .controllers.project import ProjectController
from .widgets.plk_view import PlkView


class CentralPlaceholder(QWidget):
    """Temporary central widget until plotting/view panes are added."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        title = QLabel("<h2>Welcome to Pylk</h2>")
        subtitle = QLabel("This is the new Qt6 GUI scaffold. Open a .par/.tim to get started.")
        subtitle.setWordWrap(True)
        for w in (title, subtitle):
            w.setAlignment(Qt.AlignHCenter)
        lay.addStretch(1)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addStretch(2)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pylk")
        self._par_path: str | None = None
        self._tim_path: str | None = None

        # Initialize controller
        self._project_controller = ProjectController(self)
        self._connect_controller_signals()

        # Set minimum window size (matching pintk)
        self.setMinimumSize(1000, 800)

        self._init_ui()
        self._restore_geometry()

    # ---------- UI setup ----------
    def _init_ui(self) -> None:
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        self._create_central()
        self._create_docks()

    def _create_actions(self) -> None:
        # File actions
        self.act_open_par = QAction("Open &PAR…", self)
        self.act_open_par.setShortcut(QKeySequence("Ctrl+O"))
        self.act_open_par.triggered.connect(self._on_open_par)

        self.act_open_tim = QAction("Open &TIM…", self)
        self.act_open_tim.setShortcut(QKeySequence("Ctrl+T"))
        self.act_open_tim.triggered.connect(self._on_open_tim)

        self.act_close = QAction("&Close Project", self)
        self.act_close.setShortcut(QKeySequence("Ctrl+W"))
        self.act_close.triggered.connect(self._on_close_project)

        self.act_quit = QAction("&Quit", self)
        self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_quit.triggered.connect(self.close)

        # Plot actions
        self.act_save_plot = QAction("&Save Plot…", self)
        self.act_save_plot.setShortcut(QKeySequence("Ctrl+S"))
        self.act_save_plot.triggered.connect(self._on_save_plot)
        self.act_save_plot.setEnabled(False)  # Disabled until plot is available

        # Edit/Preferences
        self.act_prefs = QAction("&Preferences…", self)
        self.act_prefs.setShortcut(QKeySequence("Ctrl+,"))
        self.act_prefs.triggered.connect(self._on_prefs)

        # View
        self.act_toggle_left_dock = QAction("Left Panel", self, checkable=True, checked=True)
        self.act_toggle_left_dock.triggered.connect(self._toggle_left_dock)

        self.act_toggle_right_dock = QAction("Right Panel", self, checkable=True, checked=True)
        self.act_toggle_right_dock.triggered.connect(self._toggle_right_dock)

        # Help
        self.act_about = QAction("&About Pylk", self)
        self.act_about.triggered.connect(self._on_about)

    def _create_menus(self) -> None:
        m_file = self.menuBar().addMenu("&File")
        m_file.addAction(self.act_open_par)
        m_file.addAction(self.act_open_tim)
        m_file.addSeparator()
        m_file.addAction(self.act_close)
        m_file.addSeparator()
        m_file.addAction(self.act_save_plot)
        m_file.addSeparator()
        m_file.addAction(self.act_quit)

        m_edit = self.menuBar().addMenu("&Edit")
        m_edit.addAction(self.act_prefs)

        m_view = self.menuBar().addMenu("&View")
        m_view.addAction(self.act_toggle_left_dock)
        m_view.addAction(self.act_toggle_right_dock)

        m_help = self.menuBar().addMenu("&Help")
        m_help.addAction(self.act_about)

    def _create_toolbars(self) -> None:
        tb = QToolBar("Main", self)
        tb.setMovable(True)
        tb.setObjectName("MainToolbar")
        tb.addAction(self.act_open_par)
        tb.addAction(self.act_open_tim)
        tb.addSeparator()
        tb.addAction(self.act_close)
        self.addToolBar(Qt.TopToolBarArea, tb)

    def _create_statusbar(self) -> None:
        sb = QStatusBar(self)
        self.setStatusBar(sb)
        self._set_status("Ready")

    def _create_central(self) -> None:
        self._central = CentralPlaceholder(self)
        self._plk_view = PlkView(self)
        self._plk_view.hide()  # Hide initially until project is loaded
        self.setCentralWidget(self._central)

    def _create_docks(self) -> None:
        # Left dock (future: file browser / project / pulsar list)
        self.left_dock = QDockWidget("Project", self)
        self.left_dock.setObjectName("LeftDock")
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.left_dock.setWidget(QLabel("Project panel placeholder"))
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right dock (future: properties / logs / inspector)
        self.right_dock = QDockWidget("Inspector", self)
        self.right_dock.setObjectName("RightDock")
        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.right_dock.setWidget(QLabel("Inspector panel placeholder"))
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        # Connect dock visibility changes to menu bar state
        self.left_dock.visibilityChanged.connect(self._on_left_dock_visibility_changed)
        self.right_dock.visibilityChanged.connect(self._on_right_dock_visibility_changed)

    # ---------- Handlers ----------
    def _on_open_par(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open PAR file", "", "Par files (*.par);;All files (*)"
        )
        if not path:
            return
        self._par_path = path
        self._set_status(f"Loaded PAR: {path}")
        self._maybe_enable_project()

    def _on_open_tim(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open TIM file", "", "Tim files (*.tim);;All files (*)"
        )
        if not path:
            return
        self._tim_path = path
        self._set_status(f"Loaded TIM: {path}")
        self._maybe_enable_project()

    def _maybe_enable_project(self) -> None:
        """Initialize project when both PAR and TIM files are loaded."""
        if self._par_path and self._tim_path:
            self._set_status("Loading project...")
            try:
                self._project_controller.open_project(self._par_path, self._tim_path)
            except Exception as e:
                self._set_status(f"Error loading project: {e}")
                QMessageBox.critical(self, "Project Error", f"Failed to load project:\n{e}")
        else:
            which = "PAR missing" if not self._par_path else "TIM missing"
            self._set_status(f"Waiting for files… ({which})")

    def _on_close_project(self) -> None:
        self._par_path = None
        self._tim_path = None
        self._project_controller.close_project()
        self._set_status("Project closed.")

    def _on_prefs(self) -> None:
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog stub.\n\nAdd settings pages for PINT paths, plotting, themes, etc.",
        )

    def _on_save_plot(self) -> None:
        """Handle save plot action."""
        if hasattr(self, "_plk_view") and self._plk_view:
            self._plk_view._save_plot()
        else:
            QMessageBox.warning(
                self,
                "No Plot Available",
                "No plot is currently available to save. Please load a PAR+TIM project first.",
            )

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About Pylk",
            "<b>Pylk</b><br>"
            "A Qt6 GUI for PINT (rewrite of pintk).<br><br>"
            "© AEI / MPS — MIT or similar license (TBD).",
        )

    def _toggle_left_dock(self, checked: bool) -> None:
        self.left_dock.setVisible(checked)

    def _toggle_right_dock(self, checked: bool) -> None:
        self.right_dock.setVisible(checked)

    def _on_left_dock_visibility_changed(self, visible: bool) -> None:
        """Handle left dock visibility changes to sync menu bar state."""
        self.act_toggle_left_dock.setChecked(visible)

    def _on_right_dock_visibility_changed(self, visible: bool) -> None:
        """Handle right dock visibility changes to sync menu bar state."""
        self.act_toggle_right_dock.setChecked(visible)

    def _connect_controller_signals(self) -> None:
        """Connect project controller signals to UI updates."""
        self._project_controller.projectLoaded.connect(self._on_project_loaded)
        self._project_controller.projectClosed.connect(self._on_project_closed)

    def _on_project_loaded(self, model) -> None:
        """Handle project loaded signal."""
        par_name = model.par_path.split("/")[-1] if model.par_path else "Unknown"
        tim_name = model.tim_path.split("/")[-1] if model.tim_path else "Unknown"
        self._set_status(f"Loaded PAR: {par_name} | TIM: {tim_name}")
        self._show_plotting_view(model)

    def _on_project_closed(self) -> None:
        """Handle project closed signal."""
        self._show_placeholder_view()

    def _show_plotting_view(self, model) -> None:
        """Switch to plotting view and connect to model."""
        self._central.hide()
        self._plk_view.show()
        self.setCentralWidget(self._plk_view)

        # Ensure PlkView takes up proper space
        self._plk_view._ensure_minimum_width()

        self._plk_view.set_model(model)

        # Enable save plot action
        self.act_save_plot.setEnabled(True)

        # Connect to residuals changes for status updates
        if hasattr(model, "residualsChanged"):
            model.residualsChanged.connect(self._on_residuals_changed)

    def _show_placeholder_view(self) -> None:
        """Switch back to placeholder view."""
        self._plk_view.hide()
        self._central.show()
        self.setCentralWidget(self._central)

        # Disable save plot action
        self.act_save_plot.setEnabled(False)

    def _on_residuals_changed(self, payload) -> None:
        """Handle residuals changed signal for status updates."""
        if payload and isinstance(payload, dict):
            n = payload.get("n", 0)
            rms_us = payload.get("rms_us", 0.0)

            # Get current PAR/TIM names for context
            par_name = "Unknown"
            tim_name = "Unknown"
            if hasattr(self, "_project_controller") and self._project_controller.model:
                if self._project_controller.model.par_path:
                    par_name = self._project_controller.model.par_path.split("/")[-1]
                if self._project_controller.model.tim_path:
                    tim_name = self._project_controller.model.tim_path.split("/")[-1]

            self._set_status(
                f"Loaded PAR: {par_name} | TIM: {tim_name} | TOAs: {n} | RMS: {rms_us:.2f} μs"
            )

    # ---------- Utilities ----------
    def _set_status(self, text: str) -> None:
        if self.statusBar():
            self.statusBar().showMessage(text, 5000)

    # ---------- Settings persistence ----------
    def _restore_geometry(self) -> None:
        s = QSettings()
        geo = s.value("MainWindow/geometry", QByteArray())
        state = s.value("MainWindow/state", QByteArray())
        if isinstance(geo, QByteArray) and not geo.isEmpty():
            self.restoreGeometry(geo)
        if isinstance(state, QByteArray) and not state.isEmpty():
            self.restoreState(state)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        s = QSettings()
        s.setValue("MainWindow/geometry", self.saveGeometry())
        s.setValue("MainWindow/state", self.saveState())
        super().closeEvent(event)
