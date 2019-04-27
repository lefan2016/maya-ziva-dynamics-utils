from maya import cmds
from PySide2 import QtWidgets, QtCore, QtGui
from . import copy
from zUtils import contexts, selection, attributes
from zUtils.ui import mayaWindow, getIconPath


class ZivaPaintableSelection(QtWidgets.QWidget):
    plugUpdate = QtCore.Signal(str)

    def __init__(self, parent, name):
        super(ZivaPaintableSelection, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create button
        button = QtWidgets.QPushButton(self)
        button.setText(name)
        button.setFixedWidth(100)
        button.released.connect(self.updateSelection)
        layout.addWidget(button)

        # create label
        self.plug = QtWidgets.QComboBox(self)
        self.plug.currentIndexChanged[str].connect(self.plugUpdate.emit)
        layout.addWidget(self.plug)

    # ------------------------------------------------------------------------

    def updateSelection(self):
        # filter selection
        sel = cmds.ls(sl=True)
        sel = selection.filterByZivaTypes(sel)
        node = sel[0] if sel else None

        # update
        self.plug.clear()

        # validate node
        if not node:
            self.plugUpdate.emit(None)
            return

        # get connected mesh
        mesh = cmds.zQuery(node, mesh=True)[0]

        # get paintable plugs
        nodeType = cmds.nodeType(node)
        plugs = attributes.getPaintableAttributesFromTransform(mesh)
        attrs = plugs.get(nodeType, {}).get(node, {}).keys()
        attrs = [attributes.getPlug(node, a) for a in attrs]

        # add attributes
        self.plug.addItems(attrs)

        # emit plug
        plug = attrs[0] if attrs else None
        self.plugUpdate.emit(plug)


class CopySettings(QtWidgets.QWidget):
    copyReleased = QtCore.Signal(bool)

    def __init__(self, parent):
        super(CopySettings, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create button
        button = QtWidgets.QPushButton(self)
        button.setText("Copy")
        button.released.connect(self.triggerCopyReleased)
        layout.addWidget(button)

        # create checkbox
        self.reverse = QtWidgets.QCheckBox(self)
        self.reverse.setText("Reverse")
        self.reverse.setFixedWidth(65)
        layout.addWidget(self.reverse)

    # ------------------------------------------------------------------------

    def triggerCopyReleased(self):
        reverseState = self.reverse.isChecked()
        self.copyReleased.emit(reverseState)


class CopyWeights(QtWidgets.QWidget):
    def __init__(self, parent):
        super(CopyWeights, self).__init__(parent)

        # variable
        self._copyWeights = copy.CopyWeights()

        # set as window
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Copy Weights")
        self.setWindowIcon(QtGui.QIcon(getIconPath("zivaLogo.png")))
        self.resize(450, 25)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create source
        self.source = ZivaPaintableSelection(self, "Set Source")
        self.source.plugUpdate.connect(self.setSource)
        layout.addWidget(self.source)

        # create target
        self.target = ZivaPaintableSelection(self, "Set Target")
        self.target.plugUpdate.connect(self.setTarget)
        layout.addWidget(self.target)

        # create copy
        self.copy = CopySettings(self)
        self.copy.setEnabled(False)
        self.copy.copyReleased.connect(self.doCopy)
        layout.addWidget(self.copy)

    # ------------------------------------------------------------------------

    @property
    def copyWeights(self):
        """
        :return: Copy Weights instance
        :rtype: CopyWeights
        """
        return self._copyWeights

    # ------------------------------------------------------------------------

    def setSource(self, node):
        self.copyWeights.source = node
        self.validate()

    def setTarget(self, node):
        self.copyWeights.target = node
        self.validate()

    # ------------------------------------------------------------------------

    def validate(self):
        # validate weights
        state, message = self.copyWeights.validate()

        # update ui
        self.copy.setEnabled(state)

        # print debug message
        if message:
            print "DEBUG: copyWeights | {}".format(message)

    # ------------------------------------------------------------------------

    def doCopy(self, reverse):
        with contexts.UndoChunk():
            self.copyWeights.copy(reverse)


def show():
    parent = mayaWindow()
    widget = CopyWeights(parent)
    widget.show()
