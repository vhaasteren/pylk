#!/usr/bin/env python -W ignore::FutureWarning -W ignore::UserWarning -W ignore:DeprecationWarning
"""pylk: Qt interactive interface for PINT pulsar timing tool"""
import sys
import argparse

import numpy as np
import matplotlib as mpl
import tempfile

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

from PyQt5 import QtGui, QtCore

from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QLabel,
    QHBoxLayout,
    QAction,
    QMessageBox,
    QStatusBar,
    QFrame,
    QFileDialog,
    QSplitter,
)

import pint.logging
from loguru import logger as log

pint.logging.setup(level=pint.logging.script_level)

import pint

from pylk import constants
from pylk.pulsar import Pulsar
from pylk.plk import PlkWidget
from pylk.opensomething import OpenSomethingWidget


#from pint.pintk.paredit import ParWidget
#from pint.pintk.plk import PlkWidget, helpstring
#from pint.pintk.pulsar import Pulsar
#from pint.pintk.timedit import TimWidget



__all__ = ["main"]


class PylkWindow(QMainWindow):
    """Main Pylk window."""

    def __init__(
        self,
        parent=None,
        parfile=None,
        timfile=None,
        fitter="auto",
        ephem=None,
        loglevel=None,
        **kwargs,
    ):
        super().__init__(parent)

        self.initUI()

        self.createJupyterKernel()

        self.createPlkWidget()
        self.createJupyterWidget()
        self.createOpenSomethingWidget()

        self.initPylkLayout()

        # Initialize the main widget (the plk emulator)
        self.setPylkLayout(whichWidget='plk',
                showJupyter=True, firsttime=True)

        # Open plk as the main widget
        self.requestOpenPlk(
                parfilename=parfile,
                timfilename=timfile,
                on_open=True,
            )

        self.show()

    def __del__(self):
        pass

    def onAbout(self):

        # TODO: add version info
        msg = constants.PylkBanner
        QMessageBox.about(self, "About Pylk", msg.strip())


    def initUI(self):
        """Initialise the user-interface elements"""

        self.setWindowTitle("Qt Jupyter interface for PINT")

        # Create the main-frame widget, and the layout
        self.mainFrame = QWidget()
        self.setCentralWidget(self.mainFrame)
        self.hbox = QHBoxLayout()     # HBox contains all widgets
        self.splitter = QSplitter(QtCore.Qt.Horizontal)

        # Menu item: open par/tim files
        self.openParTimAction = QAction('&Open par/tim', self)        
        self.openParTimAction.setShortcut('Ctrl+O')
        self.openParTimAction.setStatusTip('Open par/tim')
        self.openParTimAction.triggered.connect(self.openParTim)

        # Menu item: exit Pylk
        self.exitAction = QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

        # Previously, it was possible to switch out the 'plk' widget for another
        # main widget (the binary pulsar one). That one has been stripped out
        # now, so for now it makes no sense to 'toggle' on or off the plk
        # widget. However, the option is still there for now...
        self.togglePlkAction = QAction('&Plk', self)        
        self.togglePlkAction.setShortcut('Ctrl+P')
        self.togglePlkAction.setStatusTip('Toggle plk widget')
        self.togglePlkAction.triggered.connect(self.togglePlk)

        # Menu item: toggle the Jupyter window
        self.toggleJupyterAction = QAction('&Jupyter', self)        
        self.toggleJupyterAction.setShortcut('Ctrl+J')
        self.toggleJupyterAction.setStatusTip('Toggle Jupyter')
        self.toggleJupyterAction.triggered.connect(self.toggleJupyter)

        # Menu item: about Pylk
        self.aboutAction = QAction('&About', self)        
        self.aboutAction.setShortcut('Ctrl+A')
        self.aboutAction.setStatusTip('About Pylk')
        self.aboutAction.triggered.connect(self.onAbout)

        # I don't think we'll need the statusbar yet...
        if False:
            # The status bar
            self.theStatusBar = QStatusBar()
            #self.statusBar()
            self.setStatusBar(self.theStatusBar)

            # A label that shows what engine is being used (hardcoded: PINT)
            self.engine_label = QLabel("PINT")
            self.engine_label.setFrameStyle( QFrame.Sunken|QFrame.Panel)
            self.engine_label.setLineWidth(4)
            self.engine_label.setMidLineWidth(4)
            self.engine_label.setStyleSheet("QLabel{color:black;background-color:red}")
            self.theStatusBar.addPermanentWidget(self.engine_label)

        # On OSX, make sure the menu can be displayed (in the window itself)
        if sys.platform == 'darwin':
            # On OSX, the menubar is usually on the top of the screen, not in
            # the window. To make it in the window:
            #QtGui.qt_mac_set_native_menubar(False) 

            # Otherwise, if we'd like to get the system menubar at the top, then
            # we need another menubar object, not self.menuBar as below. In that
            # case, use:
            # self.menubar = QMenuBar()
            # TODO: Somehow this does not work. Per-window one does though
            pass

        # Create the menu bar, and link the action items
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.openParTimAction)
        self.fileMenu.addAction(self.exitAction)
        self.viewMenu = self.menubar.addMenu('&View')
        self.viewMenu.addAction(self.togglePlkAction)
        self.viewMenu.addAction(self.toggleJupyterAction)
        self.helpMenu = self.menubar.addMenu('&Help')
        self.helpMenu.addAction(self.aboutAction)

        # What is the status quo of the user interface?
        self.showJupyter = False
        self.whichWidget = 'None'
        self.prevShowJupyter = None
        self.prevWhichWidget = 'None'

    def createJupyterKernel(self):
        """Create and start the embedded Jupyter Kernel"""

        # Create an in-process kernel
        self.kernelManager = QtInProcessKernelManager()
        self.kernelManager.start_kernel()
        self.kernel = self.kernelManager.kernel

        # Launch the kernel
        self.kernelClient = self.kernelManager.client()
        self.kernelClient.start_channels()

        # Allow inline matplotlib figures
        self.kernel.shell.enable_matplotlib(gui='inline')

        # Set the in-kernel matplotlib color scheme to black.
        self.setMplColorScheme('black')     # Outside as well (do we need this?)
        self.kernel.shell.run_cell(constants.matplotlib_rc_cell_black,
                store_history=False)

        # Load the necessary packages in the embedded kernel
        # TODO: show this line in a cell of it's own
        # TODO: does this execute if we set store_history=False?
        cell = "import numpy as np, matplotlib.pyplot as plt, pint.pintk.pulsar as pulsar"
        self.kernel.shell.run_cell(cell, store_history=True)

    def createJupyterWidget(self):
        """Create the Jupyter widget"""

        self.consoleWidget = RichJupyterWidget()

        # Minimum size seems to give problems
        #self.consoleWidget.setMinimumSize(*constants.winsize_jupyter_console)

        # Show the banner
        self.consoleWidget.banner = constants.PylkBanner
        self.consoleWidget.kernel_manager = self.kernelManager

        # Couple the client
        self.consoleWidget.kernel_client = self.kernelClient
        self.consoleWidget.exit_requested.connect(self.toggleJupyter)
        self.consoleWidget.set_default_style(colors='linux')
        self.consoleWidget.hide()

        # Register a call-back function for the Jupyter shell. This one is
        # executed insite the child-kernel.
        #self.kernel.shell.register_post_execute(self.postExecute)
        #
        # In Jupyter >= 2, we can use the event register
        # Events: post_run_cell, pre_run_cell, etc...`
        self.kernel.shell.events.register('pre_execute', self.preExecute)
        self.kernel.shell.events.register('post_execute', self.postExecute)
        self.kernel.shell.events.register('post_run_cell', self.postRunCell)


    def createOpenSomethingWidget(self):
        """Create the OpenSomething widget. Do not add it to the layout yet

        TODO:   This widget should become the first main widget to see? At the
                moment, we're avoiding it for the sake of testing purposes
        """

        self.openSomethingWidget = OpenSomethingWidget(parent=self.mainFrame, \
                openFile=self.requestOpenPlk)
        self.openSomethingWidget.hide()

    def createPlkWidget(self):
        """Create the Plk widget"""

        self.plkWidget = PlkWidget(parent=self.mainFrame)
        self.plkWidget.hide()

    def toggleJupyter(self):
        """Toggle the Jupyter widget on or off"""

        self.setPylkLayout(showJupyter = not self.showJupyter)

    def togglePlk(self):
        """Toggle the plk widget on or off"""

        self.setPylkLayout(whichWidget='plk')

    def initPylkLayout(self):
        """Initialise the Pylk layout"""

        # If other 'main' widgets exist, they can be added here
        self.splitter.addWidget(self.openSomethingWidget)
        self.splitter.addWidget(self.plkWidget)

        #self.hbox.addStretch(1)
        self.splitter.addWidget(self.consoleWidget)
        self.hbox.addWidget(self.splitter)
        self.mainFrame.setLayout(self.hbox)

    def hideAllWidgets(self):
        """Hide all widgets of the mainFrame"""

        # Remove all widgets from the main window
        # No, hiding seems to work better
        """
        while self.hbox.count():
            item = self.hbox.takeAt(0)
            if isinstance(item, QWidgetItem):
                #item.widget().deleteLater()
                item.widget().hide()
            elif isinstance(item, QSpacerItem):
                #self.hbox.removeItem(item)
                pass
            else:
                #fcbox.clearLayout(item.layout())
                #self.hbox.removeItem(item)
                pass
        """
        self.openSomethingWidget.hide()
        self.plkWidget.hide()
        self.consoleWidget.hide()

    def showVisibleWidgets(self):
        """Show the correct widgets in the mainFrame"""

        # Add the widgets we need
        if self.whichWidget.lower() == 'opensomething':
            self.openSomethingWidget.show()
        elif self.whichWidget.lower() == 'plk':
            self.plkWidget.show()
        # Other widgets can be added here

        if self.showJupyter:
            self.consoleWidget.show()
        else:
            pass

        # Request focus back to the main widget
        if self.whichWidget.lower() == 'plk' and not self.showJupyter:
            self.plkWidget.setFocusToCanvas()
        # Do it for other main widgets, if they exist
        #elif self.whichWidget.lower() == 'binary' and not self.showJupyter:
        #    self.binaryWidget.setFocusToCanvas()

        # Do we immediately get focus to the Jupyter console?
        #elif self.showJupyter:
        #    self.consoleWidget.setFocus()

    def setPylkLayout(self, whichWidget=None, showJupyter=None, firsttime=False):
        """Given the current main widget, hide all the other widgets
        
        :param whichWidget:
            Which main widget we are showing right now

        :param showJupyter:
            Whether to show the Jupyter console

        :param firsttime:
            Whether or not this is the first time setting the layout. If so,
            resize to proper dimensions.
            TODO: How to do this more elegantly?
        """

        if not whichWidget is None:
            self.whichWidget = whichWidget
        if not showJupyter is None:
            self.showJupyter = showJupyter

        # After hiding the widgets, wait 0 milliseonds before showing them again
        # (what a dirty hack, ugh!)
        self.hideAllWidgets()
        QtCore.QTimer.singleShot(0, self.showVisibleWidgets)

        self.prevWhichWidget = self.whichWidget

        if self.showJupyter != self.prevShowJupyter:
            # Jupyter has been toggled
            self.prevShowJupyter = self.showJupyter
            if self.showJupyter:
                self.resize(*constants.winsize_with_jupyter)
                self.mainFrame.resize(*constants.winsize_with_jupyter)
            else:
                self.resize(*constants.winsize_without_jupyter)
                self.mainFrame.resize(*constants.winsize_without_jupyter)

        # TODO: How to do this more elegantly?
        if firsttime:
            # Set position slightly more to the left of the screen, so we can
            # still open Jupyter
            self.move(50, 100)

        self.mainFrame.setLayout(self.hbox)
        self.mainFrame.show()

    def requestOpenPlk(self, parfilename=None, timfilename=None, on_open=False):
        """Request to open a file in the plk widget

        :param parfilename:
            The parfile to open. If none, ask the user
        :param timfilename:
            The timfile to open. If none, ask the user
        :param on_open:
            Whether we are calling this function upon opening the app
        """

        self.setPylkLayout(whichWidget='plk', showJupyter=self.showJupyter)
        have_partim = not (parfilename is None or timfilename is None)
        testpulsar = (not have_partim and on_open)

        if testpulsar:
            fp_timfile, timfilename = tempfile.mkstemp()
            fp_timfile.write(constants.J1744_timfile)
            fp_timfile.close()

            fp_parfile, parfilename = tempfile.mkstemp()
            fp_parfile.write(constants.J1744_parfile)
            fp_parfile.close()


        if parfilename is None:
            parfilename = QFileDialog.getOpenFileName(self, 'Open par-file', '~/')

        if timfilename is None:
            timfilename = QFileDialog.getOpenFileName(self, 'Open tim-file', '~/')

        self.openPlkPulsar(parfilename, timfilename)

        if testpulsar:
            os.remove(timfilename)
            os.remove(parfilename)

    def setMplColorScheme(self, scheme):
        """
        Set the matplotlib color scheme

        :param scheme: 'black'/'white', the color scheme
        """

        # Obtain the Widget background color
        color = self.palette().color(QtGui.QPalette.Window)
        r, g, b = color.red(), color.green(), color.blue()
        rgbcolor = (r/255.0, g/255.0, b/255.0)

        if scheme == 'white':
            rcP = constants.mpl_rcParams_white

            rcP['axes.facecolor'] = rgbcolor
            rcP['figure.facecolor'] = rgbcolor
            rcP['figure.edgecolor'] = rgbcolor
            rcP['savefig.facecolor'] = rgbcolor
            rcP['savefig.edgecolor'] = rgbcolor
        elif scheme == 'black':
            rcP = constants.mpl_rcParams_black

        for key, value in rcP.items():
            mpl.rcParams[key] = value


    def openParTim(self):
        """Open a par-file and a tim-file"""

        # Ask the user for a par and tim file, and open these with libstempo/pint
        parfilename = QFileDialog.getOpenFileName(self, 'Open par-file', '~/')
        timfilename = QFileDialog.getOpenFileName(self, 'Open tim-file', '~/')

        # Load the pulsar
        self.openPlkPulsar(parfilename, timfilename)


    def openPlkPulsar(self, parfilename, timfilename):
        """Open a pulsar, given a parfile and a timfile

        :param parfilename: The name of the parfile to open
        :param timfilename: The name fo the timfile to open
        """
        # TODO: add ephemeris and fitter

        # Open a PINT pulsar here

        self.psr = Pulsar(parfilename, timfilename, ephem=None, fitter="WLSFitter")

        # From pintk
        # This is a way to set callbacks ('updates') from the main window
        # I guess this is where we handle them

        #self.widgets["plk"].setPulsar(
        #    self.psr,
        #    updates=[self.widgets["par"].set_model, self.widgets["tim"].set_toas],
        #)
        #self.widgets["par"].setPulsar(self.psr, updates=[self.widgets["plk"].update])
        #self.widgets["tim"].setPulsar(self.psr, updates=[self.widgets["plk"].update])

        # Update the plk widget
        #self.plkWidget.setPulsar(self.psr, updates=[self.plkWidget.update])
        # Calling 'update' here seems to delete our selections
        self.plkWidget.setPulsar(self.psr, updates=[])

        # Communicating with the kernel goes as follows
        # self.kernel.shell.push({'foo': 43, 'bar': 42}, interactive=True)
        # print("Embedded, we have:", self.kernel.shell.ns_table['user_local']['foo'])

        # Set the pulsar also in the Jupyter Terminal
        self.kernel.shell.push({'psr': self.psr}, interactive=True)

    def keyPressEvent(self, event, **kwargs):
        """Handle a key-press event

        :param event:   event that is handled here
        """

        key = event.key()

        if key == QtCore.Qt.Key_Escape:
            self.close()
        elif key == QtCore.Qt.Key_Left:
            #print("Left pressed")
            pass
        else:
            #print("Other key")
            pass

        #print("PylkWindow: key press")
        super().keyPressEvent(event, **kwargs)

    def mousePressEvent(self, event, **kwargs):
        """Handle a mouse-click event

        :param event:   event that is handled here
        """

        super().mousePressEvent(event, **kwargs)

    def preExecute(self):
        """Callback function that is run prior to execution of a cell"""
        pass

    def postExecute(self):
        """Callback function that is run after execution of a code"""
        pass

    def postRunCell(self):
        """Callback function that is run after execution of a cell (after
        post-execute)
        """

        # TODO: Do more than just update the plot, but also update _all_ the
        # widgets. Make a callback in plkWidget for that. PylkWindow might also
        # want to loop over some stuff.
        if self.whichWidget == 'plk':
            #self.plkWidget.updatePlot()
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Pylk: Qt interface for PINT pulsar timing tool"
    )
    parser.add_argument("parfile", help="parfile to use")
    parser.add_argument("timfile", help="timfile to use")
    parser.add_argument("--ephem", help="Ephemeris to use", default=None)
    parser.add_argument(
        "--test",
        help="Build UI and exit. Just for unit testing.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--fitter",
        type=str,
        choices=(
            "auto",
            "downhill",
            "WLSFitter",
            "GLSFitter",
            "WidebandTOAFitter",
            "PowellFitter",
            "DownhillWLSFitter",
            "DownhillGLSFitter",
            "WidebandDownhillFitter",
            "WidebandLMFitter",
        ),
        default="auto",
        help="PINT Fitter to use [default='auto'].  'auto' will choose WLS/GLS/WidebandTOA depending on TOA/model properties.  'downhill' will do the same for Downhill versions.",
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Print version info and  exit.",
        version=f"This is PINT version {pint.__version__}, using matplotlib (version={mpl.__version__})",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=pint.logging.levels,
        default=pint.logging.script_level,
        help="Logging level",
        dest="loglevel",
    )
    parser.add_argument(
        "-v", "--verbosity", default=0, action="count", help="Increase output verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", default=0, action="count", help="Decrease output verbosity"
    )

    parsed_args, unparsed_args = parser.parse_known_args()
    #args = parser.parse_args()

    pint.logging.setup(
        level=pint.logging.get_level(
            parsed_args.loglevel,
            parsed_args.verbosity,
            parsed_args.quiet)
    )

    # Create the actual application
    qt_args = sys.argv[:1] + unparsed_args
    app = QApplication(qt_args)

    # Create the window, and start the application
    pylkwin = PylkWindow(
                parent=None,
                parfile=parsed_args.parfile,
                timfile=parsed_args.timfile,
                fitter=parsed_args.fitter,
                ephem=parsed_args.ephem,
                loglevel=parsed_args.loglevel
            )

    pylkwin.raise_()        # Required on OSX to move the app to the foreground (Is that true?)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
