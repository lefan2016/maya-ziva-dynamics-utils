from PySide2 import QtWidgets, QtCore, QtGui
from . import create, attach, mirror
from zUtils import contexts
from zUtils.ui import mayaWindow, getIconPath


class LineOfActionUtils(QtWidgets.QWidget):
    def __init__(self, parent):
        super(LineOfActionUtils, self).__init__(parent)

        # set as window
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Line of Action")
        self.setWindowIcon(QtGui.QIcon(getIconPath("zivaLogo.png")))
        self.resize(350, 25)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # add widgets
        cr = QtWidgets.QPushButton(self)
        cr.setText("Create Line of Action")
        cr.released.connect(self.createLineOfAction)
        layout.addWidget(cr)

        cl = QtWidgets.QPushButton(self)
        cl.setText("Cluster Line of Action")
        cl.released.connect(self.clusterLineOfAction)
        layout.addWidget(cl)

        mi = QtWidgets.QPushButton(self)
        mi.setText("Mirror Line of Action")
        mi.released.connect(self.mirrorLineOfAction)
        layout.addWidget(mi)

    # ------------------------------------------------------------------------

    def createLineOfAction(self):
        with contexts.UndoChunk():
            create.createLineOfActionFromSelection()

    def clusterLineOfAction(self):
        with contexts.UndoChunk():
            attach.clusterLineOfActionFromSelection()

    def mirrorLineOfAction(self):
        with contexts.UndoChunk():
            mirror.mirrorLineOfActionFromSelection()


def show():
    parent = mayaWindow()
    widget = LineOfActionUtils(parent)
    widget.show()
