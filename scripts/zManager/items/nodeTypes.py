from PySide2 import QtWidgets, QtGui
from .. import icons
from . import base
from .nodeMapper import NODE_TYPES_WRAPPER


class ZivaNodeTypeItem(base.LabelItem):
    def __init__(self, parent, nodeType, nodes):
        super(ZivaNodeTypeItem, self).__init__(parent, nodeType)

        # add widgets
        self.setExpanded(False)
        self.setIcon(0, QtGui.QIcon(icons.ZIVA_ICON))

        # add nodes
        w = NODE_TYPES_WRAPPER.get(nodeType)
        for node in nodes:
            w(self, node)
