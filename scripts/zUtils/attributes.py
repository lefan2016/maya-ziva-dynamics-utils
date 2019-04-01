from maya import cmds


def setDefaultValue(plug):
    """
    Loop all animation curves and find the attribute it connects to. Query the
    default value of that attribute and set a linear keyframe on the provided
    frame with the default value.

    :param str plug:
    """
    # get default value
    node, attr = plug.split(".", 1)
    default = cmds.attributeQuery(attr, node=node, listDefault=True)

    # validate default
    if not default:
        return

    # set default
    cmds.setAttr(plug, default[0])


def getPlug(node, attr):
    """
    :param str node:
    :param str attr:
    :return: Plug
    :rtype: str
    """
    return "{}.{}".format(node, attr)
