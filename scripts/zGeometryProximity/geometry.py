from maya import cmds
from zUtils import intersect


def selectGeometryByProximity(r=0.25):
    """
    Select geometry by proximity of the currently selected geometry.
    Using on a distance attribute.

    :param int/float r:
    :raise RuntimeError: If no geometry is selected
    """
    # get selection
    selection = cmds.ls(selection=True) or []

    # validate selection
    if not selection:
        raise RuntimeError("Select geometry!")

    # select geometry
    cmds.select(findGeometryByProximity(selection[0], r))


def findGeometryByProximity(geo, r=0.25):
    """
    Find geometry by proximity of provided geometry using a distance
    attribute. The solver that is attached the the provided geometry
    is found, from that solver all other geometry attached the the solver
    are checked if they are within proximity of the provided geometry.

    To speed up the checks first a check based on bounding box is done
    before using the zFindVerticesByProximity function to get the proximity
    on a vertex level.

    :param int/float r:
    :raise RuntimeError: If no solver is attached to the geometry
    """
    # variable
    geometryInProximity = [geo]

    # get solver of first selected object
    solver = cmds.zQuery(geo, type="zSolver") or []

    # validate solver
    if not solver:
        raise RuntimeError(
            "Select geometry that is attached to a Ziva solver!"
        )

    # get attached meshes
    meshes = cmds.zQuery(solver, mesh=True)
    meshes.remove(geo)

    # loop meshes
    for mesh in meshes:
        # get overlapping bounding boxes
        if not intersect.intersectBoundingBox(geo, mesh, r):
            continue

        # get vertices by proximity
        if not cmds.zFindVerticesByProximity(geo, mesh, r=r):
            continue

        # add mesh to proximity meshes
        geometryInProximity.append(mesh)

    return geometryInProximity
