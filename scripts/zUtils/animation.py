from maya import cmds


def getIncomingAnimationCurves(transforms):
    """
    Get the incoming animation curves from a list of transforms.

    :param str/list transforms:
    :return: Incoming animation curves
    :rtype: list
    """
    # get all connected animation curves
    animCurves = cmds.listConnections(
        transforms,
        source=True,
        destination=False,
        type="animCurve"
    ) or []

    # filter animation curves so it contains no set driven keys and
    # referenced animation curves
    return [
        animCurve
        for animCurve in animCurves
        if not cmds.listConnections("{}.input".format(animCurve))
        and not cmds.referenceQuery(animCurve, isNodeReferenced=True)
    ]


def getPlugFromAnimationCurves(animCurves):
    """
    Loop all animation curves and find the plug the output attribute connects
    too.

    :param list animCurves:
    :return: Plugs
    :rtype: list
    """
    # variables
    plugs = []

    # loop animation curves
    for animCurve in animCurves:
        # get connection
        connections = cmds.listConnections(
            "{}.output".format(animCurve),
            plugs=True,
            source=False,
            destination=True,
        ) or []

        # add to plugs
        plugs.extend(connections)

    return plugs


def getAnimationRange(animCurves):
    """
    Get the maximum animation range from all of the animation curves provided.
    The start frame will be the earliest keyframe of all animation curves and
    the end frame will be the latest keyframe of all animation curves.

    :param animCurves:
    :return: Animation Range
    :rtype: list
    :raise ValueError: When no animation curves are provided
    :raise ValueError: When no animation keyframes are found
    """
    # validate
    if not animCurves:
        ValueError("No animation curves found!")

    # variables
    frames = []

    # loop animation curves
    for animCurve in animCurves:
        # get key indices
        indices = cmds.keyframe(animCurve, query=True, indexValue=True)

        # skip if the animation curve only has one key
        if len(indices) <= 1:
            continue

        # add frames
        frames.extend(
            cmds.keyframe(
                animCurve,
                query=True,
                index=(indices[0], indices[-1])
            ) or []
        )

    # validate frames
    if not frames:
        ValueError("No animation keyframes found!")

    # get start and end frame
    return [min(frames), max(frames)]
