import os
import shiboken2
from maya import cmds, OpenMayaUI
from PySide2 import QtWidgets, QtCore
from functools import wraps


class Wait(object):
    """
    This context change the cursor to be a waiting cursor for the duration
    of the function ran inside. Ideal to indicate to the user information is
    being processed.

    .. highlight::
        with Wait():
            # code
    """
    def __enter__(self):
        cmds.waitCursor(state=True)

    def __exit__(self, *exc_info):
        cmds.waitCursor(state=False)


def update(func):
    """
    The update decorator will force the QApplication to process its event.
    When having to be in the main thread to get information from the Maya
    scene QThreads cannot be used.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # call function
        ret = func(*args, **kwargs)
        processEvents()
        return ret
    return wrapper


def mayaWindow():
    """
    Get Maya's main window.

    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken2.wrapInstance(long(window), QtWidgets.QMainWindow)

    return window


def getIconPath(name):
    """
    Get an icon path based on file name. All paths in the XBMLANGPATH variable
    processed to see if the provided icon can be found.

    :param str name:
    :return: Icon path
    :rtype: str/None
    """
    for path in os.environ.get("XBMLANGPATH").split(os.pathsep):
        iconPath = os.path.join(path, name)
        if os.path.exists(iconPath):
            return iconPath.replace("\\", "/")


def processEvents():
    app = QtWidgets.QApplication.instance()
    app.processEvents()
