from maya import cmds
from functools import wraps


def loadPlugin(pluginToLoad):
    def wrapper(func):
        """
        Make sure the provided plugin is loaded before the function is called.
        """
        @wraps(func)
        def inner(*args, **kwargs):
            if not cmds.pluginInfo(pluginToLoad, query=True, loaded=True):
                cmds.loadPlugin(pluginToLoad)

            ret = func(*args, **kwargs)
            return ret
        return inner
    return wrapper


def preserveSelection(func):
    """
    The preserve selection decorator will store the maya selection before the
    function is called. There are many functions to Maya's native cmds that
    alter the selection. After the function is called the original selection
    shall be made.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # store selection
        sel = cmds.ls(sl=True)

        # call function
        ret = func(*args, **kwargs)

        # redo selection
        if sel:
            cmds.select(sel)
        else:
            cmds.select(clear=True)

        return ret
    return wrapper