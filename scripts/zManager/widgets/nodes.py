from PySide2 import QtWidgets
from maya import cmds
from .base import Button


class Node(QtWidgets.QWidget):
    def __init__(self, parent, node, text=None):
        super(Node, self).__init__(parent)

        # variable
        self._node = node
        text = text if text else node

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # add combo box
        button = Button(self, text)
        button.released.connect(self.doSelect)
        layout.addWidget(button)

    # ------------------------------------------------------------------------

    @property
    def node(self):
        """
        :return: Node
        :rtype: str
        """
        return self._node

    # ------------------------------------------------------------------------

    def doSelect(self):
        if cmds.objExists(self.node):
            cmds.select(self.node)
