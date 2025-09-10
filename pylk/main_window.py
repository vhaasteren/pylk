# pylk/main_window.py
from __future__ import annotations

from qtpy.QtCore import Qt, QSettings, QByteArray
from qtpy.QtGui import QAction, QKeySequence
from qtpy.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QStatusBar,
    QToolBar,
    QDockWidget,
    QMessageBox,
)


class CentralPlaceholder(QWidget):
    """Temporary central widget until plotting/view panes are added."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        title = QLabel("<h2>Welcome to Pylk</h2>")
        subtitle = QLabel(
            "This is the new Qt6 GUI scaffold. Open a .par/.tim to get started."
        )
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
        """In the real app, this is where you'd initialize your Pulsar/PINT backend."""
        if self._par_path and self._tim_path:
            self._set_status("Project ready (PAR + TIM loaded).")
            # TODO: replace central widget with your plotting/controls composite
            # and initialize your data/model controller.
        else:
            which = "PAR missing" if not self._par_path else "TIM missing"
            self._set_status(f"Waiting for files… ({which})")

    def _on_close_project(self) -> None:
        self._par_path = None
        self._tim_path = None
        self._set_status("Project closed.")
        # TODO: tear down models/views once implemented.

    def _on_prefs(self) -> None:
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog stub.\n\nAdd settings pages for PINT paths, plotting, themes, etc.",
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

