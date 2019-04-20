from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds
from .. import icons


class SolverSelector(QtWidgets.QWidget):
    solverChanged = QtCore.Signal(str)

    def __init__(self, parent):
        super(SolverSelector, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # get solvers
        solvers = cmds.ls(type="zSolver") or []

        # add combo box
        self.combo = QtWidgets.QComboBox(self)
        self.combo.addItems(solvers)
        self.combo.currentIndexChanged[str].connect(self.solverChanged.emit)
        layout.addWidget(self.combo)

        # add select button
        select = QtWidgets.QPushButton(self)
        select.setFlat(True)
        select.setIcon(QtGui.QIcon(icons.SELECT_ICON))
        select.setFixedSize(QtCore.QSize(19, 19))
        select.released.connect(self.doSelect)
        select.setEnabled(len(solvers) > 0)
        layout.addWidget(select)

    # ------------------------------------------------------------------------

    @property
    def solver(self):
        """
        :return: Active solver
        :rtype: str/None
        """
        return self.combo.currentText() or None

    # ------------------------------------------------------------------------

    def doSelect(self):
        if cmds.objExists(self.solver):
            cmds.select(self.solver)
