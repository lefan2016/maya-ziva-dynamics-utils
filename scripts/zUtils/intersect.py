from maya import cmds


def intersect1D(min1, max1, min2, max2):
    """
    Return the overlapping state on a 1 dimensional level.

    :param int/float min1:
    :param int/float max1:
    :param int/float min2:
    :param int/float max2:
    :return: Overlapping state
    :rtype: bool
    """
    return min1 < max2 and min2 < max1


def intersectBoundingBox(object1, object2, buffer):
    """
    Return the overlapping state of two objects.

    :param str object1:
    :param str object2:
    :param float buffer:
    :return: Overlapping state
    :rtype: bool
    """
    bb1 = cmds.xform(object1, query=True, ws=True, boundingBox=True)
    bb2 = cmds.xform(object2, query=True, ws=True, boundingBox=True)

    return (
        intersect1D(bb1[0] - buffer, bb1[3] + buffer, bb2[0], bb2[3]) and
        intersect1D(bb1[1] - buffer, bb1[4] + buffer, bb2[1], bb2[4]) and
        intersect1D(bb1[2] - buffer, bb1[5] + buffer, bb2[2], bb2[5])
    )
