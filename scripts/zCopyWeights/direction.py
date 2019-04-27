from maya import cmds
from .copy import CopyWeights
from zUtils import attributes, selection


def reverseFiberDirectionFromSelection():
    """
    Reverse the direction of the selected zFiber nodes end points.
    :raise RuntimeError: When no selection is made
    """
    # get selected fibers
    fibers = cmds.ls(sl=True) or []
    fibers = selection.filterByType(fibers, types="zFiber")

    # validate selection
    if not fibers:
        raise RuntimeError("Make a selection containing zFiber node(s)!")

    # reverse direction
    for fiber in fibers:
        reverseFiberDirection(fiber)


def reverseFiberDirection(fiber):
    """
    Reverse the direction of the zFiber nodes end points.

    :param str fiber:
    :raise TypeError: When parsed node is not of type zFiber
    """
    if cmds.nodeType(fiber) != "zFiber":
        print TypeError("Parsed node is not of type zFiber!")

    plug = attributes.getPlug(fiber, "endPoints")
    weights = CopyWeights(plug, plug)
    weights.copy(reverse=True)
