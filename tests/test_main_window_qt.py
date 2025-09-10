from pytestqt.qtbot import QtBot
from pylk.main_window import MainWindow

def test_main_window_init(qtbot: QtBot):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()
    assert win.windowTitle() == "Pylk"
