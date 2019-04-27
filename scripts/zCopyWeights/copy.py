from maya import cmds


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
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    # ------------------------------------------------------------------------

    def weightsToList(self, weights):
        """
        :param list/tuple weights:
        :return: Weights
        :rtype: list
        """
        return weights[0] if type(weights[0]) == tuple else weights

    def extendWeightsWithDefaultValues(self, weights, reverse):
        """
        :param list/tuple weights:
        :param bool reverse:
        :return: Extended weights
        :rtype: list
        """
        # get mesh data
        mesh = cmds.zQuery(self.source, mesh=True)[0]
        vertices = cmds.polyEvaluate(mesh, vertex=True)

        # if the weight list is already as long as the amount of vertices
        # there is no to extend the list
        if len(weights) == vertices:
            return weights

        # create default weights list
        defaultWeights = [1 if not reverse else 0] * vertices

        # get set indices
        plugs = cmds.listAttr(self.source, multi=True)
        indices = [int(plug.split("[")[-1][:-1]) for plug in plugs]

        # update default weights with weights list
        for i, weight in zip(indices, weights):
            defaultWeights[i] = weight

        return defaultWeights

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

        # get source weights
        sourceWeights = self.weightsToList(cmds.getAttr(self.source))
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
        weights = self.weightsToList(cmds.getAttr(self.source))

        # reverse weights
        if reverse:
            weights = [1-weight for weight in weights]

        # set weights based on weight type
        if cmds.getAttr(self.target, type=True) == "doubleArray":
            # set weights
            cmds.setAttr(self.target, weights, type="doubleArray")
        elif cmds.getAttr(self.target, type=True) == "TdataCompound":
            # set weights
            weights = self.extendWeightsWithDefaultValues(weights, reverse)
            for i, weight in enumerate(weights):
                cmds.setAttr("{}[{}]".format(self.target, i), weight)
        else:
            raise ValueError("Weights cannot be set")
