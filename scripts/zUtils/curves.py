from maya import cmds


def getNumCVs(curve):
    """
    :param str curve:
    :return: Number of cvs
    :rtype: int
    """
    # get attributes
    spans = cmds.getAttr("{}.spans".format(curve))
    degree = cmds.getAttr("{}.degree".format(curve))
    form = cmds.getAttr("{}.form".format(curve))

    # get num cvs
    numCVs = spans + degree

    # adjust for closed curve
    if form == 2:
        numCVs -= degree

    return numCVs


def mirrorCurve(curve):
    """
    :param str curve:
    """
    num = getNumCVs(curve)
    for i in range(num):
        cv = "{}.cv[{}]".format(curve, i)
        pos = cmds.xform(cv, q=True, ws=True, t=True)
        cmds.xform(cv, ws=True, t=[pos[0] * -1, pos[1], pos[2]])


def clusterCurve(curve):
    """
    :param str curve:
    :return: Clusters
    :rtype: list
    """
    clusters = []
    num = getNumCVs(curve)

    # create clusters
    for i in range(num):
        cluster = cmds.cluster("{}.cv[{}]".format(curve, i))[-1]
        clusters.append(cluster)

    return clusters


def getClustersFromCurve(curve):
    """
    :param str curve:
    :return: Clusters
    :rtype: list
    """
    # get clusters
    clusters = cmds.listConnections(curve, type="objectSet") or []
    clusters = cmds.listConnections(clusters, type="cluster") or []
    clusters = list(set(clusters))

    return [
        cmds.listConnections("{}.matrix".format(cls), type="transform")[0]
        for cls in clusters
    ]
