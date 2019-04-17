from maya import cmds
from zUtils import path, curves, selection


def clusterLineOfAction():
    """
    Cluster the selected curves. The first cv of the curve is considered the
    origin and the last cv the insertion. Any additional cluster will be
    numerated.

    :return: Clusters
    :rtype: list
    """
    clusters = []

    # get selected curves
    sel = cmds.ls(sl=True)
    sel = selection.extendWithShapes(sel)
    sel = selection.filterByType(sel, "nurbsCurve")

    # loop curves
    for curve in sel:
        # get nice name
        parent = cmds.listRelatives(curve, parent=True)[0]
        name = path.getNiceName(parent)

        # get cluster transforms
        transforms = curves.clusterCurve(curve)

        # rename start and end cluster transforms
        origin = cmds.rename(
            transforms[0],
            "{}_origin_cls".format(name)
        )
        insertion = cmds.rename(
            transforms[-1],
            "{}_insertion_cls".format(name)
        )

        # rename middle clusters transforms
        middle = [
            cmds.rename(transform, "{}_cls_{0:02d}".format(name, i+1))
            for i, transform in enumerate(transforms[1:-1])
        ]

        # add to list
        clusters.append(origin)
        clusters.extend(middle)
        clusters.append(insertion)

    return clusters
