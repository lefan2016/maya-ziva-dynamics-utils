from maya import cmds
from . import api, attributes


class DisableAutoKeyframe(object):
    """
    This context temporarily disables the auto keyframe command. If auto
    keyframe is turned off before going into this context no changes will be
    made.

    .. highlight::
        with DisableAutoKeyframe():
            # code
    """
    def __init__(self):
        self._state = cmds.autoKeyframe(query=True, state=True)

    # ------------------------------------------------------------------------

    def __enter__(self):
        if self._state:
            cmds.autoKeyframe(state=0)

    def __exit__(self, *exc_info):
        if self._state:
            cmds.autoKeyframe(state=1)


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


def addAnimationPreRoll(container, mover):
    """
    Add a preroll animation to the provided animation curves using the
    technique described on the ziva dynamics website.

    Video: https://zivadynamics.com/resources/pre-roll-run-up-setup

    :param str container:
    :param str mover:
    """
    def _setAnimPose(frame):
        # set frame
        cmds.currentTime(frame)

        # set keyframes
        cmds.setKeyframe(animCurves, inTangentType="linear")

    def _setZeroPose(frame):
        # set frame
        cmds.currentTime(frame)

        # set default values
        for plug in animPlugs:
            attributes.setDefaultValue(plug)

        # set keyframes
        cmds.setKeyframe(
            animPlugs,
            inTangentType="linear",
            outTangentType="linear"
        )

    def _setMoverPose(frame, bind, anim):
        # set frame
        cmds.currentTime(frame)

        # get attr
        moverAttr = "{}.worldMatrix".format(mover)

        # get bind and anim matrices
        bindMatrixList = cmds.getAttr(moverAttr, time=bind)
        bindMatrix = api.listToMatrix(bindMatrixList)

        animMatrixList = cmds.getAttr(moverAttr, time=anim)
        animMatrix = api.listToMatrix(animMatrixList)

        # find best transformation matrix
        # get forward vector from anim matrix
        forwardVec = api.listToVector([0, 0, 1])
        forward = forwardVec.transformAsNormal(animMatrix)

        # construct direction vectors
        y = api.listToVector([0, 1, 0])
        x = (y ^ forward).normal()
        z = (x ^ y).normal()

        # construct position list ( keeping the bind Y and animation X and Z )
        t = [
            animMatrixList[12],
            bindMatrixList[13],
            animMatrixList[14]
        ]

        # construct mover matrix
        moverMatrix = api.channelsToMatrix(x, y, z, t)
        relativeMatrix = moverMatrix * bindMatrix.inverse()

        # loop transforms
        for transform in animTransforms:
            # get connect animation curves to only keyframe necessary
            # attributes
            connections = getIncomingAnimationCurves(transform)
            plugs = getPlugFromAnimationCurves(connections)

            # get transformation matrix
            transformAttr = "{}.worldMatrix".format(transform)
            transformMatrixList = cmds.getAttr(transformAttr, time=bind)
            transformMatrix = api.listToMatrix(transformMatrixList)

            # set new position
            positionMatrix = api.matrixToList(transformMatrix * relativeMatrix)
            cmds.xform(transform, ws=True, matrix=positionMatrix)

            # set keyframes
            cmds.setKeyframe(
                plugs,
                inTangentType="linear",
                outTangentType="linear"
            )

    # variables
    animPlugs = []
    animCurves = []
    animTransforms = []

    # process container contents
    children = cmds.listRelatives(container, allDescendents=True) or []
    children.insert(0, container)

    # loop container contents
    for child in children:
        # get animation curves
        curves = getIncomingAnimationCurves(child)

        # validate curves
        if curves:
            # get plugs
            plugs = getPlugFromAnimationCurves(curves)

            # populate anim variables
            animPlugs.extend(plugs)
            animCurves.extend(curves)
            animTransforms.append(child)

    # get animation range
    animPoseFrame, _ = getAnimationRange(animCurves)
    zeroPoseFrame = animPoseFrame - 11
    moverPoseFrame = animPoseFrame - 10

    # set keyframes
    with DisableAutoKeyframe():
        _setAnimPose(animPoseFrame)
        _setZeroPose(zeroPoseFrame)
        _setMoverPose(moverPoseFrame, zeroPoseFrame, animPoseFrame)

    # set to start of preroll
    cmds.currentTime(zeroPoseFrame)
