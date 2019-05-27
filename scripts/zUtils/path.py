REPLACE = ["_mesh", "_bone", "_crv"]
MIRROR = {"r_": "l_", "l_": "r_"}


def getBase(path):
    """
    :param str path:
    :return: Base
    :rtype: str
    """
    return path.split("|")[-1]


def getName(path):
    """
    :param str path:
    :return: Name
    :rtype: str
    """
    return getBase(path).split(":")[-1]


def getMirrorName(path):
    """
    :param str path:
    :return: Mirrored name
    :rtype: str
    """
    # get name
    name = getName(path)

    # get mirror string
    replace = MIRROR.get(name[:2].lower())

    # return parsed path if no replacement is found
    if not replace:
        return name

    # replace side section of path
    return replace + name[2:]


def getNiceName(path, replace=REPLACE):
    """
    :param str path:
    :param list replace:
    :return: Name
    :rtype: str
    """
    # get name
    name = getName(path)

    # do name replacements
    for r in replace:
        name = name.replace(r, "")

    return name


# ----------------------------------------------------------------------------


def getNamespace(path):
    """
    :param str path:
    :return: Namespace
    :rtype: str
    """
    base = getBase(path)
    if base.find(":") != -1:
        return base.split(":")[0]


def removeNamespace(node):
    """
    :param str node:
    :return: Namespace-less path
    :rtype: str
    """
    sections = [
        s.split(":")[-1] if s.count(":") else s
        for s in node.split("|")
    ]

    return "|".join(sections)

