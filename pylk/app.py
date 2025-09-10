# pylk/app.py
from __future__ import annotations

import os
import sys
import traceback
from qtpy.QtCore import Qt, QCoreApplication
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


def _set_qt_attribute(name: str, enable: bool = True) -> None:
    """
    Set a Qt application attribute in a way that works on both Qt5 and Qt6.

    In Qt5, attributes live directly on Qt (e.g., Qt.AA_EnableHighDpiScaling).
    In Qt6, they live under Qt.ApplicationAttribute (e.g.,
    Qt.ApplicationAttribute.AA_EnableHighDpiScaling).
    """
    try:
        attr_ns = getattr(Qt, "ApplicationAttribute", Qt)
        attr = getattr(attr_ns, name)
        QCoreApplication.setAttribute(attr, enable)
    except Exception:
        # Attribute may be missing on some platforms/Qt versions; ignore.
        pass


def _configure_qt():
    # Environment for X11 inside a devcontainer
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_X11_NO_MITSHM", "1")

    # HiDPI handling:
    # - On Qt6 these are mostly defaults, but harmless to set if present.
    # - On Qt5 they are important to enable before QApplication is created.
    _set_qt_attribute("AA_EnableHighDpiScaling", True)
    _set_qt_attribute("AA_UseHighDpiPixmaps", True)

    # For Qt6, optionally make DPI rounding policy less surprising.
    try:
        policy_enum = getattr(Qt, "HighDpiScaleFactorRoundingPolicy", None)
        if policy_enum is not None:
            from qtpy.QtGui import QGuiApplication
            QGuiApplication.setHighDpiScaleFactorRoundingPolicy(policy_enum.PassThrough)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    _configure_qt()
    _install_excepthook()

    app = QApplication(argv)
    app.setApplicationName("Pylk")
    app.setOrganizationName("AEI")
    app.setOrganizationDomain("aei.mpg.de")
    app.setApplicationDisplayName("Pylk (PINT GUI)")
    app.setWindowIcon(QIcon())

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

