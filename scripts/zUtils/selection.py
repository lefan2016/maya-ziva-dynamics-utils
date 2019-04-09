from maya import cmds


def extendWithShapes(selection):
    """
    Extend the parsed selection with the selections shapes.

    :param list selection:
    :return: Extended selection
    :rtype: list
    """
    shapes = cmds.listRelatives(
        selection,
        shapes=True,
        f=True,
        ni=True
    ) or []

    selection = cmds.ls(selection, long=True)
    selection.extend(shapes)

    return selection


def filterByType(selection, types):
    """
    Filter the parsed selection based on type. The type argument can be of
    type string or list, depending on how many types you would like to filter
    by.

    :param list selection:
    :param str/list types:
    :return: Filtered selection
    :rtype: list
    """
    return cmds.ls(selection, type=types)
