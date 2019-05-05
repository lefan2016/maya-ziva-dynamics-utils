from PySide2 import QtWidgets, QtGui
from maya import cmds

from .. import icons, widgets
from . import base, nodeTypes
from .nodeMapper import NODE_TYPES_WRAPPER


# ----------------------------------------------------------------------------


NODE_TYPES = cmds.pluginInfo("ziva.mll", query=True, dependNode=True)
NODE_TYPES.sort()


# ----------------------------------------------------------------------------


class MeshItem(base.TreeItem):
    def __init__(self, parent, node):
        super(MeshItem, self).__init__(parent)

        # add widgets
        widget = widgets.Node(self.treeWidget(), node)
        self.addWidget(widget)
        self.setIcon(0, QtGui.QIcon(icons.MESH_ICON))

    # ------------------------------------------------------------------------

    @property
    def search(self):
        """
        :return: Search string for filtering
        :rtype: str
        """
        return self._widget.node.lower()

    # ------------------------------------------------------------------------

    def clear(self):
        for i in reversed(range(self.childCount())):
            self.removeChild(self.child(i))

    def update(self):
        # clear
        self.clear()

        # get node from widget
        node = self._widget.node

        # add types
        for t in NODE_TYPES:
            # validate node type
            w = NODE_TYPES_WRAPPER.get(t)
            if not w:
                continue

            # get nodes
            try:
                connections = cmds.zQuery(node, type=t) or []
                connections.sort()
            except:
                continue

            # validate connections
            if not connections:
                continue

            # create node type container
            nodeTypes.ZivaNodeTypeItem(self, t, connections)

        # add line of actions
        # get fibers
        fibers = cmds.zQuery(node, type="zFiber")
        if not fibers:
            return

        # get attached line of actions
        lineOfActions = cmds.zQuery(fibers, lineOfAction=True)
        if not lineOfActions:
            return

        # add line of actions
        nodeTypes.ZivaNodeTypeItem(self, "zLineOfAction", lineOfActions)

    def updateWhenEmpty(self):
        if not self.childCount():
            self.update()
