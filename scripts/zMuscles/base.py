from maya import cmds
from zUtils import attributes
from .tags import ZIVA_MUSCLES


class Muscles(object):
    def __init__(self, root, character=None):
        # define variables
        self._root = root

        # validate character
        if not character and not self.character:
            raise RuntimeError("Declare the 'character' variable!")

        # set character if declared
        if character:
            attributes.createTag(self.root, ZIVA_MUSCLES, character)

    # ------------------------------------------------------------------------

    @classmethod
    def getMuscleSystemsFromScene(cls):
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
            plug = attributes.getPlug(node, ZIVA_MUSCLES)

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
        return attributes.getTag(self.root, ZIVA_MUSCLES)

    @property
    def root(self):
        """
        The root node is the node that indicates the root of the animation
        node. Either in import or export mode.

        :return: Root node
        :rtype: str
        """
        return self._root
