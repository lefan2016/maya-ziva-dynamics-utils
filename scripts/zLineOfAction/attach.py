from maya import cmds
from zUtils import path, curves, selection


def clusterLineOfAction(transforms):
    """
    Cluster the parsed curves. The first cv of the curve is considered the
    origin and the last cv the insertion. Any additional cluster will be
    numerated.

    :param list transforms:
    :return: Clusters
    :rtype: list
    """
    clusters = []

    # loop curves
    for transform in transforms:
        # get nice name
        name = path.getNiceName(transform)

        # get cluster transforms
        cluster = curves.clusterCurve(transform)

        # rename start and end cluster transforms
        origin = cmds.rename(
            cluster[0],
            "{}_origin_cls".format(name)
        )
        insertion = cmds.rename(
            cluster[-1],
            "{}_insertion_cls".format(name)
        )

        # rename middle clusters transforms
        middle = [
            cmds.rename(transform, "{}_cls_{0:02d}".format(name, i+1))
            for i, transform in enumerate(cluster[1:-1])
        ]

        # add to list
        clusters.append(origin)
        clusters.extend(middle)
        clusters.append(insertion)

    return clusters


def clusterLineOfActionFromSelection():
    """
    Cluster the selected curves. The first cv of the curve is considered the
    origin and the last cv the insertion. Any additional cluster will be
    numerated.

    :return: Clusters
    :rtype: list
    """
    # get selected curves
    sel = cmds.ls(sl=True, l=True)
    sel = selection.extendWithShapes(sel)
    sel = selection.filterByType(sel, "nurbsCurve")

    # get transform of curves
    transforms = [
        cmds.listRelatives(s, parent=True)[0]
        for s in sel
    ]

    return clusterLineOfAction(transforms)
