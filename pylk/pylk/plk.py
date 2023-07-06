#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4:softtabstop=4:shiftwidth=4:expandtab

"""
Pylk: Qt interactive interface for PINT


pintk helpstring:

The following interactions are currently supported in the plotting pane in `pintk`:

Left click      Select a TOA (if close enough)
Right click     Delete a TOA (if close enough)
  z             Toggle from zoom mode to select mode or back
  r             Reset the pane - undo all deletions, selections, etc.
  k             Correct the pane (i.e. rescale the axes and plot)
  f             Perform a fit on the selected TOAs
  d             Delete (permanently) the selected TOAs
  t             Stash (temporarily remove) or un-stash the selected TOAs
  u             Un-select all of the selected TOAs
  j             Jump the selected TOAs, or un-jump them if already jumped
  v             Jump all TOA clusters except those selected
  i             Print the prefit model as of this moment
  o             Print the postfit model as of this moment (if it exists)
  c             Print the postfit model parameter correlation matrix
  s             Print summary / derived parameters about the pulsar
  m             Print the range of MJDs with the highest density of TOAs
space           Print info about highlighted points (or all, if none are selected)
  x             Print chi^2 and rms info about highlighted points (or all, if none are selected)
  + (or =)      Increase pulse number for selected TOAs
  - (or _)      Decrease pulse number for selected TOAs
  > (or .)      Increase pulse number for TOAs to the right (i.e. later) of selection
  < (or ,)      Decrease pulse number for TOAs to the right (i.e. later) of selection
  q             Quit
  h             Print help




Help from tempo2 plk:

Fitting and Calculating Options
===============================
b          Bin TOAs within certain time bin
c          Change fitting parameters
d (or right mouse) delete point
ctrl-d     delete highlighted points
e          multiply all TOA errors by given amount
F          run FITWAVES
ctrl-f     remove FITWAVES curve from residuals
i (or left mouse) identify point
M          toggle removing mean from the residuals
ctrl-n     Add white noise to site-arrival-times
p          Change model parameter values
ctrl-p     Toggle plotting versus pulse phase
r          Reset (reload .par and .tim file)
ctrl-r     Select regions in MJDs and write to file
w          toggle fitting using weights
x          redo fit using post-fit parameters
+          add positive phase jump
-          add negative phase jump
BACKSPACE  remove all phase jumps
ctrl-=     add period to residuals above cursor
/          re-read .par file

Plot Selection
==============
D (or middle mouse) view profile
s          start of zoom section
f          finish of zoom section
Ctrl-u     Overplot Shapiro delay
u          unzoom
v          view profiles for highlighted points
V          define the user parameter
Ctrl-v     for pre-fit plotting, decompose the timing model fits
           (i.e. overplot the fitted curves - only for prefit plots
ctrl-X     select x-axis specifically
y          Rescale y-axis only
Y          set y-scale exactly
ctrl-Y     select y-axis specifically
z          Zoom using mouse
<          in zoom mode include previous observation
>          in zoom mode include next observation
1          plot pre-fit  residuals vs date
2          plot post-fit residuals vs date
3          plot pre-fit  residuals vs orbital phase
4          plot post-fit residuals vs orbital phase
5          plot pre-fit  residuals serially
6          plot post-fit residuals serially
7          plot pre-fit  residuals vs day of year
8          plot post-fit residuals vs day of year
9          plot pre-fit  residuals vs frequency
a          plot post-fit residuals vs frequency
!          plot pre-fit  residuals vs TOA error
@          plot post-fit residuals vs TOA error
#          plot pre-fit  residuals vs user values
$          plot post-fit residuals vs user values
%          plot pre-fit  residuals vs year
^          plot post-fit residuals vs year
&          plot pre-fit residuals vs elevation
*          plot post-fit residuals vs elevation
(          plot pre-fit residuals vs rounded MJD
)          plot post-fit residuals vs rounded MJD

Options for selecting x and y axes individually
Ctrl-X n   set x-axis
Ctrl-Y n   set y-axis
where n = 

1         plot pre-fit residuals
2         plot post-fit residuals
3         plot centred MJD
4         plot orbital phase
5         plot TOA number
6         plot day of year
7         plot frequency
8         plot TOA error
9         plot user value
0         plot year
-         plot elevation

Display Options
===============
B          place periodic marks on the x-scale
ctrl-c     Toggle between period epoch and centre for the reference epoch
E          toggle plotting error bars
g          change graphics device
G          change gridding on graphics device
ctrl-e     highlight points more than 3 sigma from the mean
H          highlight points with specific flag using symbols
ctrl-i     highlight points with specific flag using colours
I          indicate individual observations
j          draw line between points 
J          toggle plotting points
L          add label to plot
ctrl-l     add line to plot
ctrl-m     toggle menu bar
N          highlight point with a given filename
o          obtain/highlight all points currently in plot
ctrl-T     set text size
U          unhighlight selected points
[          toggle plotting x-axis on log scale
]          toggle plotting y-axis on log scale

Output Options
==============
Ctrl-J     output listing of residuals in Jodrell format
Ctrl-O     output listing of residuals in simple format
l          list all data points in zoomed region
m          measure distance between two points
P          write new .par file
Ctrl-w     over-write input .par file
S          save a new .tim file
Ctrl-S     overwrite input.tim file
t          Toggle displaying statistics for zoomed region
Ctrl-z     Listing of all highlighted points

Various Options
===============
C          run unix command with filenames for highlighted observations
h          this help file
q          quit



"""

import os, sys
import copy

# Importing all the stuff for the IPython console widget
from PyQt5 import QtGui, QtCore

from PyQt5.QtWidgets import (
    QCheckBox,
    QListWidget,
    QWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QGridLayout,
    QButtonGroup,
    QLabel,
    QRadioButton,
)

# All the Qt keys we want to bind
from PyQt5.QtCore import Qt

# Importing all the stuff for the matplotlib widget
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from astropy.time import Time
import astropy.units as u
import numpy as np

import pint.pintk.pulsar as pulsar
import pint.pintk.colormodes as cm
#from pylk import pulsar   # Not used anymore
from pylk import constants

import pint.logging
from loguru import logger as log

try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
except ImportError:
    from matplotlib.backends.backend_tkagg import (
        NavigationToolbar2TkAgg as NavigationToolbar2Tk,
    )

# Mapping from Matplotlib key strings to Qt key constants
key_map = {
    "control": Qt.ControlModifier,
    "ctrl": Qt.ControlModifier,
    "alt": Qt.AltModifier,
    "shift": Qt.ShiftModifier,
    "super": Qt.MetaModifier,
    "cmd": Qt.MetaModifier,
    "up": Qt.Key_Up,
    "down": Qt.Key_Down,
    "left": Qt.Key_Left,
    "right": Qt.Key_Right,
    "enter": Qt.Key_Return,
    "return": Qt.Key_Return,
    "backspace": Qt.Key_Backspace,
    "escape": Qt.Key_Escape,
    "f1": Qt.Key_F1,
    "f2": Qt.Key_F2,
    "f3": Qt.Key_F3,
    "f4": Qt.Key_F4,
    "f5": Qt.Key_F5,
    "f6": Qt.Key_F6,
    "f7": Qt.Key_F7,
    "f8": Qt.Key_F8,
    "f9": Qt.Key_F9,
    "f10": Qt.Key_F10,
    "f11": Qt.Key_F11,
    "f12": Qt.Key_F12,
    "underscore": Qt.Key_Underscore,
    "minus": Qt.Key_Minus,
    "plus": Qt.Key_Plus,
    "equal": Qt.Key_Equal,
    "less": Qt.Key_Less,
    "greater": Qt.Key_Greater,
    "comma": Qt.Key_Comma,
    "period": Qt.Key_Period,
    "space": Qt.Key_Space,
}

plotlabels = {
    "pre-fit": [
        "Pre-fit residual",
        "Pre-fit residual (phase)",
        "Pre-fit residual (us)",
    ],
    "post-fit": [
        "Post-fit residual",
        "Post-fit residual (phase)",
        "Post-fit residual (us)",
    ],
    "mjd": r"MJD",
    "orbital phase": "Orbital Phase",
    "serial": "TOA number",
    "day of year": "Day of the year",
    "year": "Year",
    "frequency": r"Observing Frequency (MHz)",
    "TOA error": r"TOA uncertainty ($\mu$s)",
    "rounded MJD": r"MJD",
}

# TODO: Move nofitboxcomponents into pulsar.py
# All parameters that initially get a fit box
# Some components by default don't have visible fitboxes
#nofitboxcomponents = [
#    "TroposphereDelay",
#    "SolarWindDispersion",
#    "DispersionDM",
#    "DispersionDMX",
#    "FD",
#    "PLRedNoise",
#    "ScaleToaError",
#    "ErrorNoise",
#    "AbsPhase",
#]

# TODO: Move fitboxcomponents into pulsar.py
# Only a few timing model components will have a fitbox by default
fitboxcomponents = [
        "AstrometryEcliptic",
        "AstrometryEquatorial",
        "Spindown",
        "PhaseJump",
    ]

helpstring = """The following interactions are currently supported in the plotting pane in `pintk`:

Left click      Select a TOA (if close enough)
Right click     Delete a TOA (if close enough)
  z             Toggle from zoom mode to select mode or back
  r             Reset the pane - undo all deletions, selections, etc.
  k             Correct the pane (i.e. rescale the axes and plot)
  f             Perform a fit on the selected TOAs
  d             Delete (permanently) the selected TOAs
  t             Stash (temporarily remove) selected TOAs (or un-stash if nothing is selected) 
  u             Un-select all of the selected TOAs
  j             Jump the selected TOAs, or un-jump them if already jumped
  v             Jump all TOA clusters except those selected
  i             Print the prefit model as of this moment
  o             Print the postfit model as of this moment (if it exists)
  c             Print the postfit model parameter correlation matrix
  s             Print summary / derived parameters about the pulsar
  m             Print the range of MJDs with the highest density of TOAs
space           Print info about highlighted points (or all, if none are selected)
  x             Print chi^2 and rms info about highlighted points (or all, if none are selected)
  + (or =)      Increase pulse number for selected TOAs
  - (or _)      Decrease pulse number for selected TOAs
  > (or .)      Increase pulse number for TOAs to the right (i.e. later) of selection
  < (or ,)      Decrease pulse number for TOAs to the right (i.e. later) of selection
  q             Quit
  h             Print help
"""


clickDist = 0.0005

# wideband and narrowband fitter options
wb_fitters = [
    "WidebandTOAFitter",
    "WidebandDownhillFitter",
    "WidebandLMFitter",
]
nb_fitters = [
    "WLSFitter",
    "GLSFitter",
    "PowellFitter",
    "DownhillWLSFitter",
    "DownhillGLSFitter",
]

icon_img = os.path.join(os.path.split(__file__)[0], "PINT_LOGO_128trans.gif")

# foreground text for labels etc
foreground = "black"
background = "#E9E9E9"


class State:
    """class used by revert to save the state of the system before each fit"""

    pass

# This is the old design philosopy. Take with a grain of salt
#
# Design philosophy:
# - The pulsar timing engine is dealt with through derivatives of the abstract
# base class 'BasePulsar'. The object is called psr. Interface is close to that
# of libstempo, but it has some extra features related to plotting parameters.
# PlkWidget has psr as a member, but all the child widgets should not (they do
# know about psr at the moment).
# The plotting parameters and all that are obtained through the psr object. No
# calculations whatsoever are supposed to be done in PlkWidget, or it's child
# widget. They need to know as little as possible, so that they are reusable in
# other GUI types.
# Drawing is done through PlkWidget. There is a callback function 'updatePlot'
# that all child widgets are allowed to call, but they should not get access to
# any further data.
# TODO: remove dependence on psr object in child widgets

def mpl_key_to_qt_key(mpl_key):
    """Convert a Matplotlib key string to a Qt key constant"""
    qt_key = 0
    qt_mod = Qt.NoModifier

    keys = mpl_key.split("+")

    for key in keys:
        if key in key_map:
            if key in ["control", "ctrl", "alt", "shift", "super", "cmd"]:
                qt_mod |= key_map[key]
            else:
                qt_key = key_map[key]
        elif len(key) == 1:
            qt_key = ord(key.upper())

    return qt_key, qt_mod


class PlkFitboxesWidget(QWidget):
    """A widget that allows one to select which parameters to fit for"""

    def __init__(self, parent=None, **kwargs):
        super(PlkFitboxesWidget, self).__init__(parent, **kwargs)

        self.parent = parent
        self.boxChecked = None

        # The checkboxes are ordered on a grid
        self.hbox = QHBoxLayout()     # One horizontal layout
        self.vboxes = []              # Several vertical layouts (9 per line)
        self.fitboxPerLine = 8

        self.fitboxList = QListWidget()     # Which parameters are fit for
        self.checkboxList = QListWidget()   # Which parameters have checkbox

        self.setPlkFitboxesLayout()


    def setPlkFitboxesLayout(self):
        """Set the layout of this widget"""

        # Initialise the layout of the fit-box Widget
        # Initially there are no fitboxes, so just add the hbox
        self.setLayout(self.hbox)


    def setCallbacks(self, boxChecked):
    #, setpars, fitpars, nofitbox):
        """Set the callback functions

        :param boxChecked:      Callback function, when box is checked
        :param model:           PINT model
        #:param setpars:         psr.parameters(which='set')
        #:param fitpars:         psr.parameters(which='fit')
        #:param nofitbox:        Which parameters not to have a box for
        """

        self.boxChecked = boxChecked
        self.deleteFitCheckBoxes()

    #def addFitCheckBoxes(self, setpars, fitpars, nofitbox):
    def addFitCheckBoxes(self, model):
        """Add the fitting checkboxes at the top of the plk Window

        :param model:       The PINT model
        """

        # Delete the fitboxes if there were still some left
        if not len(self.vboxes) == 0:
            self.deleteFitCheckBoxes()

        # In pintk, the parameters are organized per model 'component'.
        # Components can include Astrometry, Spindown, phasejump, DispersionDM,
        # TroposphereDelay, etc.
        # Especially the DispersionDM, but many others too, can contain MANY
        # parameters. Too many to show checkboxes for. We need a better UI way
        # to organize them.
        #
        # Proposal:
        # Parameters are uniquely identified by their name (like in the parfile)
        # Only have a few parameter checkboxes that are shown. Allow this to be
        # changed with a drop-down menu.

        # Figure out which parameters we have,
        # which can be selected
        # which *components* should be shown
        # and of which we show a checkbox

        # Parameters that are not frozen
        #fitparams = [p for p in model.params if not getattr(model, p).frozen]

        # All parameters + components that can be fit for
        allcomps, allpars = zip(*[
            (comp, p)
            for comp in model.components.keys()
            for p in model.components[comp].params
            if p not in pulsar.nofitboxpars
            and getattr(model, p).quantity is not None
        ])

        # The parameter names are more organized this way
        listboxparnames = [f"{comp}::{p}" for (comp, p) in zip(allcomps, allpars)]


        fitboxpars = [
            p
            for (comp, p) in zip(allcomps, allpars)
            if comp in fitboxcomponents
            and p not in pulsar.nofitboxpars
            and getattr(model, p).quantity is not None
        ]

        # Now, for the actual layout
        # First add all the vbox layouts
        for ii in range(min(self.fitboxPerLine, len(fitboxpars))):
            self.vboxes.append(QVBoxLayout())
            self.hbox.addLayout(self.vboxes[-1])

        # Then add the checkbox widgets to the vboxes
        index = 0
        for pp, par in enumerate(fitboxpars): #setpars):
            vboxind = index % self.fitboxPerLine

            cb = QCheckBox(par, self)
            cb.stateChanged.connect(self.changedFitCheckBox)

            # Set checked/unchecked
            #cb.setChecked(par in fitparams)
            cb.setChecked(getattr(model, par).frozen)

            self.vboxes[vboxind].addWidget(cb)
            index += 1

        for vv, vbox in enumerate(self.vboxes):
            vbox.addStretch(1)


    def deleteFitCheckBoxes(self):
        """Delete all the checkboxes from the Widget. (for new pulsar)"""

        for fcbox in self.vboxes:
            while fcbox.count():
                item = fcbox.takeAt(0)
                if isinstance(item, QWidgetItem):
                    item.widget().deleteLater()
                elif isinstance(item, QSpacerItem):
                    fcbox.removeItem(item)
                else:
                    fcbox.clearLayout(item.layout())
                    fcbox.removeItem(item)


        for fcbox in self.vboxes:
            self.hbox.removeItem(fcbox)

        self.vboxes = []

    def changedFitCheckBox(self):
        """This is the signal handler when a checkbox is changed. The changed checkbox
        value will be propagated back to the psr object."""

        # Check who sent the signal
        sender = self.sender()
        parchanged = sender.text()

        # Whatevs, we can just as well re-scan all the CheckButtons, and re-do
        # the fit
        for fcbox in self.vboxes:
            items = (fcbox.itemAt(i) for i in range(fcbox.count())) 
            for w in items:
                if isinstance(w, QWidgetItem) and \
                        isinstance(w.widget(), QCheckBox) and \
                        parchanged == w.widget().text():
                    # boxChecked is the callback function when a box is changed
                    # boxChecked(changed_par, new_state)
                    self.boxChecked(parchanged, bool(w.widget().checkState()))
                    print("{0} set to {1}".format(parchanged, bool(w.widget().checkState())))



class PlkXYChoiceWidget(QWidget):
    """
    Allows one to choose which quantities to plot against one another
    """

    def __init__(self, parent=None, **kwargs):
        super(PlkXYChoiceWidget, self).__init__(parent, **kwargs)

        self.parent = parent

        # We are going to use a grid layout:
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.xButtonGroup = QButtonGroup(self)
        self.xButtonGroup.buttonClicked[int].connect(self.updateXPlot)
        self.yButtonGroup = QButtonGroup(self)
        self.yButtonGroup.buttonClicked[int].connect(self.updateYPlot)

        self.xSelected = 0
        self.ySelected = 0

        # TODO: implement this:
        # Connect the 'buttonClicked' signal 'self.setLabel'
        # There are two overloads for 'buttonClicked' signal: QAbstractButton (button itself) or int (id)
        # Specific overload for the signal is selected via [QAbstractButton]
        # Clicking any button in the QButtonGroup will send this signal with the button
        # self.buttonGroup.buttonClicked[QAbstractButton].connect(self.setLabel)
        # def setLabel(self, button):

        # Use an empty base pulsar to obtain the labels
        # TODO: what to use here?
        #psr = qp.BasePulsar()
    
        self.setPlkXYChoiceLayout()

    def setPlkXYChoiceLayout(self):
        labellength = 3

        label = QLabel(self)
        label.setText("")
        self.grid.addWidget(label, 0, 0, 1, labellength)
        label = QLabel(self)
        label.setText("X")
        self.grid.addWidget(label, 0, 0+labellength, 1, 1)
        label = QLabel(self)
        label.setText("Y")
        self.grid.addWidget(label, 0, 1+labellength, 1, 1)

        # Add all the xychoices
        for ii, choice in enumerate(pulsar.plot_labels):
            # The label of the choice
            label = QLabel(self)
            label.setText(choice)
            self.grid.addWidget(label, 1+ii, 0, 1, labellength)

            # The X and Y radio buttons
            radio = QRadioButton("")
            self.grid.addWidget(radio, 1+ii, labellength, 1, 1)
            if choice.lower() == 'mjd':
                radio.setChecked(True)
                self.xSelected = ii
            self.xButtonGroup.addButton(radio)
            self.xButtonGroup.setId(radio, ii)

            radio = QRadioButton("")
            self.grid.addWidget(radio, 1+ii, 1+labellength, 1, 1)
            if choice.lower() == 'pre-fit':
                radio.setChecked(True)
                self.ySelected = ii
            self.yButtonGroup.addButton(radio)
            self.yButtonGroup.setId(radio, ii)

        self.setLayout(self.grid)

    def setChoice(self, xid="mjd", yid="pre-fit"):
        for ii, choice in enumerate(pulsar.plot_labels):
            if choice.lower() == xid:
                self.xSelected = ii
            if choice.lower() == yid:
                self.ySelected = ii
        
        self.updateChoice()

    def setCallbacks(self, updatePlot):
        """
        Set the callback functions
        """
        self.updatePlot = updatePlot

    def plotIDs(self):
        """
        Return the X,Y ids of the selected quantities
        """
        return pulsar.plot_labels[self.xSelected], pulsar.plot_labels[self.ySelected]

    def updateXPlot(self, newid):
        """
        The x-plot radio buttons have been updated
        """
        self.xSelected = newid
        self.updateChoice()

    def updateYPlot(self, newid):
        """
        The y-plot radio buttons have been updated
        """
        self.ySelected = newid
        self.updateChoice()

    def updateChoice(self):
        # updatePLot was the callback from the main widget
        if self.updatePlot is not None:
            self.updatePlot()

class PlkActionsWidget(QWidget):
    """
    Shows action items like re-fit, write par, write tim, etc.
    """

    def __init__(self, parent=None, **kwargs):

        super(PlkActionsWidget, self).__init__(parent, **kwargs)

        self.parent = parent
        self.updatePlot = None

        self.fit_callback = None
        self.clearAll_callback = None
        self.writePar_callback = None
        self.writeTim_callback = None
        self.saveFig_callback = None
        self.revert_callback = None

        self.hbox = QHBoxLayout()

        self.initPlkActions()

    def initPlkActions(self):
        """
        Pintk has buttons: Fit, Revert, Write Par, Write Tim, Reset
        """

        self.fitbutton = QPushButton('Fit')
        self.fitbutton.clicked.connect(self.fit)
        self.fitbutton.setToolTip('Fit the selected TOAs to the current model.')
        self.hbox.addWidget(self.fitbutton)

        button = QPushButton('Revert')
        button.clicked.connect(self.revert)
        button.setToolTip('Undo the last model fit.')
        self.hbox.addWidget(button)

        button = QPushButton('Write par')
        button.clicked.connect(self.writePar)
        button.setToolTip('Write the post-fit parfile to a file of your choice.')
        self.hbox.addWidget(button)

        button = QPushButton('Write tim')
        button.clicked.connect(self.writeTim)
        button.setToolTip('Write the current TOAs table to a .tim file of your choice.')
        self.hbox.addWidget(button)

        button = QPushButton('Reset')
        button.clicked.connect(self.reset)
        button.setToolTip('Reset everything to the beginning of the session.  Be Careful!')
        self.hbox.addWidget(button)

        button = QPushButton('Save fig')
        button.clicked.connect(self.saveFig)
        button.setToolTip('Save the current figure to file')
        self.hbox.addWidget(button)

        self.hbox.addStretch(1)

        self.setLayout(self.hbox)

    def setCallbacks(self, updatePlot, fit, reset, writePar, writeTim, revert):
        """Callback functions"""

        self.updatePlot = updatePlot

        self.fit_callback = fit
        self.revert_callback = revert
        self.writePar_callback = writePar
        self.writeTim_callback = writeTim
        self.reset_callback = reset

    def setFitButtonText(self, text):
        self.fitbutton.setText(text)

    def fit(self):
        if self.fit_callback is not None:
            self.fit_callback()
        log.info("Fit clicked")

    def revert(self):
        if self.revert_callback is not None:
            self.revert_callback()
        log.info("Revert clicked")

    def writePar(self):
        if self.writePar_callback is not None:
            self.writePar_callback()
        log.info("Write Par clicked")

    def writeTim(self):
        if self.writeTim_callback is not None:
            self.writeTim_callback()
        log.info("Write Tim clicked")

    def reset(self):
        if self.reset_callback is not None:
            self.reset_callback()
        log.info("Reset clicked")

    def saveFig(self):
        log.info("saveFig clicked")




class PlkWidget(QWidget):

    def __init__(self, parent=None, **kwargs):
        super(PlkWidget, self).__init__(parent, **kwargs)

        self.parent = parent

        self.init_loglevel = kwargs.get("loglevel", None)
        self.initSettings()
        self.initKeyHandlerDict()
        self.initPlk()
        self.initPlkLayout()
        self.showVisibleWidgets()


    def initSettings(self):
        self.fit_callback = None
        self.revert_callback = None
        self.clearAll_callback = None
        self.writePar_callback = None
        self.writeTim_callback = None
        self.saveFig_callback = None

        self.psr = None
        self.current_state = State()
        self.state_stack = []
        self.update_callbacks = None

        self.press = False
        self.move = False

        self.color_modes = [
            cm.DefaultMode(self),
            cm.FreqMode(self),
            cm.ObsMode(self),
            cm.NameMode(self),
            cm.JumpMode(self),
        ]
        self.current_mode = "default"


    def initPlk(self):
        self.setMinimumSize(*constants.winsize_without_jupyter)

        self.plkbox = QVBoxLayout()       # plkbox contains the whole PlkWidget
        self.xychoicebox = QHBoxLayout()  # xychoicebox contains the PlkXYChoiceWidget

        self.fitboxesWidget = PlkFitboxesWidget(parent=self)    # Contains all the checkboxes
        self.xyChoiceWidget = PlkXYChoiceWidget(parent=self)
        self.actionsWidget = PlkActionsWidget(parent=self)

        # TODO: implement these
        #self.randomboxWidget = PlkRandomModelSelect(master=self)
        #self.logLevelWidget = PlkLogLevelSelect(master=self)
        #self.fitterWidget = PlkFitterSelect(master=self)
        #self.colorModeWidget = PlkColorModeBoxes(master=self)

        # We are creating the Figure here, so set the color scheme appropriately
        self.setColorScheme(True)

        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        # TODO: set these in constants.py
        self.plkDpi = 100
        self.plkFig = Figure((5.0, 4.0), dpi=self.plkDpi)
        self.plkCanvas = FigureCanvas(self.plkFig)
        self.plkCanvas.setParent(self)
        
        # Call-back functions for clicking and key-press.
        # This is a GUI-independent way of dealing with events. Matplotlib
        # provides that for portability. However, in Qt, we would have more
        # flexibility if we subclass 'FigureCanvas' instead. Then we can just
        # overload 'mousePressEvent', 'mouseMoveEvent' etc. However, we stay
        # close to the pintk way of doing things for now
        self.plkCanvas.mpl_connect('button_press_event', self.canvasClickEvent)
        self.plkCanvas.mpl_connect("button_release_event", self.canvasReleaseEvent)
        self.plkCanvas.mpl_connect("motion_notify_event", self.canvasMotionEvent)
        self.plkCanvas.mpl_connect("key_press_event", self.canvasKeyEvent)

        # This makes the "Home" button reset the plot just like the 'k' key
        #self.plkToolbar.children["!button"].config(command=self.updatePlot)

        # Since we have only one plot, we could use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        self.plkAxes = self.plkFig.add_subplot(111)
        self.plkAx2x = self.plkAxes.twinx()
        self.plkAx2y = self.plkAxes.twiny()
        self.plkAxes.set_zorder(0.1)

        # Done creating the Figure. Restore color scheme to defaults
        self.setColorScheme(False)

        # Create the navigation toolbar, tied to the canvas
        #
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Draw an empty graph
        self.drawSomething()


        # At startup, all the widgets are visible
        self.xyChoiceVisible = True
        self.fitboxVisible = True
        self.actionsVisible = False
        #self.layoutMode = 1   # (0 = none, 1 = all, 2 = only fitboxes, 3 = fit & action)
        self.layoutMode = 4    # (0 = none, 1 = all, 2 = only xy select, 3 = only fit, 4 = xy select & fit)

    def drawSomething(self):
        """
        When we don't have a pulsar yet, but we have to display something, just draw
        an empty figure
        """
        self.setColorScheme(True)
        self.plkAxes.clear()
        self.plkAxes.grid(True)
        self.plkAxes.set_xlabel('MJD')
        self.plkAxes.set_ylabel('Residual ($\mu$s)')
        self.plkFig.tight_layout()
        #self.plkToolbar.push_current()
        self.plkCanvas.draw()
        self.setColorScheme(False)

    def initPlkLayout(self):
        """
        Initialise the basic layout of this plk emulator emulator
        """
        # Initialise the plk box
        self.plkbox.addWidget(self.fitboxesWidget)

        self.xychoicebox.addWidget(self.xyChoiceWidget)
        self.xychoicebox.addWidget(self.plkCanvas)

        self.plkbox.addLayout(self.xychoicebox)

        self.plkbox.addWidget(self.actionsWidget)
        self.setLayout(self.plkbox)

    def initKeyHandlerDict(self):
        self.key_handlers = {
            (Qt.Key_A, Qt.NoModifier): self.handleKeyA,
            (Qt.Key_B, Qt.NoModifier): self.handleKeyB,
            (Qt.Key_C, Qt.NoModifier): self.handleKeyC,
            (Qt.Key_D, Qt.NoModifier): self.handleKeyD,
            (Qt.Key_E, Qt.NoModifier): self.handleKeyE,
            (Qt.Key_F, Qt.NoModifier): self.handleKeyF,
            (Qt.Key_G, Qt.NoModifier): self.handleKeyG,
            (Qt.Key_H, Qt.NoModifier): self.handleKeyH,
            (Qt.Key_I, Qt.NoModifier): self.handleKeyI,
            (Qt.Key_J, Qt.NoModifier): self.handleKeyJ,
            (Qt.Key_K, Qt.NoModifier): self.handleKeyK,
            (Qt.Key_L, Qt.NoModifier): self.handleKeyL,
            (Qt.Key_M, Qt.NoModifier): self.handleKeyM,
            (Qt.Key_N, Qt.NoModifier): self.handleKeyN,
            (Qt.Key_O, Qt.NoModifier): self.handleKeyO,
            (Qt.Key_P, Qt.NoModifier): self.handleKeyP,
            (Qt.Key_Q, Qt.NoModifier): self.handleKeyQ,
            (Qt.Key_R, Qt.NoModifier): self.handleKeyR,
            (Qt.Key_S, Qt.NoModifier): self.handleKeyS,
            (Qt.Key_T, Qt.NoModifier): self.handleKeyT,
            (Qt.Key_U, Qt.NoModifier): self.handleKeyU,
            (Qt.Key_V, Qt.NoModifier): self.handleKeyV,
            (Qt.Key_W, Qt.NoModifier): self.handleKeyW,
            (Qt.Key_X, Qt.NoModifier): self.handleKeyX,
            (Qt.Key_Y, Qt.NoModifier): self.handleKeyY,
            (Qt.Key_Z, Qt.NoModifier): self.handleKeyZ,
            (Qt.Key_Underscore, Qt.NoModifier): self.subtractPhaseWrapSel,
            (Qt.Key_Minus, Qt.NoModifier): self.subtractPhaseWrapSel,
            (Qt.Key_Plus, Qt.NoModifier): self.addPhaseWrapSel,
            (Qt.Key_Equal, Qt.NoModifier): self.addPhaseWrapSel,
            (Qt.Key_Less, Qt.NoModifier): self.subtractPhaseWrapAfter,
            (Qt.Key_Period, Qt.NoModifier): self.subtractPhaseWrapAfter,
            (Qt.Key_Greater, Qt.NoModifier): self.addPhaseWrapAfter,
            (Qt.Key_Comma, Qt.NoModifier): self.addPhaseWrapAfter,
            (Qt.Key_Space, Qt.NoModifier): self.print_info,
            (Qt.Key_Escape, Qt.NoModifier): self.handleEscape,
            (Qt.Key_M, Qt.ControlModifier): self.handleCtrlM,
            (Qt.Key_M, Qt.MetaModifier): self.handleCtrlM,
            (Qt.Key_J, Qt.ControlModifier): self.handleCtrlJ,
            (Qt.Key_J, Qt.MetaModifier): self.handleCtrlJ,
        }

    def showVisibleWidgets(self):
        """
        Show the correct widgets in the plk Window
        """
        self.xyChoiceWidget.setVisible(self.xyChoiceVisible)
        self.fitboxesWidget.setVisible(self.fitboxVisible)
        self.actionsWidget.setVisible(self.actionsVisible)

    def setColorScheme(self, start=True):
        """
        Set the color scheme

        :param start:   When true, save the original scheme, and set to white
                        When False, restore the original scheme
        """
        # Obtain the Widget background color
        color = self.palette().color(QtGui.QPalette.Window)
        r, g, b = color.red(), color.green(), color.blue()
        rgbcolor = (r/255.0, g/255.0, b/255.0)

        if start:
            # Copy of 'white', because of bug in matplotlib that does not allow
            # deep copies of rcParams. Store values of matplotlib.rcParams
            self.orig_rcParams = copy.deepcopy(constants.mpl_rcParams_white)
            for key, value in self.orig_rcParams.items():
                self.orig_rcParams[key] = mpl.rcParams[key]

            rcP = copy.deepcopy(constants.mpl_rcParams_white)
            rcP['axes.facecolor'] = rgbcolor
            rcP['figure.facecolor'] = rgbcolor
            rcP['figure.edgecolor'] = rgbcolor
            rcP['savefig.facecolor'] = rgbcolor
            rcP['savefig.edgecolor'] = rgbcolor

            for key, value in rcP.items():
                mpl.rcParams[key] = value
        else:
            for key, value in constants.mpl_rcParams_black.items():
                mpl.rcParams[key] = value

    def update(self):
        if self.psr is not None:
            self.psr.update_resids()
            self.selected = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
            self.jumped = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
            self.actionsWidget.setFitButtonText("Fit")
            self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
            #self.randomboxWidget.addRandomCheckbox(self)
            #self.colorModeWidget.addColorModeCheckbox(self.color_modes)
            #self.fitterWidget.updateFitterChoices(self.psr.all_toas.wideband)
            self.xyChoiceWidget.setChoice()
            self.updatePlot(keepAxes=True)
            #self.plkToolbar.update()
            # reset state stack
            self.state_stack = [self.base_state]
            self.current_state = State()

    def setPulsar(self, psr, updates):
        self.psr = psr

        # self.selected & self.jumped = boolean arrays, len = all_toas, True = selected/jumped
        self.selected = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
        self.jumped = np.zeros(self.psr.all_toas.ntoas, dtype=bool)

        # update jumped with any jump params already in the file
        self.updateAllJumped()
        self.update_callbacks = updates

        if not hasattr(self, "base_state"):
            self.base_state = State()
            self.base_state.psr = copy.deepcopy(self.psr)
            self.base_state.selected = copy.deepcopy(self.selected)
            self.state_stack.append(self.base_state)

        self.fitboxesWidget.setCallbacks(self.fitboxChecked)
        #self.colorModeWidget.setCallbacks(self.updateGraphColors)
        self.xyChoiceWidget.setCallbacks(self.updatePlot)
        self.actionsWidget.setCallbacks(self.updatePlot,
            self.fit, self.reset, self.writePar, self.writeTim, self.revert
        )

        #self.fitboxesWidget.grid(row=0, column=0, columnspan=2, sticky="W")
        #self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
        #self.randomboxWidget.addRandomCheckbox(self)
        #self.colorModeWidget.grid(row=2, column=0, columnspan=1, sticky="S")
        #self.colorModeWidget.addColorModeCheckbox(self.color_modes)
        self.xyChoiceWidget.setChoice()
        #self.fitterWidget.updateFitterChoices(self.psr.all_toas.wideband)
        #self.fitterWidget.fitterSelect.current(
        #    self.fitterWidget.fitterSelect["values"].index(self.psr.fit_method)
        #)
        #self.fitterWidget.fitter = self.psr.fit_method
        self.updatePlot(keepAxes=False)
        #self.plkToolbar.update()

        # Draw the residuals
        self.xyChoiceWidget.updateChoice()

        # This screws up the show/hide logistics
        #self.show()

    def call_updates(self, psr_update=False):
        if self.update_callbacks is not None:
            for ucb in self.update_callbacks:
                if psr_update:
                    ucb(self.psr)
                else:
                    ucb()

    def updateGraphColors(self, color_mode):
        self.current_mode = color_mode
        self.updatePlot(keepAxes=True)

    def fitboxChecked(self, parchanged, newstate):
        """
        When a fitbox is (un)checked, this callback function is called

        :param parchanged:  Which parameter has been (un)checked
        :param newstate:    The new state of the checkbox
        """
        getattr(self.psr.prefit_model, parchanged).frozen = not newstate
        if self.psr.fitted:
            getattr(self.psr.postfit_model, parchanged).frozen = not newstate
        if parchanged.startswith("JUMP"):
            self.updateJumped(parchanged)
        self.call_updates()
        self.updatePlot(keepAxes=True)

    def unselect(self):
        """
        Undo a selection (but not deletes)
        """
        self.psr.selected_toas = copy.deepcopy(self.psr.all_toas)
        self.selected = np.zeros(self.psr.selected_toas.ntoas, dtype=bool)
        self.updatePlot(keepAxes=True)
        self.call_updates()

    def fit(self):
        """
        fit the selected points using the current pre-fit model
        """
        raise NotIplementedError()
        if self.psr is not None:
            # check jumps wont cancel fit, if so, exit here
            if self.check_jump_invalid():
                return None
            if self.psr.fitted:
                # append the current state to the state stack
                self.current_state.psr = copy.deepcopy(self.psr)
                self.current_state.selected = self.selected
                self.state_stack.append(copy.deepcopy(self.current_state))
            self.psr.fit_method = self.fitterWidget.fitter
            self.psr.fit(self.selected)
            #if self.randomboxWidget.getRandomModel():
            #    self.psr.random_models(self.selected)
            self.current_state.selected = copy.deepcopy(self.selected)
            self.actionsWidget.setFitButtonText("Re-fit")
            self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
            #self.randomboxWidget.addRandomCheckbox(self)
            #self.colorModeWidget.addColorModeCheckbox(self.color_modes)
            xid, yid = self.xyChoiceWidget.plotIDs()
            self.xyChoiceWidget.setChoice(xid=xid, yid="post-fit")
            self.jumped = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
            self.updateAllJumped()
            self.updatePlot(keepAxes=False)
        self.call_updates()

    def reset(self):
        """
        Reset all plot changes for this pulsar
        """
        self.psr.use_pulse_numbers = False
        self.psr.reset_TOAs()
        self.psr.fitted = False
        self.psr = copy.deepcopy(self.base_state.psr)
        self.selected = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
        self.jumped = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
        self.updateAllJumped()
        self.actionsWidget.setFitButtonText("Fit")
        self.fitboxesWidget.addFitCheckBoxes(self.base_state.psr.prefit_model)
        #self.randomboxWidget.addRandomCheckbox(self)
        #self.colorModeWidget.addColorModeCheckbox(self.color_modes)
        self.xyChoiceWidget.setChoice()
        self.updatePlot(keepAxes=False)
        #self.plkToolbar.update()
        self.current_state = State()
        self.state_stack = [self.base_state]
        self.call_updates(psr_update=True)

    def writePar(self, format="pint"):
        """
        Write the fit parfile to ea file
        """
        # TODO: do a file dialog here
        raise NotImplementedError("")
        filename = tkFileDialog.asksaveasfilename(title="Choose output par file")
        try:
            with open(filename, "w") as fout:
                if self.psr.fitted:
                    fout.write(self.psr.postfit_model.as_parfile(format=format))
                    log.info(f"Saved post-fit parfile to {filename} in {format} format")
                else:
                    fout.write(self.psr.prefit_model.as_parfile(format=format))
                    log.warning(
                        f"Pulsar has not been fitted! Saving pre-fit parfile to {filename} in {format} format"
                    )

        except:
            if filename in [(), ""]:
                print("Write Par cancelled.")
            else:
                log.error(f"Could not save parfile to filename:\t{filename}")

    def writeTim(self, format="tempo2"):
        """
        Write the current timfile to a file
        """
        # TODO: do a file dialog here
        raise NotImplementedError("")
        # remove jump flags from toas (don't want model-specific jumps being saved)
        for dict in self.psr.all_toas.table["flags"]:
            if "jump" in dict.keys():
                del dict["jump"]
        filename = tkFileDialog.asksaveasfilename(title="Choose output tim file")
        try:
            log.info(f"Choose output file {filename}")
            self.psr.all_toas.write_TOA_file(filename, format=format)
            log.info(f"Wrote TOAs to {filename} with format {format}")
        except:
            if filename in [(), ""]:
                print("Write Tim cancelled.")
            else:
                log.error(f"Could not save file to filename:\t{filename}")

    def revert(self):
        """
        revert to the state of the model and toas right before the last fit
        """
        if len(self.state_stack) > 0 and self.psr.fitted and self.psr is not None:
            c_state = self.state_stack.pop()
            self.psr = c_state.psr
            self.selected = c_state.selected
            self.selected = self.psr.delete_TOAs(self.psr.deleted, self.selected)
            self.updateAllJumped()
            self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
            #self.randomboxWidget.addRandomCheckbox(self)
            self.colorModeWidget.addColorModeCheckbox(self.color_modes)
            if len(self.state_stack) == 0:
                self.state_stack.append(self.base_state)
                self.actionsWidget.setFitButtonText("Fit")
            self.psr.update_resids()
            self.updatePlot(keepAxes=False)
        else:
            log.warning("No model to revert to")

    def updatePlot(self, keepAxes=False):
        """
        Update the plot/figure

        @param keepAxes: Set to True whenever we want to preserve zoom
        """

        # These three calls are not in pintk
        self.setColorScheme(True)
        self.plkAxes.clear()
        self.plkAxes.grid(True)

        if self.psr is not None:
            # Get a mask for the plotting points
            #msk = self.psr.mask('plot')

            # Get the IDs of the X and Y axis
            self.xid, self.yid = self.xyChoiceWidget.plotIDs()

            # Retrieve the data
            x, self.xerrs = self.psr_data_from_label(self.xid)
            y, self.yerrs = self.psr_data_from_label(self.yid)
            if x is not None and y is not None:
                self.xvals = x
                self.yvals = y
                if "fit" in self.yid and not hasattr(self, "y_unit"):
                    ymin, ymax = self.determine_yaxis_units(miny=y.min(), maxy=y.max())
                    self.y_unit = ymin.unit
                    self.yvals = self.yvals.to(self.y_unit)
                    self.yerrs = self.yerrs.to(self.y_unit)
                self.plotResiduals(keepAxes=keepAxes)
            else:
                raise ValueError("Nothing to plot!")

        self.plkFig.tight_layout()
        self.plkCanvas.draw()
        self.setColorScheme(False)

    def plotErrorbar(self, selected, color):
        """
        For some reason, xvals will not plot unless unitless.
        Tried using quantity_support and time_support, which plots x & yvals,
        but then yerrs fails - cannot find work-around in this case.
        """

        self.plkAxes.errorbar(
            self.xvals[selected].value,
            self.yvals[selected],
            yerr=self.yerrs[selected],
            fmt=".",
            color=color,
        )

    def plotResiduals(self, keepAxes=False):
        """
        Update the plot, given all the plotting info
        """
        if keepAxes:
            xmin, xmax = self.plkAxes.get_xlim()
            ymin, ymax = self.plkAxes.get_ylim()
        else:
            xave = 0.5 * (np.max(self.xvals) + np.min(self.xvals))
            xmin = xave - 1.10 * (xave - np.min(self.xvals))
            xmax = xave + 1.10 * (np.max(self.xvals) - xave)
            if self.yerrs is None:
                yave = 0.5 * (np.max(self.yvals) + np.min(self.yvals))
                ymin = yave - 1.10 * (yave - np.min(self.yvals))
                ymax = yave + 1.10 * (np.max(self.yvals) - yave)
            else:
                yave = 0.5 * (
                    np.max(self.yvals + self.yerrs) + np.min(self.yvals - self.yerrs)
                )
                ymin = yave - 1.10 * (yave - np.min(self.yvals - self.yerrs))
                ymax = yave + 1.10 * (np.max(self.yvals + self.yerrs) - yave)
            xmin, xmax = xmin.value, xmax.value

        # determine if y-axis units need scaling and scale accordingly
        if "fit" in self.yid:
            # ymin, ymax = self.determine_yaxis_units(miny=ymin, maxy=ymax)
            # self.y_unit = ymin.unit
            if type(self.yvals) == u.quantity.Quantity:
                self.yvals = self.yvals.to(self.y_unit)
            if type(ymin) == u.quantity.Quantity:
                ymin, ymax = ymin.to(self.y_unit).value, ymax.to(self.y_unit).value
        else:
            if type(ymin) == u.quantity.Quantity:
                ymin, ymax = ymin.value, ymax.value

        self.plkAxes.clear()
        self.plkAx2x.clear()
        self.plkAx2y.clear()
        self.plkAxes.grid(True)
        # plot residuals in appropriate color scheme
        for mode in self.color_modes:
            if self.current_mode == mode.mode_name:
                mode.plotColorMode()
        self.plkAxes.axis([xmin, xmax, ymin, ymax])
        self.plkAxes.get_xaxis().get_major_formatter().set_useOffset(False)
        self.plkAx2y.set_visible(False)
        self.plkAx2x.set_visible(False)
        # clears the views stack and puts the scaled view on top, fixes toolbar problems
        # self.plkToolbar._views.clear()
        #self.plkToolbar.push_current()

        if self.xid in ["pre-fit", "post-fit"]:
            self.plkAxes.set_xlabel(plotlabels[self.xid][0])
            m = (
                self.psr.prefit_model
                if self.xid == "pre-fit" or not self.psr.fitted
                else self.psr.postfit_model
            )
            if hasattr(m, "F0"):
                self.plkAx2y.set_visible(True)
                self.plkAx2y.set_xlabel(plotlabels[self.xid][1])
                f0 = m.F0.quantity.to(u.MHz).value
                self.plkAx2y.set_xlim(xmin * f0, xmax * f0)
                self.plkAx2y.xaxis.set_major_locator(
                    mpl.ticker.FixedLocator(self.plkAxes.get_xticks() * f0)
                )
        else:
            self.plkAxes.set_xlabel(plotlabels[self.xid])

        if self.yid in ["pre-fit", "post-fit"]:
            self.plkAxes.set_ylabel(
                plotlabels[self.yid][0] + " (" + str(self.y_unit) + ")"
            )
            try:
                r = (
                    self.psr.prefit_resids
                    if self.yid == "pre-fit" or not self.psr.fitted
                    else self.psr.postfit_resids
                )
                if self.y_unit == u.us:
                    f0 = r.get_PSR_freq().to(u.MHz).value
                elif self.y_unit == u.ms:
                    f0 = r.get_PSR_freq().to(u.kHz).value
                else:
                    f0 = r.get_PSR_freq().to(u.Hz).value
                self.plkAx2x.set_visible(True)
                self.plkAx2x.set_ylabel(plotlabels[self.yid][1])
                self.plkAx2x.set_ylim(ymin * f0, ymax * f0)
                self.plkAx2x.yaxis.set_major_locator(
                    mpl.ticker.FixedLocator(self.plkAxes.get_yticks() * f0)
                )
            except:
                pass
            # If fitting orbital phase, plot the conjunction
            if self.xid == "orbital phase":
                m = (
                    self.psr.prefit_model
                    if self.xid == "pre-fit" or not self.psr.fitted
                    else self.psr.postfit_model
                )
                if m.is_binary:
                    print(
                        "The black vertical line is when superior conjunction occurs."
                    )
                    # Get the time of conjunction after T0 or TASC
                    tt = m.T0.value if hasattr(m, "T0") else m.TASC.value
                    mjd = m.conjunction(tt)
                    pb = m.pb()[0].to_value("day")
                    phs = (mjd - tt) / pb
                    self.plkAxes.plot([phs, phs], [ymin, ymax], "k-")
        else:
            self.plkAxes.set_ylabel(plotlabels[self.yid])

        self.plkAxes.set_title(self.psr.name, y=1.1)

        # plot random models
        if self.psr.fitted == True and self.randomboxWidget.getRandomModel() == 1:
            log.info("Plotting random models")
            f_toas = self.psr.faketoas
            rs = self.psr.random_resids
            # look at axes, allow random models to plot on x-axes other than MJD
            xid, yid = self.xyChoiceWidget.plotIDs()
            if xid == "year":
                t = Time(f_toas.get_mjds(), format="mjd")
                f_toas_plot = np.asarray(t.decimalyear) << u.year
            else:
                f_toas_plot = f_toas.get_mjds()
            scale = 1
            if self.yvals.unit == u.us:
                scale = 10**6
            elif self.yvals.unit == u.ms:
                scale = 10**3
            # Want to plot things in sorted order so that lines are smooth
            sort_inds = np.argsort(f_toas_plot)
            f_toas_plot = f_toas_plot[sort_inds]
            for i in range(len(rs)):
                self.plkAxes.plot(
                    f_toas_plot, rs[i][sort_inds] * scale, "-k", alpha=0.3
                )

    def determine_yaxis_units(self, miny, maxy):
        """Checks range of residuals and converts units if range sufficiently large/small."""
        diff = maxy - miny
        if diff > 0.2 * u.s:
            maxy = maxy.to(u.s)
            miny = miny.to(u.s)
        elif diff > 0.2 * u.ms:
            maxy = maxy.to(u.ms)
            miny = miny.to(u.ms)
        elif diff <= 0.2 * u.ms:
            maxy = maxy.to(u.us)
            miny = miny.to(u.us)
        return miny, maxy

    def print_info(self, *args, **kwargs):
        """
        Write information about the current selection, or all points
        """
        # Select all the TOAs if not are selected
        selected = self.selected if np.sum(self.selected) else ~self.selected

        # xvals, yvals, index, obs, freq, error MJD flags
        header = (
            f"\n{self.xid: ^10} {self.yid: ^10} {'index': ^7} {'Obs': ^7} "
            + f"{'Freq (MHz)': ^11} {'Error (us)': ^11} {'MJD': ^20}     flags"
        )
        print(header)
        print("-" * (len(header) + 8))

        xs = self.xvals[selected].value
        ys = self.yvals[selected].value
        inds = self.psr.all_toas.table["index"][selected]
        obss = self.psr.all_toas.table["obs"][selected]
        freqs = self.psr.all_toas.table["freq"][selected]
        errors = self.psr.all_toas.table["error"][selected]
        MJDs = self.psr.all_toas.table["mjd_float"][selected]
        flags = self.psr.all_toas.table["flags"][selected]

        for x, y, ind, obs, freq, err, MJD, flag in zip(
            xs, ys, inds, obss, freqs, errors, MJDs, flags
        ):
            print(
                f"{x:^10.4f} {y:^10.4f} {ind:^7} {obs:^7} {freq:^11.4f} {err:^11.3f} {MJD:^20.15f} {flag}"
            )
        self.print_chi2()

    def print_chi2(self):
        """Print chi^2 about just the selected points"""
        # Select all the TOAs if not are selected
        selected = self.selected if np.sum(self.selected) else ~self.selected
        self.psr.print_chi2(selected)

    def psr_data_from_label(self, label):
        """
        Given a label, get the corresponding data from the pulsar

        :param label: The label for the data we want
        :return:    data, error
        """
        data, error = None, None
        if label == "pre-fit":
            if self.psr.fitted:
                # TODO: may want to include option for prefit resids to include jumps
                data = self.psr.prefit_resids_no_jumps.time_resids.to(u.us)
                error = self.psr.all_toas.get_errors().to(u.us)
                return data, error
            data = self.psr.prefit_resids.time_resids.to(u.us)
            error = self.psr.all_toas.get_errors().to(u.us)
        elif label == "post-fit":
            if self.psr.fitted:
                data = self.psr.postfit_resids.time_resids.to(u.us)
            else:
                log.warning("Pulsar has not been fitted yet! Giving pre-fit residuals")
                data = self.psr.prefit_resids.time_resids.to(u.us)
            error = self.psr.all_toas.get_errors().to(u.us)
        elif label == "mjd":
            data = self.psr.all_toas.get_mjds()
            error = self.psr.all_toas.get_errors()
        elif label == "orbital phase":
            data = self.psr.orbitalphase()
            error = None
        elif label == "serial":
            data = np.arange(self.psr.all_toas.ntoas) * u.m / u.m
            error = None
        elif label == "day of year":
            data = self.psr.dayofyear()
            error = None
        elif label == "year":
            data = self.psr.year()
            error = None
        elif label == "frequency":
            data = self.psr.all_toas.get_freqs()
            error = None
        elif label == "TOA error":
            data = self.psr.all_toas.get_errors().to(u.us)
            error = None
        elif label == "rounded MJD":
            data = np.floor(self.psr.all_toas.get_mjds() + 0.5 * u.d)
            error = self.psr.all_toas.get_errors().to(u.d)
        return data, error

    def coordToPoint(self, cx, cy, which='xy'):
        """
        Given a set of x-y coordinates, get the TOA index (i.e. current TOA
        table row) closest to it

        :param cx:      x-value of the coordinates
        :param cy:      y-value of the coordinates
        :param which:   which axis to include in distance measure [xy/x/y]

        :return:    Index of observation
        """
        ax, ay = 1, 1
        if which=='x': ay = 0
        if which=='y': ax = 0

        ind = None
        if self.psr is not None and cx is not None and cy is not None:
            x = self.xvals.value
            y = self.yvals.value
            xmin, xmax, ymin, ymax = self.plkAxes.axis()
            dist = ax*((x - cx) / (xmax - xmin)) ** 2.0 + ay*((y - cy) / (ymax - ymin)) ** 2.0
            ind = np.argmin(dist)
            log.debug(
                f"Closest: TOA index {self.psr.all_toas.table['index'][ind]} (plot index {ind}): "
                f"({self.xvals[ind]:.4f}, {self.yvals[ind]:.3g}) at d={dist[ind]:.3g}"
            )
            if dist[ind] > clickDist:
                log.warning("Not close enough to a point")
                ind = None

        return ind

    def check_jump_invalid(self):
        """checks if jumps will cancel the attempted fit"""
        if "PhaseJump" not in self.psr.prefit_model.components:
            return False
        self.updateAllJumped()
        sel = ~self.selected if self.selected.sum() == 0 else self.selected
        if np.all(self.jumped[sel]):
            log.warning(
                "TOAs being fit must not all be jumped."
                "Remove or uncheck at least one jump in the selected TOAs before fitting."
            )
            return True

    def updateJumped(self, jump_name):
        """update self.jumped for the jump given"""
        # if removing a jump, add_jump returns a boolean array rather than a name
        if type(jump_name) == list:
            self.jumped[jump_name] = False
            return None
        elif type(jump_name) != str:
            log.error(
                jump_name,
                "Return value for the jump name is not a string, jumps not updated",
            )
            return None
        num = jump_name[4:]  # string value
        jump_select = [
            ("jump" in dict and dict["jump"] == num)
            for dict in self.psr.all_toas.table["flags"]
        ]
        log.info(f"JUMP{num} contains {sum(jump_select)} TOAs for fit.")
        self.jumped[jump_select] = ~self.jumped[jump_select]

    def updateAllJumped(self):
        """Update self.jumped for all active JUMPs"""
        self.jumped = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
        for param in self.psr.prefit_model.params:
            if (
                param.startswith("JUMP")
                and getattr(self.psr.prefit_model, param).frozen == False
            ):
                self.updateJumped(param)

    def setFocusToCanvas(self):
        """
        Set the focus to the plk Canvas
        """
        self.plkCanvas.setFocus()

    def canvasClickEvent(self, event):
        """
        Call this function when the figure/canvas is clicked
        """
        log.debug(f"You clicked in the canvas (button = {event.button})")
        self.setFocusToCanvas()
        if event.inaxes == self.plkAxes:
            self.press = True
            self.pressEvent = event

            # Unlike in Tk, in PyQt we don't directly draw on the canvas
            # So, we need to create a rectangle artist using Matplotlib and add
            # it to the axes
            self.rect = Rectangle((0, 0), 0, 0, fill=False)  # create an invisible rectangle
            self.plkAxes.add_patch(self.rect)  # add rectangle to the axes

    def canvasMotionEvent(self, event):
        """
        Call this function when mouse is moved in the figure/canvas
        """
        if event.inaxes == self.plkAxes and self.press:
            self.move = True
            # Draw bounding box
            x0, x1 = self.pressEvent.x, event.x
            y0, y1 = self.pressEvent.y, event.y
            self.rect.set_xy((min([x0, x1]), min([y0, y1])))  # set bottom left corner
            self.rect.set_width(abs(x1 - x0))  # set width
            self.rect.set_height(abs(y1 - y0))  # set height
            self.rect.set_visible(True)  # make rectangle visible
            self.plkCanvas.draw()        # Don't need to update the whole plot

            #height = self.plkFig.bbox.height
            #y0 = height - y0
            #y1 = height - y1
            #if hasattr(self, "brect"):
            #    self.plkCanvas._tkcanvas.delete(self.brect)
            #self.brect = self.plkCanvas._tkcanvas.create_rectangle(x0, y0, x1, y1)

    def canvasReleaseEvent(self, event):
        """
        Call this function when the figure/canvas is released
        """
        self.rect.set_visible(False)  # hide the rectangle
        self.plkCanvas.draw()

        if self.press and not self.move:
            self.stationaryClick(event)
        elif self.press and self.move:
            self.clickAndDrag(event)
        self.press = False
        self.move = False

    def stationaryClick(self, event):
        """
        Call this function when the mouse is clicked but not moved
        """
        log.debug(f"You stationary clicked (button = {event.button})")
        if event.inaxes == self.plkAxes:
            ind = self.coordToPoint(event.xdata, event.ydata)
            if ind is not None:
                if event.button == 3:
                    # Right click deletes closest TOA
                    # Adapt to TOA index rather than plot index, they differ when TOAs are already deleted
                    toa_ind = self.psr.all_toas.table["index"][ind]
                    sudo_select_mask = np.zeros_like(self.selected).astype(bool)
                    sudo_select_mask[ind] = True
                    jumped_copy = copy.deepcopy(self.jumped)
                    unselect_jump_stat = jumped_copy[~sudo_select_mask]

                    # Check if it is jumped
                    if jumped_copy[ind]:
                        # Means its jumped, so unjump it
                        jump_name = self.psr.add_jump(sudo_select_mask)
                        self.updateJumped(jump_name)
                        if type(jump_name) != list:
                            log.error(f"Mistakenly added new jump {jump_name}")
                        else:
                            log.info(
                                f"Existing jump removed for {np.array(jump_name).astype(int).sum()} toas and deleted them"
                            )
                    # Now delete it
                    self.selected = self.psr.delete_TOAs([toa_ind], self.selected)
                    self.updateAllJumped()
                    self.jumped |= unselect_jump_stat
                    self.psr.update_resids()
                    self.updatePlot(keepAxes=True)
                    self.call_updates()
                if event.button == 1:
                    # Left click is select
                    self.selected[ind] = not self.selected[ind]
                    self.updatePlot(keepAxes=True)
                    # if point is being selected (instead of unselected) or
                    # point is unselected but other points remain selected
                    if self.selected[ind] or any(self.selected):
                        # update selected_toas object w/ selected points
                        self.psr.selected_toas = self.psr.all_toas[self.selected]
                        self.psr.update_resids()
                        self.call_updates()

    def clickAndDrag(self, event):
        """
        Call this function when the mouse is clicked and dragged
        """
        #log.debug(f"You clicked and dragged in mode '{self.plkToolbar.mode}'")
        # The following is for a selection if not in zoom mode
        #if "zoom" not in self.plkToolbar.mode and event.inaxes == self.plkAxes:
        if event.inaxes == self.plkAxes:
            xmin, xmax = self.pressEvent.xdata, event.xdata
            ymin, ymax = self.pressEvent.ydata, event.ydata
            if xmin > xmax:
                xmin, xmax = xmax, xmin
            if ymin > ymax:
                ymin, ymax = ymax, ymin
            selected = (self.xvals.value > xmin) & (self.xvals.value < xmax)
            selected &= (self.yvals.value > ymin) & (self.yvals.value < ymax)
            self.selected |= selected
            self.updatePlot(keepAxes=True)
            #self.plkCanvas._tkcanvas.delete(self.brect)
            if any(self.selected):
                self.psr.selected_toas = self.psr.all_toas[self.selected]
                self.psr.update_resids()
                self.call_updates()
        else:
            # This just removes the rectangle from the zoom click and drag
            pass  # the rectangle is already removed in canvasReleaseEvent

    def canvasKeyEvent(self, event):
        """
        When one presses a button on the Figure/Canvas, this function is called.
        The coordinates of the click are stored in event.xdata, event.ydata
        """
        # Callback to the plkWidget, which handles all events
        self.keyPressEvent(event)

    def keyPressEvent(self, event, **kwargs):
        """
        A key is pressed. Handle all the shortcuts here.

        This function can be called as a callback from the Canvas, or as a
        callback from Qt. So first some parsing must be done
        """

        if hasattr(event.key, '__call__'):
            from_canvas = False
            self.propagate_key_up = True
            xpos, ypos = None, None
            ukey = event.key()
            modifiers = event.modifiers()

            log.debug(
                "Call-back key-press, canvas location not available"
            )
        else:
            from_canvas = True
            self.propagate_key_up = False
            xpos, ypos = event.xdata, event.ydata
            ukey, modifiers = mpl_key_to_qt_key(event.key)


        action = self.key_handlers.get((ukey, modifiers), None)
        if action: 
            action(xpos, ypos, from_canvas)

        # For propagate_key_up we'd need the Qt event. We don't have that
        # Since it's a matplotlib event, we're just not going to propagate it,
        # it's not recommended. TODO: Remove propagate_key_up
        if not from_canvas: # or self.propagate_key_up:
            # TODO: check when this is necessary
            if self.parent is not None:
                log.debug("Propagating key press to parent also")
                self.parent.keyPressEvent(event)

            super(PlkWidget, self).keyPressEvent(event, **kwargs)

    def handleKeyA(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyB(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyC(self, xpos=None, ypos=None, from_canvas=False):
        if self.psr.fitted:
            self.psr.fitter.get_parameter_correlation_matrix(
                pretty_print=True, prec=3, usecolor=True
            )

    def handleKeyD(self, xpos=None, ypos=None, from_canvas=False):
        # Get the current state of jumped toas
        jumped_copy = copy.deepcopy(self.jumped)
        unselect_jump_status = jumped_copy[~self.selected]

        # First update the jump status and then delete them
        if np.any(jumped_copy & self.selected):
            # Which means that there is an overlap between selected and jumped TOAs
            jump_name = self.psr.add_jump(self.selected)
            self.updateJumped(jump_name)
            # Here jump_name has to be a list
            if type(jump_name) != list:
                log.error(f"Mistakenly added new jump {jump_name}")
            else:
                log.info(
                    f"Existing jump removed for {np.array(jump_name).astype(int).sum()} toas and deleted them"
                )
        # Delete the selected points
        self.selected = self.psr.delete_TOAs(
            self.psr.all_toas.table["index"][self.selected], self.selected
        )
        self.updateAllJumped()

        # Restore the jumps back
        self.jumped |= unselect_jump_status
        self.psr.update_resids()
        self.updatePlot(keepAxes=True)
        self.call_updates()

    def handleKeyE(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyF(self, xpos=None, ypos=None, from_canvas=False):
        self.fit()

    def handleKeyG(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyH(self, xpos=None, ypos=None, from_canvas=False):
        print(helpstring)

    def handleKeyI(self, xpos=None, ypos=None, from_canvas=False):
        print("\n" + "-" * 40)
        print("Prefit model:")
        print("-" * 40)
        print(self.psr.prefit_model.as_parfile())

    def handleKeyJ(self, xpos=None, ypos=None, from_canvas=False):
        # jump the selected points, or unjump if already jumped
        jump_name = self.psr.add_jump(self.selected)
        self.updateJumped(jump_name)
        self.psr.selected_toas = copy.deepcopy(self.psr.all_toas)
        self.selected = np.zeros(self.psr.selected_toas.ntoas, dtype=bool)
        self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
        self.randomboxWidget.addRandomCheckbox(self)
        self.colorModeWidget.addColorModeCheckbox(self.color_modes)
        self.updatePlot(keepAxes=True)
        self.call_updates()

    def handleKeyK(self, xpos=None, ypos=None, from_canvas=False):
        """Rescale the axes"""
        self.updatePlot(keepAxes=False)

    def handleKeyL(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyM(self, xpos=None, ypos=None, from_canvas=False):
        print(self.psr.all_toas.get_highest_density_range())

    def handleKeyN(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyO(self, xpos=None, ypos=None, from_canvas=False):
        if self.psr.fitted:
            print("\n" + "-" * 40)
            print("Postfit model:")
            print("-" * 40)
            print(self.psr.postfit_model.as_parfile())
        else:
            log.warning("No postfit model to show")

    def handleKeyP(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyQ(self, xpos=None, ypos=None, from_canvas=False):
        log.info("Exiting.")
        self.propagate_key_up = True

    def handleKeyR(self, xpos=None, ypos=None, from_canvas=False):
        """Reset the pane"""
        self.reset()

    def handleKeyS(self, xpos=None, ypos=None, from_canvas=False):
        if self.psr.fitted:
            print(self.psr.fitter.get_summary())

    def handleKeyT(self, xpos=None, ypos=None, from_canvas=False):
        # Stash/unstash selected TOAs

        if np.all(
            ~self.selected
        ):  # if no TOAs are selected, attempt to unstash all TOAs
            if (
                self.psr.stashed is None
            ):  # if there is nothing in the stash, do nothing
                log.debug("Nothing to stash/unstash.")
                return None
            # otherwise, pull all TOAs out of the stash and set it to None
            log.debug(
                f"Unstashing {len(self.psr.stashed)-len(self.psr.all_toas)} TOAs"
            )
            self.psr.all_toas = copy.deepcopy(self.psr.stashed)
            self.selected = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
            self.psr.stashed = None
            self.updateAllJumped()
            self.psr.update_resids()
            self.updatePlot(keepAxes=False)

        else:  # if TOAs are selected, add them to the stash
            if (
                self.psr.stashed is None
            ):  # if there is nothing in the stash, copy current TOAs to stash
                jumped_copy = copy.deepcopy(self.jumped)
                self.updateAllJumped()
                all_jumped = copy.deepcopy(self.jumped)
                self.jumped = jumped_copy
                if (self.selected & all_jumped).any():
                    # if any of the points are jumped, tell the user to delete the jump(s) first
                    log.warning(
                        "Cannot stash jumped TOAs. Delete interfering jumps before stashing TOAs."
                    )
                    return None
                log.debug(f"Stashing {sum(self.selected)} TOAs")
                self.psr.stashed = copy.deepcopy(self.psr.all_toas)

            else:  # if the stash isn't empty, remove selected from front-facing TOAs
                log.debug(
                    f"Added {sum(self.selected)} TOAs to stash (stash now contains {len(self.psr.stashed.table)-len(self.psr.all_toas.table)+sum(self.selected)} TOAs)"
                )
            if self.psr.fitted and self.psr.use_pulse_numbers:
                self.psr.all_toas.compute_pulse_numbers(self.psr.postfit_model)

            # remove the newly-stashed TOAs from the front-facing TOAs
            self.psr.all_toas.table = self.psr.all_toas.table[~self.selected]
            self.psr.selected_toas = copy.deepcopy(self.psr.all_toas)
            self.selected = np.zeros(self.psr.all_toas.ntoas, dtype=bool)
            self.updateAllJumped()
            self.psr.update_resids()
            self.updatePlot(
                keepAxes=False
            )  # We often stash at beginning or end of array

            self.call_updates()


    def handleKeyU(self, xpos=None, ypos=None, from_canvas=False):
        self.unselect()

    def handleKeyV(self, xpos=None, ypos=None, from_canvas=False):
        # jump all clusters except the one(s) selected, or jump all clusters if none selected
        jumped_copy = copy.deepcopy(self.jumped)
        self.updateAllJumped()
        all_jumped = copy.deepcopy(self.jumped)
        self.jumped = jumped_copy
        clusters = list(self.psr.all_toas.table["clusters"])
        # jump each cluster, check doesn't overlap with existing jumps and selected
        for num in np.arange(max(clusters) + 1):
            cluster_bool = np.array([
                num == cluster for cluster in self.psr.all_toas.table["clusters"]
            ])
            if True in [
                a and b for a, b in zip(cluster_bool, self.selected)
            ] or True in [a and b for a, b in zip(cluster_bool, all_jumped)]:
                continue
            self.psr.selected_toas = self.psr.all_toas[cluster_bool]
            jump_name = self.psr.add_jump(cluster_bool)
            self.updateJumped(jump_name)
        if (
            self.selected is not None
            and self.selected is not []
            and all(self.selected)
        ):
            self.psr.selected_toas = self.all_toas[self.selected]
        self.fitboxesWidget.addFitCheckBoxes(self.psr.prefit_model)
        #self.randomboxWidget.addRandomCheckbox(self)
        #self.colorModeWidget.addColorModeCheckbox(self.color_modes)
        self.updatePlot(keepAxes=True)
        self.call_updates()

    def handleKeyW(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyX(self, xpos=None, ypos=None, from_canvas=False):
        self.print_chi2()

    def handleKeyY(self, xpos=None, ypos=None, from_canvas=False):
        pass

    def handleKeyZ(self, xpos=None, ypos=None, from_canvas=False):
        """Zoom"""
        #self.plkToolbar.zoom()
        #self.randomboxWidget.changeMode(self.plkToolbar.mode)
        pass

    def handleEscape(self, xpos=None, ypos=None, from_canvas=False):
        log.info("Exiting.")
        self.propagate_key_up = True

    def handleCtrlM(self, xpos=None, ypos=None, from_canvas=False):
        """Change the visible widgets"""
        self.layoutMode = (1+self.layoutMode)%5
        if self.layoutMode == 0:
            self.xyChoiceVisible = False
            self.fitboxVisible = False
            self.actionsVisible = False
        elif self.layoutMode == 1:
            self.xyChoiceVisible = True
            self.fitboxVisible = True
            self.actionsVisible = True
        elif self.layoutMode == 2:
            self.xyChoiceVisible = True
            self.fitboxVisible = False
            self.actionsVisible = False
        elif self.layoutMode == 3:
            self.xyChoiceVisible = False
            self.fitboxVisible = True
            self.actionsVisible = False
        elif self.layoutMode == 4:
            self.xyChoiceVisible = True
            self.fitboxVisible = True
            self.actionsVisible = False
        self.showVisibleWidgets()

    def handleCtrlJ(self, xpos=None, ypos=None, from_canvas=False):
        """This is handled by the parent window (through the menu shortcuts)"""
        self.propagate_key_up = True

    def subtractPhaseWrapSel(self, xpos=None, ypos=None, from_canvas=False):
        """Subtract a phase wrap for selected TOAs"""
        self.psr.add_phase_wrap(self.selected, -1)
        self.updatePlot(keepAxes=False)
        self.call_updates()
        log.info("Pulse number for selected points decreased.")

    def addPhaseWrapSel(self, xpos=None, ypos=None, from_canvas=False):
        """Add a phase wrap for selected TOAs"""
        self.psr.add_phase_wrap(self.selected, 1)
        self.updatePlot(keepAxes=False)
        self.call_updates()
        log.info("Pulse number for selected points increased.")

    def subtractPhaseWrapAfter(self, xpos=None, ypos=None, from_canvas=False):
        if np.sum(self.selected) > 0:
            later = (
                self.psr.selected_toas.get_mjds().max()
                < self.psr.all_toas.get_mjds()
            )
            self.psr.add_phase_wrap(later, -1)
            log.info(
                "Pulse numbers to the right (i.e. later in time) of selection were decreased."
            )
            self.updatePlot(keepAxes=False)
            self.call_updates()

    def addPhaseWrapAfter(self, xpos=None, ypos=None, from_canvas=False):
        if np.sum(self.selected) > 0:
            later = (
                self.psr.selected_toas.get_mjds().max()
                < self.psr.all_toas.get_mjds()
            )
            self.psr.add_phase_wrap(later, 1)
            log.info(
                "Pulse numbers to the right (i.e. later in time) of selection were increased."
            )
            self.updatePlot(keepAxes=False)
            self.call_updates()

