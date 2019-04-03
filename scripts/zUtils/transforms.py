from maya import cmds
from . import attributes


def getWorldMatrixAtTime(node, time=None):
    """
    :param str node:
    :param int/float/None time:
    :return: World matrix of node at given or current time
    :rtype: list
    """
    plug = attributes.getPlug(node, "worldMatrix[0]")
    arguments = {"time": time} if time else {}
    return cmds.getAttr(plug, **arguments)
