from maya import cmds
from . import api


def getIncomingAnimationCurves(transforms):
    """
    Get the incoming animation curves from a list of transforms.

    :param list transforms:
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


def setAnimationStartFrame(animCurves, startFrame=1001):
    """
    Shift all of the animation curves to make sure the first keyframe found
    from checking all of the animation curves starts on the provided frame.

    :param list animCurves:
    :param float/int startFrame:
    """
    # get animation range
    animStartFrame, _ = getAnimationRange(animCurves)

    # get shift amount
    shift = startFrame - animStartFrame

    # shift animation curves
    cmds.keyframe(animCurves, edit=True, relative=True, timeChange=shift)


def setAnimationDefaultValue(animCurves):
    """
    Loop all animation curves and find the attribute it connects to. Query the
    default value of that attribute and set a linear keyframe on the provided
    frame with the default value.

    :param list animCurves:
    """
    # loop animation curves
    for animCurve in animCurves:
        # get connection
        connections = cmds.listConnections(
            "{}.output".format(animCurve),
            plugs=True,
            source=False,
            destination=True,
        ) or []

        # validate connection
        if not connections:
            continue

        # get default value
        node, attr = connections[0].split(".", 1)
        default = cmds.attributeQuery(attr, node=node, listDefault=True)

        # validate default
        if not default:
            continue

        # create keyframe
        cmds.setKeyframe(
            animCurve,
            value=default[0],
            inTangentType="linear",
            outTangentType="linear",
        )


def addAnimationPreRoll(animCurves, moveControl):
    """
    Add a preroll animation to the provided animation curves using the
    technique described on the ziva dynamics website.

    Video: https://zivadynamics.com/resources/pre-roll-run-up-setup

    :param list animCurves:
    """
    # get current time
    currentFrame = cmds.currentTime(query=True)

    # get animation range
    animStartFrame, _ = getAnimationRange(animCurves)

    # get frames
    zeroPoseFrame = animStartFrame - 11
    movePoseFrame = animStartFrame - 10

    # set start frame keyframe to make incoming tangent linear
    cmds.currentTime(animStartFrame)
    cmds.setKeyframe(animCurves, inTangentType="linear")

    # get current move control position
    pos = cmds.xform(moveControl, query=True, os=True, t=True)
    forward = api.getRotationAxis(moveControl)
    y = api.listToVector([0, 1, 0])
    x = (y ^ forward).normal()
    z = (x ^ y).normal()

    # create matrix
    matrix = api.channelsToMatrix(x=x, y=y, z=z)

    # set move pose
    cmds.currentTime(movePoseFrame)
    setAnimationDefaultValue(animCurves)

    cmds.xform(moveControl, ws=True, matrix=api.matrixToList(matrix))
    cmds.xform(moveControl, os=True, t=[pos[0], 0, pos[2]])
    cmds.setKeyframe(moveControl)

    # set zero pose
    cmds.currentTime(zeroPoseFrame)
    setAnimationDefaultValue(animCurves)

    # reset current time
    cmds.currentTime(currentFrame)
