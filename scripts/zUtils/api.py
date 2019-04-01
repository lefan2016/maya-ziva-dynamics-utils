from maya import OpenMaya


def vectorToList(vector):
    """
    :param MVector vector:
    :return: Vector values as list
    :rtype: list
    """
    return [vector.x, vector.y, vector.z]


def listToVector(l):
    """
    :param list l:
    :return: List values as vector
    :rtype: MVector
    """
    return OpenMaya.MVector(*l)

# ----------------------------------------------------------------------------


def channelsToMatrix(x=None, y=None, z=None, t=None):
    """
    :param list/MVector/None x: X-vector
    :param list/MVector/None y: Y-vector
    :param list/MVector/None z: Z-vector
    :param list/MPoint/None t: Translation
    :return: Matrix
    :rtype: MMatrix
    """
    # define lists if not provided
    if not x:
        x = [1, 0, 0]
    if not y:
        y = [0, 1, 0]
    if not z:
        z = [0, 0, 1]
    if not t:
        t = [0, 0, 0]

    # convert maya type to list
    if type(x) != list:
        x = vectorToList(x)
    if type(y) != list:
        y = vectorToList(y)
    if type(z) != list:
        z = vectorToList(z)

    # construct matrix
    l = x + [0] + y + [0] + z + [0] + t + [1]
    return listToMatrix(l)


def listToMatrix(l):
    """
    :param list l:
    :return: Matrix
    :rtype: MMatrix
    """
    matrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil().createMatrixFromList(l, matrix)

    return matrix


def matrixToList(matrix):
    """
    :param MMatrix matrix:
    :return: Matrix as list
    :rtype: list
    """
    return [
        matrix(i, j)
        for i in range(4)
        for j in range(4)
    ]