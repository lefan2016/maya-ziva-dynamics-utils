import os
import shiboken2
from maya import cmds, OpenMayaUI
from PySide2 import QtWidgets, QtCore


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


class BlockSignals(object):
    """
    This context will block the signals of the provided widgets.

    .. highlight::
        with BlockSignals(widgets):
            # code
    """
    def __init__(self, *widgets):
        self._widgets = widgets

    def __enter__(self):
        for widget in self.widgets:
            widget.blockSignals(True)

    def __exit__(self, *exc_info):
        for widget in self.widgets:
            widget.blockSignals(False)

    # ------------------------------------------------------------------------

    @property
    def widgets(self):
        """
        :return: Widgets
        :rtype: list
        """
        return self._widgets


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
