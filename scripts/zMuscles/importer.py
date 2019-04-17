from maya import cmds
from zUtils import path, contexts, transforms, attributes, decorators
from zAnimation import Animation

from .base import Muscles
from .tags import (
    ZIVA_MUSCLES_ANIMATION,
    ZIVA_SOLVER,
    ZIVA_SOLVER_ATTRIBUTES
)


# ----------------------------------------------------------------------------


class MusclesAnimationImport(Muscles):
    def __init__(self, root, character=None, animation=None, solver=None):
        super(MusclesAnimationImport, self).__init__(root, character)

        # validate animation
        if not animation and not self.animation:
            raise RuntimeError("Declare the 'animation' variable!")

        # validate solver
        if not solver and not self.solver:
            raise RuntimeError("Declare the 'solver' variable!")

        # set animation if declared
        if animation:
            attributes.createLink(self.root, animation, ZIVA_MUSCLES_ANIMATION)

        # set solver if declared
        if solver:
            attributes.createLink(self.root, solver, ZIVA_SOLVER)

    # ------------------------------------------------------------------------

    @property
    def animation(self):
        """
        :return: Ziva animation importer node
        :rtype: str
        """
        return attributes.getLink(
            self.root,
            ZIVA_MUSCLES_ANIMATION,
            destination=True
        )

    @property
    def solver(self):
        """
        :return: Ziva solver node
        :rtype: str
        """
        return attributes.getLink(self.root, ZIVA_SOLVER, destination=True)

    # ------------------------------------------------------------------------

    def _transferAnimation(self, animation):
        """
        Create a driving connection between matches of the animation and
        muscle rig. Meshes will be checked to see if they

        :param AnimationExport animation:
        """
        # get meshes
        sources = cmds.listRelatives(animation.root, allDescendents=True)
        targets = cmds.listRelatives(self.animation, allDescendents=True)

        # get meshes mappers
        mapper = {path.getName(t): t for t in targets}

        # loop source meshes
        for source in sources:
            # get target mesh
            name = path.getName(source)
            target = mapper.get(name)

            if not target:
                s = "DEBUG: transferAnimation | Unable to find target for {}!"
                print s.format(source)
                continue

            # get connections
            connections = cmds.listConnections(
                source,
                type="AlembicNode",
                plugs=True,
                connections=True,
                skipConversionNodes=True,
                source=True,
                destination=False
            ) or []

            # do connections
            targetAttributes = [t.split(".", 1)[-1] for t in connections[::2]]
            sourcePlugs = connections[1::2]

            for sourcePlug, attr in zip(sourcePlugs, targetAttributes):
                targetPlug = attributes.getPlug(target, attr)
                cmds.connectAttr(sourcePlug, targetPlug, force=True)

    def _createSolverAnimation(self, animation):
        """
        Create solver animation. It handles the first frame jump and the
        substeps on the solver.

        :param AnimationExport animation:
        """
        # set animation start frame
        plug = attributes.getPlug(self.solver, "startFrame")
        cmds.setAttr(plug, animation.startFrame)

        # get solver mover plugs
        plugs = [
            attributes.getPlug(self.solver, attr)
            for attr in ZIVA_SOLVER_ATTRIBUTES
        ]

        # create first frame jump
        for frame in [animation.startFrame, animation.startFrame + 1]:
            # set time
            cmds.currentTime(frame)

            # position solver
            matrix = transforms.getWorldMatrixAtTime(animation.solver)
            cmds.xform(self.solver, ws=True, matrix=matrix)

            # set keyframes
            cmds.setKeyframe(
                plugs,
                inTangentType="linear",
                outTangentType="linear"
            )

        # create sub step frame jump
        plug = attributes.getPlug(self.solver, "substeps")

        # set keyframes
        tangents = {"inTangentType": "linear", "outTangentType": "linear"}
        cmds.setKeyframe(plug, time=animation.startFrame + 2, **tangents)
        cmds.setKeyframe(plug, time=animation.startFrame + 1, value=1, **tangents)
        cmds.setKeyframe(plug, time=animation.startFrame, value=1, **tangents)

    # ------------------------------------------------------------------------

    def _removeAnimation(self):
        """
        Loop al nodes in the animation container and remove any connection
        made to an AlembicNode.
        """
        # get nodes
        nodes = cmds.listRelatives(self.animation, allDescendents=True)

        # get connections
        connections = cmds.listConnections(
            nodes,
            type="AlembicNode",
            plugs=True,
            connections=True,
            skipConversionNodes=True,
            source=True,
            destination=False
        ) or []

        # remove connections
        sourcePlugs = connections[1::2]
        targetPlugs = connections[::2]

        for source, target in zip(sourcePlugs, targetPlugs):
            cmds.disconnectAttr(source, target)
            attributes.setDefaultValue(target)

    def _removeSolverAnimation(self):
        """
        Loop al keyframed attributes on the solver and delete any animation
        curves connected to it.
        """
        # remove animation curves from solver
        for attr in ZIVA_SOLVER_ATTRIBUTES + ["substeps"]:
            plug = attributes.getPlug(self.solver, attr)
            anim = cmds.listConnections(
                plug,
                type="animCurve",
                source=True,
                destination=False,
                skipConversionNodes=True
            )

            if anim:
                cmds.delete(anim)

    # ------------------------------------------------------------------------

    def getAnimations(self):
        """
        :return: Exported animation
        :rtype: list
        """
        return Animation.getAnimationsFromScene().get(self.character, [])

    # ------------------------------------------------------------------------

    def removeAnimation(self):
        """
        Loop all meshes in the importer node and see if a blendshape node is
        connected. If this is the case remove the blendshape node.
        """
        # disable ziva solvers
        with contexts.DisableZivaSolvers():
            # set start frame of existing solver frame
            plug = attributes.getPlug(self.solver, "startFrame")
            frame = cmds.getAttr(plug)
            cmds.currentTime(frame)

            # remove animation
            self._removeAnimation()
            self._removeSolverAnimation()

    def applyAnimation(self, animation):
        """
        :param AnimationExport animation:
        """
        # disable ziva solvers
        with contexts.DisableZivaSolvers():
            # set start frame of existing solver frame
            plug = attributes.getPlug(self.solver, "startFrame")
            frame = cmds.getAttr(plug)
            cmds.currentTime(frame)

            # remove existing animation
            self.removeAnimation()

            # create animation
            self._transferAnimation(animation)
            self._createSolverAnimation(animation)
