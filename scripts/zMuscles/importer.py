from maya import cmds
from zUtils import path, transforms, attributes
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
        # get meshes
        meshes = cmds.listRelatives(
            self.root,
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

        # remove animation curves from solver
        for attr in ZIVA_SOLVER_ATTRIBUTES:
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

    def applyAnimation(self, animation):
        """
        :param AnimationExport animation:
        """
        # remove existing animation
        self.removeAnimation()

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

        # animate solver
        plugs = [
            attributes.getPlug(self.solver, attr)
            for attr in ZIVA_SOLVER_ATTRIBUTES
        ]

        for frame in [animation.startFrame, animation.startFrame+1]:
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
