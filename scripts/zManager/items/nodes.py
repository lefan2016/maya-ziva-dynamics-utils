from PySide2 import QtWidgets, QtGui
from maya import cmds
from .. import icons, widgets
from . import base, actions


class ZivaNodeItem(base.TreeItem):
    def __init__(self, parent, node, text=None):
        super(ZivaNodeItem, self).__init__(parent)

        # add widgets
        widget = widgets.Node(self.treeWidget(), node, text)
        self.addWidget(widget)
        self.setExpanded(True)


class CurveNodeItem(base.TreeItem):
    def __init__(self, parent, node):
        super(CurveNodeItem, self).__init__(parent)

        # add widgets
        widget = widgets.Node(self.treeWidget(), node)
        self.addWidget(widget)
        self.setIcon(0, QtGui.QIcon(icons.LINE_ICON))


class ZivaLineOfActionNodeItem(ZivaNodeItem):
    def __init__(self, parent, node):
        super(ZivaLineOfActionNodeItem, self).__init__(parent, node)
        self.setExpanded(False)

        # get curves
        curves = cmds.listConnections("{}.curves".format(node)) or []

        # add curves
        for curve in curves:
            CurveNodeItem(self, curve)


class ZivaWeightNodeItem(ZivaNodeItem):
    def __init__(self, parent, node):
        super(ZivaWeightNodeItem, self).__init__(parent, node)
        actions.PaintItem(self, node, "weights")


class ZivaFiberNodeItem(ZivaNodeItem):
    def __init__(self, parent, node):
        super(ZivaFiberNodeItem, self).__init__(parent, node)
        actions.PaintItem(self, node, "endPoints")
        actions.PaintItem(self, node, "weights")


class ZivaAttachmentNodeItem(ZivaNodeItem):
    def __init__(self, parent, node):
        super(ZivaAttachmentNodeItem, self).__init__(parent, node)
        self.setExpanded(False)

        source = cmds.zQuery(node, attachmentSource=True)[0]
        target = cmds.zQuery(node, attachmentTarget=True)[0]

        ZivaNodeItem(self, source, "source")
        ZivaNodeItem(self, target, "target")
        actions.PaintItem(self, node, "weights")
