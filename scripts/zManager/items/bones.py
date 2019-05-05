from maya import cmds
from . import base, mesh


class BonesItem(base.LabelItem):
    def __init__(self, parent, solver):
        super(BonesItem, self).__init__(parent, text="bones")
        self.setExpanded(False)

        # get bones
        meshes = cmds.zQuery(solver, mesh=True, type="zBone") or []
        meshes.sort()

        # add bones
        for m in meshes:
            item = mesh.MeshItem(self, m)
            item.setExpanded(True)
