from maya import cmds
from zUtils import attributes


class CopyWeights(object):
    def __init__(self, source=None, target=None):
        self._source = source
        self._target = target

    # ------------------------------------------------------------------------

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def sourcePlug(self):
        return attributes.getPlug(self.source, "weightList[0].weights")

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def targetPlug(self):
        return attributes.getPlug(self.target, "weightList[0].weights")

    # ------------------------------------------------------------------------

    def validate(self):
        """
        Check the source and target, their plugs and the weights to see if
        they are compatible with each other. If they are the state will be
        returned as true, if not the state is false and and error message
        will be added.

        :return: Validation state
        :rtype: tuple
        """
        # validate input
        if not self.source:
            return False, "Source doesn't exist!"
        elif not self.target:
            return False, "Target doesn't exist!"

        # validate plugs
        if not cmds.objExists(self.sourcePlug):
            return False, "Source doesn't have a weights plug!"
        elif not cmds.objExists(self.targetPlug):
            return False, "Target doesn't have a weights plug!"

        # validate source weight
        sourceWeights = cmds.getAttr(self.sourcePlug)[0]
        if not len(sourceWeights):
            return False, "Source contains no painted weights!"

        # validate vertex count
        sourceMesh = cmds.zQuery(self.source, mesh=True)[0]
        targetMesh = cmds.zQuery(self.target, mesh=True)[0]

        sourceCount = cmds.polyEvaluate(sourceMesh, vertex=True)
        targetCount = cmds.polyEvaluate(targetMesh, vertex=True)

        if sourceCount != targetCount:
            return False, "Source and Target vertex count are not the same!"

        return True, ""

    # ------------------------------------------------------------------------

    def copy(self, reverse=False):
        # validate source and target
        state, message = self.validate()
        if not state:
            raise ValueError(message)

        # get weights
        weights = cmds.getAttr(self.sourcePlug)[0]

        # reverse weights
        if reverse:
            weights = [1-weight for weight in weights]

        # set weights
        for i, weight in enumerate(weights):
            cmds.setAttr("{}[{}]".format(self.targetPlug, i), weight)
