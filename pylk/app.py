# pylk/app.py
from __future__ import annotations

import os
import sys
import traceback
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QMessageBox

from .main_window import MainWindow


def _install_excepthook():
    def handle_exception(exc_type, exc, tb):
        traceback.print_exception(exc_type, exc, tb)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Unexpected Error")
        msg.setText("An unexpected error occurred.")
        msg.setInformativeText(str(exc))
        msg.setDetailedText("".join(traceback.format_exception(exc_type, exc, tb)))
        msg.exec()
    sys.excepthook = handle_exception


def _configure_qt():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # On X11, allow running inside devcontainer with forwarded display
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_X11_NO_MITSHM", "1")
    # If using VSCode devcontainers, DISPLAY is typically set by your devcontainer.json


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    _configure_qt()
    _install_excepthook()

    app = QApplication(argv)
    app.setApplicationName("Pylk")
    app.setOrganizationName("AEI")
    app.setOrganizationDomain("aei.mpg.de")
    app.setApplicationDisplayName("Pylk (PINT GUI)")
    # Optional: set a default icon if you have one in the future
    app.setWindowIcon(QIcon())

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

