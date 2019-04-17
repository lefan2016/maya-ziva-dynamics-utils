from maya import cmds
from zUtils import path


def createLineOfAction():
    """
    Loop the current selection and see if a zFiber is connected to the
    object. If this is the case the zLineOfActionUtil function is used
    to create a curve based on the fiber direction. This curve is then
    renamed to reflect the name of the selection and the color is changed
    to red.

    :return: Created line of actions
    :rtype: list
    """
    curves = []
    selection = cmds.ls(sl=True) or []
    for sel in selection:
        if not cmds.zQuery(sel, type="zFiber"):
            continue

        # create curve
        curveShape, fiber = cmds.zLineOfActionUtil(sel)

        # color curve
        cmds.setAttr("{0}.overrideEnabled".format(curveShape), 1)
        cmds.setAttr("{0}.overrideColor".format(curveShape), 13)

        # rename curve
        curve = cmds.listRelatives(curveShape, p=True)[0]
        curve = cmds.rename(curve, "{}_crv".format(path.getNiceName(sel)))
        curves.append(curve)

    return curves
