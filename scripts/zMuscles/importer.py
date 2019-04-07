from maya import cmds
from zUtils import path, contexts, transforms, attributes
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

    def _getMeshTransforms(self, node):
        """
        Get all descendents of a node and filter all of its meshes. Once the
        meshes are found the direct parent of this mesh is added to the list
        that is returned.

        :param str node:
        :return: Mesh transforms
        :rtype: list
        """
        meshes = cmds.listRelatives(node, allDescendents=True, type="mesh")
        return [cmds.listRelatives(m, parent=True)[0] for m in meshes]

    # ------------------------------------------------------------------------

    def _createBlendshapes(self, animation):
        """
        Create blendshapes between matches it can find between the animation
        and muscle rig.

        :param AnimationExport animation:
        """
        # get meshes
        sourceMeshes = self._getMeshTransforms(animation.root)
        targetMeshes = self._getMeshTransforms(self.animation)

        # get meshes mappers
        mapper = {path.getName(m): m for m in targetMeshes}

        # remove existing animation on target nodes
        for source in sourceMeshes:
            # get target mesh
            name = path.getName(source)
            target = mapper.get(name)

            if not target:
                continue

            # apply blendshape
            cmds.blendShape(
                source,
                target,
                frontOfChain=True,
                weight=[0, 1],
                origin="world"
            )

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

    def _removeBlendshapes(self):
        """
        Loop all meshes and see if there is a blendshape connected to it. If
        it is remove the blendshape node.
        """
        # get meshes
        meshes = cmds.listRelatives(
            self.animation,
            allDescendents=True,
            type="mesh"
        )

        # remove blendshapes from history
        for mesh in meshes:
            blendshapes = [
                node
                for node in cmds.listHistory(mesh)
                if cmds.nodeType(node) == "blendShape"
            ]

            if blendshapes:
                cmds.delete(blendshapes)

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
        self._removeBlendshapes()
        self._removeSolverAnimation()

    def applyAnimation(self, animation):
        """
        :param AnimationExport animation:
        """
        # set start frame of existing solver frame
        plug = attributes.getPlug(self.solver, "startFrame")
        frame = cmds.getAttr(plug)
        cmds.currentTime(frame)

        # disable ziva solvers
        with contexts.DisableZivaSolvers():
            # remove existing animation
            self.removeAnimation()

            # create animation
            self._createBlendshapes(animation)
            self._createSolverAnimation(animation)
