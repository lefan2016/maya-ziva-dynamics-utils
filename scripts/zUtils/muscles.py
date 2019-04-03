from maya import cmds
from . import path, attributes
from .animation import Animation


# ----------------------------------------------------------------------------


ZIVA_MUSCLE_RIG = "__ziva_muscle_rig"
ZIVA_SOLVER = "__ziva_solver"


# ----------------------------------------------------------------------------


class MuscleRig(object):
    def __init__(self, root, character=None, solver=None):
        # define variables
        self._root = root

        # validate character
        if not character and not self.character:
            raise RuntimeError("Declare the 'character' variable!")

        # validate solver
        if not solver and not self.solver:
            raise RuntimeError("Declare the 'solver' variable!")

        # set character if declared
        if character:
            attributes.createTag(self.root, ZIVA_MUSCLE_RIG, character)

        # set solver if declared
        if solver:
            attributes.createLink(self.root, solver, ZIVA_SOLVER)

    # ------------------------------------------------------------------------

    @classmethod
    def getMuscleRigsFromScene(cls):
        """
        Loop over all transforms and that contain an import animation tag.
        Read the value of this tag and add it into a dictionary.

        :return: Exported animation from current scene
        :rtype: dict
        """
        # data variable
        data = {}

        # loop transforms
        for node in cmds.ls(transforms=True):
            # get plug
            plug = attributes.getPlug(node, ZIVA_MUSCLE_RIG)

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
        return attributes.getTag(self.root, ZIVA_MUSCLE_RIG)

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

    def applyAnimation(self, animation):
        """
        :param AnimationExport animation:
        """
        # remove existing animation
        self.removeAnimation()

        # get meshes
        sourceMeshes = self._getMeshTransforms(animation.root)
        targetMeshes = self._getMeshTransforms(self.root)

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
