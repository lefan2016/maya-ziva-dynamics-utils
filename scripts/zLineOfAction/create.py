from maya import cmds
from zUtils import path


def createLineOfAction(transforms):
    """
    Loop the provided transforms list see if a zFiber is connected to the
    object. If this is the case the zLineOfActionUtil function is used
    to create a curve based on the fiber direction. This curve is then
    renamed to reflect the name of the selection and the color is changed
    to red.

    :return: Created line of actions
    :rtype: list
    """
    curves = []

    for transform in transforms:
        # get name
        name = path.getNiceName(transform)
        name = "{}_crv".format(name)

        if cmds.objExists(name):
            continue

        if not cmds.zQuery(transform, type="zFiber"):
            continue

        # create curve
        curveShape, fiber = cmds.zLineOfActionUtil(transform)

        # color curve
        cmds.setAttr("{0}.overrideEnabled".format(curveShape), 1)
        cmds.setAttr("{0}.overrideColor".format(curveShape), 13)

        # rename curve
        curve = cmds.listRelatives(curveShape, p=True)[0]
        curve = cmds.rename(curve, name)

        curves.append(curve)

    return curves


def createLineOfActionFromSelection():
    """
    Loop the current selection and see if a zFiber is connected to the
    object. If this is the case the zLineOfActionUtil function is used
    to create a curve based on the fiber direction. This curve is then
    renamed to reflect the name of the selection and the color is changed
    to red.

    :return: Created line of actions
    :rtype: list
    """
    selection = cmds.ls(sl=True, l=True) or []
    return createLineOfAction(selection)
