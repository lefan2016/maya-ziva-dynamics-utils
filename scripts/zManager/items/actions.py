from maya import cmds, mel
from .. import widgets
from . import base


class PaintItem(base.TreeItem):
    def __init__(self, parent, node, attr):
        super(PaintItem, self).__init__(parent)

        # variable
        self._node = node
        self._attr = "{}.{}.{}".format(
            cmds.nodeType(node),
            node,
            attr
        )

        # add widgets
        widget = widgets.Button(self.treeWidget(), attr)
        widget.released.connect(self.paint)
        self.addWidget(widget)

    # ------------------------------------------------------------------------

    @property
    def node(self):
        """
        :return: Node
        :rtype: str
        """
        return self._node

    @property
    def attr(self):
        """
        :return: Paintable attributes
        :rtype: str
        """
        return self._attr

    # ------------------------------------------------------------------------

    def paint(self):
        """
        Select the associated mesh and initialize the paint tools.
        """
        # select mesh
        mesh = cmds.zQuery(self.node, mesh=True)[0]
        cmds.select(mesh)

        # set tool
        cmd = 'artSetToolAndSelectAttr("artAttrCtx", "{}")'.format(self.attr)
        mel.eval(cmd)
