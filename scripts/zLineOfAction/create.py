from maya import cmds
from zUtils import path


def createLineOfAction():
    curves = []
    selection = cmds.ls(sl=True) or []
    for sel in selection:
        if not cmds.zQuery(sel, type="zFiber"):
            continue

        curveShape, fiber = cmds.zLineOfActionUtil(sel)
        curve = cmds.listRelatives(curveShape, p=True)[0]
        curve = cmds.rename(curve, "{}_crv".format(path.getNiceName(sel)))
        curves.append(curve)

    return curves