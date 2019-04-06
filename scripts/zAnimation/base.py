from maya import cmds
from zUtils import api, transforms, attributes, decorators

from .tags import (
    ZIVA_ANIMATION,
    ZIVA_ANIMATION_START,
    ZIVA_ANIMATION_END,
    ZIVA_ANIMATION_TRANSITION,
    ZIVA_SOLVER_PARENT
)


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
