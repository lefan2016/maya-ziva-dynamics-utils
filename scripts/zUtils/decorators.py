from maya import cmds
from functools import wraps


ALEMBIC_IMPORT_PLUGIN = "AbcImport.mll"
ALEMBIC_EXPORT_PLUGIN = "AbcExport.mll"


def loadAlembicImportPlugin(func):
    """
    Make sure the alembic import is loaded before the function is called.
    This decorator can be used on functions that need to import alembic files.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if not cmds.pluginInfo(ALEMBIC_IMPORT_PLUGIN, query=True, loaded=True):
            cmds.loadPlugin(ALEMBIC_IMPORT_PLUGIN)

        ret = func(*args, **kwargs)
        return ret
    return inner


def loadAlembicExportPlugin(func):
    """
    Make sure the alembic export is loaded before the function is called.
    This decorator can be used on functions that need to export alembic files.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if not cmds.pluginInfo(ALEMBIC_EXPORT_PLUGIN, query=True, loaded=True):
            cmds.loadPlugin(ALEMBIC_EXPORT_PLUGIN)

        ret = func(*args, **kwargs)
        return ret
    return inner


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