from maya import cmds
from . import base, mesh
from zUtils import contexts


class MeshTissueItem(base.CheckBoxItem):
    def __init__(self, parent, container, meshes):
        super(MeshTissueItem, self).__init__(parent, container)

        # variables
        states = []

        # loop meshes
        for m in meshes:
            # add mesh
            item = mesh.MeshItem(self, m)
            item.setExpanded(True)

            # get tissue enabled state
            tissue = cmds.zQuery(m, type="zTissue")[0]
            states.append(cmds.getAttr("{}.enable".format(tissue)))

        # set checked default state
        self.widget.setChecked(all(states))
        self.widget.stateChanged.connect(self.setEnabledTissues)

    # ------------------------------------------------------------------------

    def setEnabledTissues(self, state):
        """
        Loop all children of the container and set the zTissue node that is
        attached to the child nodes to the provided state. This function makes
        it easier to enable/disable large groups of tissues.

        :param bool state:
        """
        with contexts.UndoChunk():
            state = True if state == 2 else False
            num = self.childCount()
            for i in range(num):
                m = self.child(i)
                tissue = cmds.zQuery(m.widget.node, type="zTissue")[0]
                cmds.setAttr("{}.enable".format(tissue), state)


class TissuesItem(base.LabelItem):
    def __init__(self, parent, solver):
        super(TissuesItem, self).__init__(parent, text="tissues")
        self.setExpanded(True)

        # variable
        data = {}

        # get tissues
        meshes = cmds.zQuery(solver, mesh=True, type="zTissue")
        meshes.sort()

        # filter tissues
        for m in meshes:
            p = cmds.listRelatives(m, parent=True)
            p = p[0] if p else "None"

            if p not in data.keys():
                data[p] = []
            data[p].append(m)

        # add tissues
        for container, meshes in data.iteritems():
            # add parent
            parent = MeshTissueItem(self, container, meshes)
            parent.setExpanded(True)
