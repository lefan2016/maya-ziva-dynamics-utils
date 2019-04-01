from maya import cmds
from collections import OrderedDict
from . import api, attributes


# ----------------------------------------------------------------------------


SOLVER_PARENT = "solver_parent"


# ----------------------------------------------------------------------------


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


class DisableAutoKeyframe(object):
    """
    This context temporarily disables the auto keyframe command. If auto
    keyframe is turned off before going into this context no changes will be
    made.

    .. highlight::
        with DisableAutoKeyframe:
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


class AnimationExport(object):
    def __init__(self, container=None, mover=None, exporter=None):
        # define variables
        self._container = None
        self._mover = None
        self._exporter = None
        self._solver = None
        self._solverName = "solver_parent_grp"

        self._animationPlugs = []
        self._animationNodes = []
        self._animationCurves = []

        self._animationStartFrame = None
        self._animationEndFrame = None

        # set variables
        self.container = container
        self.mover = mover
        self.exporter = exporter

    # ------------------------------------------------------------------------

    @property
    def container(self):
        """
        The container node is a node in the hierarchy of which either itself
        or its children contain all of the animation curve that move the
        character. This can be a control rig or even a skeleton hierarchy.

        :param str container:
        :return: Container node
        :rtype: str
        """
        return self._container

    @container.setter
    def container(self, container):
        # set container
        self._container = container

        # validate container
        if not container:
            self._animationPlugs = []
            self._animationNodes = []
            self._animationCurves = []

            self._animationStartFrame = None
            self._animationEndFrame = None

            return

        # get content
        nodes = self._getTransformContent(container)

        # loop nodes
        for node in nodes:
            # get animation curves
            curves = getIncomingAnimationCurves(node)

            # validate curves
            if curves:
                # get plugs
                plugs = getPlugFromAnimationCurves(curves)

                # populate animation variables
                self._animationPlugs.extend(plugs)
                self._animationNodes.append(node)
                self._animationCurves.extend(curves)

        # set animation range
        self._animationStartFrame, self._animationEndFrame = \
            getAnimationRange(self._animationCurves)

    # ------------------------------------------------------------------------

    @property
    def mover(self):
        """
        The mover node is the node that indicates the one frame move in the
        pre roll animation. Any other animated transforms found will be moved
        relative to the mover node.

        :param str mover:
        :return: Mover node
        :rtype: str
        """
        return self._mover

    @mover.setter
    def mover(self, mover):
        self._mover = mover

    # ------------------------------------------------------------------------

    @property
    def exporter(self):
        """
        The exporter node is the node that indicates which group and its
        children to export as an alembic cache.

        :param str exporter:
        :return: Parent node to export
        :rtype: str
        """
        return self._exporter

    @exporter.setter
    def exporter(self, exporter):
        # set exporter
        self._exporter = exporter

        # validate exporter
        if not exporter:
            self._solver = None
            return

        # find/create solver
        children = cmds.listRelatives(exporter, children=True) or []
        children = [child.split("|")[-1] for child in children]

        if SOLVER_PARENT in children:
            self._solver = "{}|{}".format(exporter, SOLVER_PARENT)
        else:
            self._solver = cmds.group(
                empty=True,
                parent=self.exporter,
                name=SOLVER_PARENT
            )

    # ------------------------------------------------------------------------

    def _getTransformContent(self, transform):
        """
        Get all of the children of the transform including itself.
        The content list is sorted based on hierarchy to reduce the errors in
        settings transforms.

        :return: Container contents
        :rtype: list
        """
        # get all of the container children
        children = cmds.listRelatives(
            transform,
            allDescendents=True,
            fullPath=True
        ) or []

        # add container itself
        children.append(transform)

        # sort container based on hierarchy
        children.sort(key=lambda x: len(x.split("|")))

        return children

    # ------------------------------------------------------------------------

    def _getWorldMatrix(self, node, time=None):
        """
        :param str node:
        :param int/float/None time:
        :return: World matrix of node at given or current time
        :rtype: list
        """
        plug = attributes.getPlug(node, "worldMatrix[0]")
        arguments = {"time": time} if time else {}
        return cmds.getAttr(plug, **arguments)

    def _getMatrixDifference(self, sourceMatrix, targetMatrix, start, end):
        """
        :param list sourceMatrix:
        :param list targetMatrix:
        :param int start:
        :param int end:
        :return: Matrix difference
        :rtype: float
        """
        return sum(
            [
                a1 - a2
                for a1, a2 in zip(
                    sourceMatrix[start:end],
                    targetMatrix[start:end]
                )
            ]
        )

    # ------------------------------------------------------------------------

    def _getMoverRotationVectors(self, zeroMatrix, animMatrix):
        """
        Get the mover rotation vectors with the constraint that the rotation
        vectors are only allowed to be rotating the mover in the Y axis
        relative to its zero pose.

        :param MMatrix zeroMatrix:
        :param MMatrix animMatrix:
        :return: Rotation Vectors
        :rtype: list
        """
        # get forward vector from anim matrix
        forward = api.listToVector([0, 0, 1])
        forward = forward.transformAsNormal(animMatrix)

        # get up vector from zero matrix
        y = api.listToVector([0, 1, 0])
        y = y.transformAsNormal(zeroMatrix)

        # construct direction vectors
        x = (y ^ forward).normal()
        z = (x ^ y).normal()

        return [x, y, z]

    def _getMoverTranslation(self, zeroMatrix, animMatrix):
        """
        Get the mover relative position constrained in the Y axis based on
        the zero position.

        :param list zeroMatrix:
        :param list animMatrix:
        :return: Position
        :rtype: list
        """
        return [animMatrix[12], zeroMatrix[13], animMatrix[14]]

    # ------------------------------------------------------------------------

    def _splitPlugsByChannel(self, plugs):
        """
        :param list plugs:
        :return: Split plugs
        :rtype: dict
        """
        data = {}
        channels = ["translate", "rotate", "scale"]

        for plug in plugs:
            for channel in channels:
                if plug.count(channel):
                    if not channel in data.keys():
                        data[channel] = []
                    data[channel].append(plug)

        return data

    # ------------------------------------------------------------------------

    def _setAnimKeyframes(self):
        """
        The animation pose is already keyframed, as it is the start of all of
        the animation. The reason for keying all of the curves again is to
        make sure an actual key is set at the start frame which doesn't have
        to be a given. The other reason is to make sure the in tangent type is
        set to linear to make sure the pre roll blend is linear.
        """
        # set frame
        cmds.currentTime(self._animationStartFrame)

        # set keyframes
        cmds.setKeyframe(self._animationCurves, inTangentType="linear")

    def _setZeroKeyframes(self):
        """
        The zero pose is retrieved by changing all of the attributes back to
        its default value.
        """
        # set frame
        cmds.currentTime(self._zeroFrame)

        # set default values
        for plug in self._animationPlugs:
            attributes.setDefaultValue(plug)

        # set keyframes
        cmds.setKeyframe(
            self._animationPlugs + [self._solver],
            inTangentType="linear",
            outTangentType="linear"
        )

    def _setMoverKeyframes(self, maxInterations):
        """
        The mover pose is the closest the zero pose can get to the animation
        pose by just moving the mover node. The mover node is allowed to be
        rotated in Y and moved in X and Z.

        :param int maxInterations:
        """
        # variable
        i = 0

        # set frame
        cmds.currentTime(self._moveFrame)

        # get bind and anim matrices
        zeroMatrixList = self._getWorldMatrix(self.mover, self._zeroFrame)
        zeroMatrix = api.listToMatrix(zeroMatrixList)

        animMatrixList = self._getWorldMatrix(self.mover, self._animationStartFrame)
        animMatrix = api.listToMatrix(animMatrixList)

        # construct mover matrix
        # get rotation vectors and translation
        x, y, z = self._getMoverRotationVectors(zeroMatrix, animMatrix)
        t = self._getMoverTranslation(zeroMatrixList, animMatrixList)

        # construct mover matrix
        moverMatrix = api.channelsToMatrix(x, y, z, t)
        relativeMatrix = moverMatrix * zeroMatrix.inverse()

        # store world positions of all of the transforms, as controls can
        # influence each other it is important to check if the set transform
        # is set to the correct position.
        transformData = OrderedDict()
        for transform in self._animationNodes + [self._solver]:
            # get transformation matrix
            zeroMatrixList = self._getWorldMatrix(transform, self._zeroFrame)
            zeroMatrix = api.listToMatrix(zeroMatrixList)

            # get transforms world position as matrix
            transformMatrix = api.matrixToList(zeroMatrix * relativeMatrix)

            # store data
            transformData[transform] = transformMatrix

        # set positions
        while transformData:
            # set matrices
            for transform, transformMatrix in transformData.iteritems():
                cmds.xform(transform, ws=True, matrix=transformMatrix)

            # validate matrices
            for transform, transformMatrix in transformData.iteritems():
                # get connect animation curves to only keyframe necessary
                # attributes
                connections = getIncomingAnimationCurves(transform)
                plugs = getPlugFromAnimationCurves(connections)
                plugsData = self._splitPlugsByChannel(plugs)

                # get current matrix
                currentMatrix = self._getWorldMatrix(transform)

                # get matrix range
                # exclude rotations if no rotation plugs are found
                start = 0 if plugsData.get("rotate") else 12
                end = 16 if plugsData.get("rotate") else 15

                # get numeric difference value between matrices
                difference = self._getMatrixDifference(
                    transformMatrix,
                    currentMatrix,
                    start,
                    end
                )

                # validate difference
                if difference > 0.0001:
                    continue

                # set keyframes
                cmds.setKeyframe(
                    plugs,
                    inTangentType="linear",
                    outTangentType="linear"
                )

                # remove from dict
                del transformData[transform]

            # update iteration
            i += 1

            # handle max iterations to not get stuck in while loop when
            # transforms cannot be resolved
            if i == maxInterations:
                break

    # ------------------------------------------------------------------------

    def setStartFrame(self, startFrame=1001):
        """
        Shift all of the animation curves so the animation starts at the
        provided frame.

        :param int/float startFrame:
        :raise ValueError: No animation curves found
        """
        # validate animation curves
        if not self._animationCurves:
            raise ValueError("No animation curves found to shift!")

        # get animation range
        startFrameAnim, _ = getAnimationRange(self._animationCurves)

        # get shift amount
        shift = startFrame - startFrameAnim

        # shift animation curves
        cmds.keyframe(
            self._animationCurves,
            edit=True,
            relative=True,
            timeChange=shift
        )

        # set animation range
        self._animationStartFrame, self._animationEndFrame = \
            getAnimationRange(self._animationCurves)

    def addPreRoll(self, transitionFrames=10, maxIterations=10):
        """
        This function will allow you to add a pre roll animation before the`
        existing animation. This pre roll animation follows the technique
        described on the ziva dynamics website. There is a one frame jump
        in which the solver needs to move too. The duration of the transition
        between poses can be adjusted. The jump frame will be as close as
        possible to the first animation frame.

        :param int transitionFrames:
        :param int maxIterations:
        """
        # get key frame values
        self._moveFrame = self._animationStartFrame - transitionFrames
        self._zeroFrame = self._moveFrame - 1

        # set keyframes
        with DisableAutoKeyframe():
            self._setAnimKeyframes()
            self._setZeroKeyframes()
            self._setMoverKeyframes(maxIterations)

        # set current frame to zero frame
        cmds.currentTime(self._zeroFrame)
