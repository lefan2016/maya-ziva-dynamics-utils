from PySide2 import QtWidgets, QtCore, QtGui
from . import geometry
from zUtils import contexts
from zUtils.ui import mayaWindow, getIconPath


class GeometryProximity(QtWidgets.QWidget):
    def __init__(self, parent):
        super(GeometryProximity, self).__init__(parent)

        # set as window
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Select Geometry by Proximity")
        self.setWindowIcon(QtGui.QIcon(getIconPath("zivaLogo.png")))
        self.resize(350, 25)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create input
        self.r = QtWidgets.QDoubleSpinBox(self)
        self.r.setValue(0.25)
        self.r.setMinimum(0.05)
        self.r.setSingleStep(0.05)
        self.r.setDecimals(2)
        layout.addWidget(self.r)

        # create button
        button = QtWidgets.QPushButton(self)
        button.setText("Select")
        button.released.connect(self.doSelection)
        layout.addWidget(button)

    # ------------------------------------------------------------------------

    def doSelection(self):
        with contexts.UndoChunk():
            r = self.r.value()
            geometry.selectGeometryByProximity(r)


def show():
    parent = mayaWindow()
    widget = GeometryProximity(parent)
    widget.show()
