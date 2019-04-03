from maya import cmds
from collections import OrderedDict
from . import api, attributes, decorators


# ----------------------------------------------------------------------------


ZIVA_ANIMATION = "__ziva_animation"
ZIVA_ANIMATION_START = "__ziva_animation_start"
ZIVA_ANIMATION_END = "__ziva_animation_end"
ZIVA_ANIMATION_TRANSITION = "__ziva_animation_transition"
ZIVA_ANIMATION_CONTAINER = "__ziva_animation_container"
ZIVA_ANIMATION_MOVER = "__ziva_animation_mover"
ZIVA_SOLVER_PARENT = "__ziva_solver_parent"



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


class Animation(object):
    def __init__(self, root, character=None):
        # define variables
        self._root = root

        # validate character
        if not character and not self.character:
            raise RuntimeError("Declare the 'character' variable!")

        if self.character is None and character:
            # create export tags
            attributes.createTag(self.root, ZIVA_ANIMATION, character)

            # create animation tags
            attributes.createTag(self.root, ZIVA_ANIMATION_START, 0.0)
            attributes.createTag(self.root, ZIVA_ANIMATION_END, 0.0)
            attributes.createTag(self.root, ZIVA_ANIMATION_TRANSITION, 0.0)

    # ------------------------------------------------------------------------

    @classmethod
    def getAnimationsFromScene(cls):
        """
        Loop over all transforms and that contain an export animation tag.
        Read the value of this tag and add it into a dictionary.

        :return: Exported animation from current scene
        :rtype: dict
        """
        # data variable
        data = {}

        # loop transforms
        for node in cmds.ls(transforms=True):
            # get plug
            plug = attributes.getPlug(node, ZIVA_ANIMATION)

            # validate plug
            if cmds.objExists(plug):
                # get character
                character = cmds.getAttr(plug)

                # add character to dictionary
                if character not in data.keys():
                    data[character] = []

                # add animation to dictionary
                data[character].append(cls(node, character))

        return data

    # ------------------------------------------------------------------------

    @property
    def character(self):
        """
        The character name gets stored throughout the importing and exporting
        process. It is the value that links an import and export.

        :return: Character name
        :rtype: str
        """
        return attributes.getTag(self.root, ZIVA_ANIMATION)

    @property
    def root(self):
        """
        The root node is the node that indicates the root of the animation
        node. Either in import or export mode.

        :return: Root node
        :rtype: str
        """
        return self._root

    # ------------------------------------------------------------------------

    @property
    def startFrame(self):
        """
        :param int/float value:
        :return: Animation start frame
        :rtype: int/float
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_START)
        return cmds.getAttr(plug)

    @startFrame.setter
    def startFrame(self, value):
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_START)
        cmds.setAttr(plug, value)

    @property
    def endFrame(self):
        """
        :param int/float value:
        :return: Animation end frame
        :rtype: int/float
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_END)
        return cmds.getAttr(plug)

    @endFrame.setter
    def endFrame(self, value):
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_END)
        cmds.setAttr(plug, value)

    @property
    def transitionFrames(self):
        """
        :param int/float value:
        :return: Animation transition frames
        :rtype: int/float
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_TRANSITION)
        return cmds.getAttr(plug)

    @transitionFrames.setter
    def transitionFrames(self, value):
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_TRANSITION)
        cmds.setAttr(plug, value)


class AnimationExport(Animation):
    def __init__(self, root, character=None, container=None, mover=None):
        super(AnimationExport, self).__init__(root, character)

        # variables
        self._animationPlugs = []
        self._animationNodes = []
        self._animationCurves = []
        self._additionalKeyframes = {}

        # validate container
        if not container and not self.container:
            raise RuntimeError("Declare the 'container' variable!")

        # validate mover
        if not mover and not self.mover:
            raise RuntimeError("Declare the 'mover' variable!")

        # set character and root if declared
        if character:
            attributes.createTag(self.root, ZIVA_ANIMATION, character)

            # create animation tags
            attributes.createTag(self.root, ZIVA_ANIMATION_START, 0.0)
            attributes.createTag(self.root, ZIVA_ANIMATION_END, 0.0)
            attributes.createTag(self.root, ZIVA_ANIMATION_TRANSITION, 0.0)

        # set container and mover if declared
        if container:
            self.container = container
        if mover:
            self.mover = mover

        # create solver parent
        self._createSolverParent()

        # initialize animation data
        self._updateAnimationData()

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
        return attributes.getLink(
            self.root,
            ZIVA_ANIMATION_CONTAINER,
            destination=True
        )

    @container.setter
    def container(self, container):
        # remove existing container
        if self.container:
            attributes.removeLink(
                self.root,
                self.container,
                ZIVA_ANIMATION_CONTAINER
            )

        # set new container
        if container:
            attributes.createLink(
                self.root,
                container,
                ZIVA_ANIMATION_CONTAINER
            )

        self._updateAnimationData()

    # ------------------------------------------------------------------------

    @property
    def solver(self):
        """
        The solver parent group is used to drive the ziva solver with the
        snapping of the character created in the pre roll animation.

        :return: Solver parent
        :rtype: str/None
        """
        # the reason for looping through it's children rather than relying on
        # a link is that when exporting an alembic this link attribute
        # connection is not respected.
        for child in cmds.listRelatives(self.root, children=True):
            if cmds.objExists(attributes.getPlug(child, ZIVA_SOLVER_PARENT)):
                return child

    @decorators.preserveSelection
    def _createSolverParent(self):
        """
        Create and tag the solver parent node. If the solver already exists
        no new solver will be created. As the solver is to be exported it
        will be parented underneath the root node.
        """
        # validate solver
        if self.solver:
            return

        # create solver node
        parent = cmds.createNode(
            "transform",
            name="solver_parent",
            skipSelect=True
        )
        parent = cmds.parent(parent, self.root)[0]

        # create link
        attributes.createLink(
            self.root,
            parent,
            ZIVA_SOLVER_PARENT
        )

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
        return attributes.getLink(
            self.root,
            ZIVA_ANIMATION_MOVER,
            destination=True
        )

    @mover.setter
    def mover(self, mover):
        # remove existing mover
        if self.mover:
            attributes.removeLink(
                self.root,
                self.mover,
                ZIVA_ANIMATION_MOVER
            )

        # set new mover
        if mover:
            attributes.createLink(
                self.root,
                mover,
                ZIVA_ANIMATION_MOVER
            )

    # ------------------------------------------------------------------------

    @property
    def additionalKeyframes(self):
        """
        Additional keyframes are in dictionary format and the keys are the
        plugs and the values the values. Sometimes it can be your additional
        keys are either not key framed by default or don't have the correct
        default value. For example is better to calculate the pre roll using
        FK systems. Additional keyframes can be used to force a certain state.

        :return: Additional keyframes
        :rtype: dict
        """
        return self._additionalKeyframes

    def addAdditionalKeyframe(self, plug, value):
        """
        :param str plug:
        :param int/float value:
        """
        self.additionalKeyframes[plug] = value

    def removeAdditionalKeyframe(self, plug):
        """
        :param str plug:
        """
        if plug in self.additionalKeyframes.keys():
            del self.additionalKeyframes[plug]

    # ------------------------------------------------------------------------

    def _updateAnimationData(self):
        """
        When the container updates this function should be called to populate
        the animation data. This animation data is used in both the shift
        animation and adding pre roll animation functions.
        """
        # validate container
        if not self.container:
            self._animationPlugs = []
            self._animationNodes = []
            self._animationCurves = []

            self.startFrame = None
            self.endFrame = None

            return

        # get content
        nodes = self._getTransformContent(self.container)

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
        self.startFrame, self.endFrame = \
            getAnimationRange(self._animationCurves)

    # ------------------------------------------------------------------------

    def _storeAnimationStartFrame(self, value):
        """
        :param int/float value:
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_START)
        cmds.setAttr(plug, value)

    def _storeAnimationEndFrame(self, value):
        """
        :param int/float value:
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_END)
        cmds.setAttr(plug, value)

    def _storeAnimationTransitionFrames(self, value):
        """
        :param int/float value:
        """
        plug = attributes.getPlug(self.root, ZIVA_ANIMATION_TRANSITION)
        cmds.setAttr(plug, value)

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
        cmds.currentTime(self.startFrame)

        # set keyframes
        cmds.setKeyframe(
            self._animationCurves + self.additionalKeyframes.keys(),
            inTangentType="linear"
        )

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

        # set additional keyframe values
        for plug, value in self.additionalKeyframes.iteritems():
            cmds.setAttr(plug, value)

        # get nodes
        nodes = []
        nodes.append(self.solver)
        nodes.extend(self._animationPlugs)
        nodes.extend(self.additionalKeyframes.keys())

        # set keyframes
        cmds.setKeyframe(
            nodes,
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

        animMatrixList = self._getWorldMatrix(self.mover, self.startFrame)
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
        for transform in self._animationNodes + [self.solver]:
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

        if self.additionalKeyframes:
            # set additional keyframe values
            for plug, value in self.additionalKeyframes.iteritems():
                cmds.setAttr(plug, value)

            # set keyframes
            cmds.setKeyframe(
                self.additionalKeyframes.keys(),
                inTangentType="linear",
                outTangentType="linear"
            )

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
        self.startFrame, self.endFrame = \
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
        # store transition frames
        self.transitionFrames = transitionFrames

        # get key frame values
        self._moveFrame = self.startFrame - transitionFrames
        self._zeroFrame = self._moveFrame - 1

        # set keyframes
        with DisableAutoKeyframe():
            self._setAnimKeyframes()
            self._setZeroKeyframes()
            self._setMoverKeyframes(maxIterations)

        # set current frame to zero frame
        cmds.currentTime(self._zeroFrame)

    # ------------------------------------------------------------------------

    @decorators.loadAlembicExportPlugin
    def export(self, output, step=1):
        """
        Export an alembic cache of the root node. All the animation will
        be shifted to frame 1001 for consistency and a pre roll will be added
        to the animation.

        :param str output:
        :param int/float step:
        """
        # get frame range
        start, end = getAnimationRange(self._animationCurves)

        # store frame range
        self._storeAnimationStartFrame(start)
        self._storeAnimationEndFrame(end)

        # construct attributes
        attrs = [
            "-attr {}".format(attr)
            for attr in [
                ZIVA_ANIMATION,
                ZIVA_SOLVER_PARENT,
                ZIVA_ANIMATION_TRANSITION,
                ZIVA_ANIMATION_START,
                ZIVA_ANIMATION_END
            ]
        ]

        # construct command
        cmd = " ".join(
            [
                "-frameRange {} {}".format(start, end),
                "-step {}".format(step),
                " ".join(attrs),
                "-wholeFrameGeo",
                "-worldSpace",
                "-writeVisibility",
                "-eulerFilter",
                "-dataFormat ogawa",
                "-root '{}'".format(self.root),
                "-file '{}'".format(output)
            ]
        )

        # execute command
        cmds.AbcExport(j=cmd)
