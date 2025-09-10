import pytest


@pytest.fixture(scope="session")
def qapp():
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    return app
