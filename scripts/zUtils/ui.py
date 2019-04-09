import os
import shiboken2
from maya import OpenMayaUI
from PySide2 import QtWidgets


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
