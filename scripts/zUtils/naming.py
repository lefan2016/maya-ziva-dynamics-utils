from maya import cmds
from . import path


# ----------------------------------------------------------------------------


SPACER = "_"
PADDING = 2
STRIP = ["mesh", "bone"]

ATTACHMENT_TYPES = ["zAttachment"]
DIRECT_TYPES = ["zFiber", "zMaterial", "zTet", "zGeo", "zBone", "zTissue"]


# ----------------------------------------------------------------------------


def mapper():
    """
    :return: Rename function mapper based on nodeType
    :rtype: dict
    """
    types = {}
    types.update({t: autoNameAttachment for t in ATTACHMENT_TYPES})
    types.update({t: autoNameDirect for t in DIRECT_TYPES})
    types.update(
        {
            "zSolver": autoNameSolverConnections,
            "transform": autoNameMeshConnections
        }
    )

    return types


def rename(node, name):
    """
    The rename function is a helper function to mayas standard rename. It will
    pad a number behind the name if the provided name already exists in the
    scene. The number of padding is adjustable in the static variables.

    :param str node:
    :param str name:
    """
    # validate rename
    if path.getName(node) == name:
        return

    # check if node exists
    if cmds.objExists(name):
        # store existing node
        existingNode = name

        # get new name and rename existing node with a number
        name = SPACER.join([name, "1".zfill(PADDING)])
        cmds.rename(existingNode, name)
        print("DEBUG: autoNaming | {} -> {}".format(existingNode, name))

    # rename node
    cmds.rename(node, name)
    print("DEBUG: autoNaming | {} -> {}".format(node, name))


def strip(name):
    """
    The strip function strips the name and checks if the part of the name is
    present in the STRIP variable. If it is it will be omitted. The attach
    function is they used to stitch the sections together.
    :param str name:
    :return: Stripped name
    :rtype: str
    """
    sections = [s for s in split(name) if s not in STRIP]
    return attach(sections)


# ----------------------------------------------------------------------------


def attach(sections):
    """
    Override this function if you naming convention is not based on snake
    case. The attach function will stitch sections together into a single
    string.

    :param sections:
    :return: Name
    :rtype: str
    """
    return "_".join(sections)


def split(node):
    """
    Override this function if your naming convention is not based on snake
    case. The strip function will first split the name of the node into its
    different sections. These section will then be tested to see if some
    parts can be omitted.

    :param str node:
    :return: Split name
    :rtype: list
    """
    name = path.getName(node)
    return name.split("_")


# ----------------------------------------------------------------------------


def autoNameSelected():
    """
    Name selected nodes based on nodetype. The mapper function will be used
    to map naming function against nodeType.
    """
    # get selection
    selection = cmds.ls(sl=True) or []

    # get mapper
    nodeTypesMapper = mapper()

    # loop selection
    for sel in selection:
        # get node type
        nodeType = cmds.nodeType(sel)

        # get name function based on node type
        func = nodeTypesMapper.get(nodeType)

        # validate function
        if not func:
            continue

        # run function
        func(sel)


# ----------------------------------------------------------------------------


def autoNameSolverConnections(node):
    """
    Name all of the connections made to the zSolver. Connected meshes are
    found and from there the individual nodes are handled.

    :param str node:
    """
    # get meshes connected to solver
    meshes = cmds.zQuery(node, mesh=True)

    # name meshes
    for mesh in meshes:
        autoNameMeshConnections(mesh)


def autoNameMeshConnections(mesh):
    """
    Find all the Ziva node types connected to the mesh and name them
    accordingly.

    :param str mesh:
    """
    # get all ziva dependency node types
    nodeTypes = cmds.pluginInfo("ziva.mll", query=True, dependNode=True)
    nodeTypesMapper = mapper()

    # loop node types
    for nodeType in nodeTypes:
        # skip transforms and solver as they trigger a cycle
        if nodeType in ["zSolver", "transform"]:
            continue

        # get naming function
        func = nodeTypesMapper.get(nodeType)

        # skip if function doesn't exists
        if not func:
            continue

        # get connected nodes of provided type
        connections = cmds.zQuery(mesh, type=nodeType) or []

        # rename nodes
        for connection in connections:
            func(connection)


# ----------------------------------------------------------------------------


def autoNameAttachment(node):
    """
    Name the zAttachment node.
    Format: {attachmentSource}{SPACER}{attachmentTarget}{SPACER}zAttachment

    :param str node:
    """
    # validate node type
    if cmds.nodeType(node) not in ATTACHMENT_TYPES:
        raise ValueError("Please provide a {} node!".format(ATTACHMENT_TYPES))

    # get attachments
    source = cmds.zQuery(node, attachmentSource=True)
    target = cmds.zQuery(node, attachmentTarget=True)

    # combine names
    source = "_".join([strip(s) for s in source])
    target = "_".join([strip(t) for t in target])

    # combine source and target
    name = SPACER.join([source, target, "zAttachment"])

    # rename
    rename(node, name)


def autoNameDirect(node):
    """
    Name the directly connected nodes.
    Format: {mesh}{SPACER}{nodeType}

    :param str node:
    """
    # validate node type
    if cmds.nodeType(node) not in DIRECT_TYPES:
        raise ValueError("Please provide a {} node!".format(DIRECT_TYPES))

    # get attachments
    mesh = cmds.zQuery(node, mesh=True)
    mesh = "_".join([strip(m) for m in mesh])

    # combine source and target
    name = SPACER.join([mesh, cmds.nodeType(node)])

    # rename
    rename(node, name)
