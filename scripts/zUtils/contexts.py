from maya import cmds
from . import attributes


class DisableZivaSolvers(object):
    """
    This context temporarily disables the ziva solvers so it won't trigger any
    calculation when the function is executed.

    .. highlight::
        with DisableZivaSolvers():
            # code
    """
    def __init__(self):
        # store solver data
        self._solvers = {}

        # loop solvers
        for solver in cmds.ls(type="zSolver"):
            transform = cmds.listRelatives(solver, parent=True)[0]
            plug = attributes.getPlug(transform, "enable")
            self._solvers[plug] = cmds.getAttr(plug)

    # ------------------------------------------------------------------------

    def __enter__(self):
        for plug in self._solvers.keys():
            cmds.setAttr(plug, 0)

    def __exit__(self, *exc_info):
        for plug, value in self._solvers.iteritems():
            cmds.setAttr(plug, value)


class DisableAutoKeyframe(object):
    """
    This context temporarily disables the auto keyframe command. If auto
    keyframe is turned off before going into this context no changes will be
    made.

    .. highlight::
        with DisableAutoKeyframe:
            # code
    """
    def __init__(self):
        self._state = cmds.autoKeyframe(query=True, state=True)

    # ------------------------------------------------------------------------

    def __enter__(self):
        if self._state:
            cmds.autoKeyframe(state=0)

    def __exit__(self, *exc_info):
        if self._state:
            cmds.autoKeyframe(state=1)
