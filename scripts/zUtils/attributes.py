from maya import cmds
from . import decorators


# ----------------------------------------------------------------------------


TYPE_MAPPER = {
    int: {"attributeType": "long"},
    float: {"attributeType": "float"},
    str: {"dataType": "string"},
    unicode: {"dataType": "string"},
    type(None): {"dataType": "string"}
}


# ----------------------------------------------------------------------------


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


# ----------------------------------------------------------------------------


def createTag(node, attr, value=None):
    """
    :param str node:
    :param str attr:
    :param str/int/float/None value:
    :raise ValueError:
        If the provided value doesn't match any of the supported data types
    """
    # validate attribute
    if cmds.objExists(getPlug(node, attr)):
        return

    # get arguments from value
    kwargsCreate = TYPE_MAPPER.get(type(value), {})
    if not kwargsCreate and value:
        raise ValueError(
            "A value of type '{}' is not supported!".format(type(value))
        )

    # create attribute
    cmds.addAttr(
        node,
        shortName=attr,
        longName=attr,
        keyable=False,
        **kwargsCreate
    )

    # validate value
    if not value:
        return

    # set value
    dataType = kwargsCreate.get("dataType")
    kwargsSet = {"type": "string"} if dataType == "string" else {}
    cmds.setAttr(getPlug(node, attr), value, **kwargsSet)


def getTag(node, attr):
    """
    :param str node:
    :param str attr:
    :return: Tag value
    :rtype: str/unicode/int/float
    """
    plug = getPlug(node, attr)
    if cmds.objExists(plug):
        return cmds.getAttr(plug)


# ----------------------------------------------------------------------------


def createLink(source, target, attr):
    """
    :param str source:
    :param str target:
    :param str attr:
    """
    # create tags
    createTag(source, attr)
    createTag(target, attr)

    # connect tags
    sourcePlug = getPlug(source, attr)
    targetPlug = getPlug(target, attr)

    if not cmds.isConnected(sourcePlug, targetPlug):
        cmds.connectAttr(sourcePlug, targetPlug, force=True)


def removeLink(source, target, attr):
    """
    :param str source:
    :param str target:
    :param str attr:
    """
    # disconnect tags
    sourcePlug = getPlug(source, attr)
    targetPlug = getPlug(target, attr)

    if cmds.isConnected(sourcePlug, targetPlug):
        cmds.disconnectAttr(sourcePlug, targetPlug)

    if cmds.objExists(sourcePlug):
        cmds.deleteAttr(sourcePlug)

    if cmds.objExists(targetPlug):
        cmds.deleteAttr(targetPlug)


def getLink(node, attr, destination=False, source=False):
    """
    :param node:
    :param attr:
    :return: Linked node
    :rtype: str/None
    """
    # validate plug
    plug = getPlug(node, attr)
    if not cmds.objExists(plug):
        return

    # get connections
    connections = cmds.listConnections(
        plug,
        destination=destination,
        source=source
    )

    # link connections
    if connections:
        return connections[0]


# ----------------------------------------------------------------------------


@decorators.preserveSelection
def getPaintableAttributesFromTransform(transform):
    """
    Get all of the paintable attributes from a transform. The paintable
    attributes are listed under node type and then nodes in the dictionary.

    :param str transform:
    :return: Paintable attributes
    :rtype: dict
    """
    # variables
    data = {}

    # select node, the node needs to be selected for the maya command to work
    # for this reason the preserve selection decorator is added to this
    # function.
    cmds.select(transform)

    # get paintable attributes
    commands = cmds.artBuildPaintMenu().split()

    # loop commands
    for command in commands:
        # split command
        nodeType, node, attr, _ = command.split(".")

        if nodeType not in data.keys():
            data[nodeType] = {}

        if node not in data.get(nodeType).keys():
            data[nodeType][node] = {}

        # get actual attribute
        attrs = [
            a.rsplit("[", 1)[0]
            for a in cmds.listAttr(node, multi=True, string=attr) or []
            if a.count("{}[".format(attr))
        ]
        full = attrs[0] if attrs else attr

        # validate attribute
        if not cmds.objExists(getPlug(node, full)):
            continue

        # populate data
        data[nodeType][node][full] = ".".join([nodeType, node, attr])

    return data
