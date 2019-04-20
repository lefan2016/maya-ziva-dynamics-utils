from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds, mel
from .. import icons


class SearchField(QtWidgets.QWidget):
    searchChanged = QtCore.Signal(str)

    def __init__(self, parent):
        super(SearchField, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # add line edit
        self.le = QtWidgets.QLineEdit(self)
        self.le.setPlaceholderText("search...")
        self.le.textChanged.connect(self.searchChanged.emit)
        layout.addWidget(self.le)

        # add clear button
        clear = QtWidgets.QPushButton(self)
        clear.setFlat(True)
        clear.setIcon(QtGui.QIcon(icons.CLOSE_ICON))
        clear.setFixedSize(QtCore.QSize(19, 19))
        clear.released.connect(self.doClear)
        layout.addWidget(clear)

        # add select button
        select = QtWidgets.QPushButton(self)
        select.setFlat(True)
        select.setIcon(QtGui.QIcon(icons.SELECT_ICON))
        select.setFixedSize(QtCore.QSize(19, 19))
        select.released.connect(self.fromSelection)
        layout.addWidget(select)

    # ------------------------------------------------------------------------

    @property
    def text(self):
        """
        :return: Search text
        :rtype: str
        """
        return self.le.text()

    # ------------------------------------------------------------------------

    def doClear(self):
        """
        Clear the search line edit of any text, which will still trigger the
        searchChanged signal to be triggered.
        """
        self.le.setText("")

    def fromSelection(self):
        """
        Set the search field string to the name of the first node selected.
        If nothing is selected a RuntimeError is raised.
        """
        # get selection
        sel = cmds.ls(sl=True)

        # validate selection
        if not sel:
            raise RuntimeError("Selection is clear!")

        # set selection
        self.le.setText(sel[0])
