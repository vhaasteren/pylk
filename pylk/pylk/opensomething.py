#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4:softtabstop=4:shiftwidth=4:expandtab

"""
OpenSomething: Qt widget to open a file


"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
)


class OpenSomethingWidget(QWidget):
    """
    The open-something Widget. First shown in the main window, if it is not
    started with a command to open any file to begin with. This way, we don't
    have to show an empty graph
    """
    def __init__(self, parent=None, openFile=None, **kwargs):
        super(OpenSomethingWidget, self).__init__(parent, **kwargs)

        self.parent = parent
        self.openFileFn = openFile

        self.initOSWidget()

    def initOSWidget(self):
        """
        Initialise the widget with a button and a label
        """
        self.vbox = QVBoxLayout()

        button = QPushButton("Open a file...")
        button.clicked.connect(self.openFile)
        self.vbox.addWidget(button)

        self.setLayout(self.vbox)

    def openFile(self):
        """
        Display the open file dialog, and send the parent window the order to
        open the file
        """
        if not self.openFileFn is None:
            filename = QFileDialog.getOpenFileName(self, 'Open file', '~/')
            self.openFileFn(filename)

