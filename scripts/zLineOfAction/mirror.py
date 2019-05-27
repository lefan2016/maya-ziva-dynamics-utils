from maya import cmds
from . import attach
from zUtils import path, curves, selection


def mirrorLineOfAction(transforms):
    """
    The parsed curves will be copied with a mirrored name. If if any clusters
    are connected to the curve the cluster states are copied and the mirrored
    parent on the source clusters will be found. If a curve name cannot be
    mirrored that curve will be skipped.

    :return: Mirrored line of actions
    :rtype: list
    """
    mirrored = []

    # loop transforms
    for transform in transforms:
        # get mirrored name
        name = path.getMirrorName(transform)

        # validate name
        if name == transform:
            continue

        # get curve shape
        curve = cmds.listRelatives(transform, type="nurbsCurve")[0]

        # duplicate curve
        mirror = cmds.duplicate(transform, name=name)[0]
        mirror = cmds.rename(mirror, name)
        curves.mirrorCurve(mirror)

        # create clusters mapper
        mapper = {}

        for cls in curves.getClustersFromCurve(curve):
            parent = cmds.listRelatives(cls, p=True)
            parent = parent[0] if parent else parent
            mapper[cls] = parent

        # mapper
        clusters = attach.clusterLineOfAction([mirror])

        # parent clusters
        for cls in clusters:
            # get parent
            name = path.getMirrorName(cls)
            parent = mapper.get(name)
            parent = path.getMirrorName(parent) if parent else None

            # validate parent
            if not parent or not cmds.objExists(parent):
                cmds.warning(
                    "Cluster parent of '{}' couldn't be determined!".format(
                        cls
                    )
                )
                continue

            # parent cluster
            cmds.parent(cls, parent)

            # get cluster state
            attr = "{}.visibility".format(name)
            locked = cmds.getAttr(attr, lock=True)
            visible = cmds.getAttr(attr)

            # set cluster state
            attr = "{}.visibility".format(cls)
            cmds.setAttr(attr, visible)
            cmds.setAttr(attr, lock=locked)

        mirrored.append(mirror)

    return mirrored


def mirrorLineOfActionFromSelection():
    """
    Loop the current selection and filter out the selected nurbsCurves.
    These curves will be copied with a mirrored name. If if any clusters are
    connected to the curve the cluster states are copied and the mirrored
    parent on the source clusters will be found. If a curve name cannot be
    mirrored that curve will be skipped.

    :return: Mirrored line of actions
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

    return mirrorLineOfAction(transforms)
