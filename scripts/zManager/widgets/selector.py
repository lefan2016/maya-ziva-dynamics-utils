from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds
from .. import icons
from zUtils import ui


class SolverSelector(QtWidgets.QWidget):
    solverChanged = QtCore.Signal(str)

    def __init__(self, parent):
        super(SolverSelector, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # add combo box
        self.combo = QtWidgets.QComboBox(self)
        self.combo.currentIndexChanged[str].connect(self.solverChanged.emit)
        layout.addWidget(self.combo)

        # add refresh
        refresh = QtWidgets.QPushButton(self)
        refresh.setFlat(True)
        refresh.setIcon(QtGui.QIcon(icons.REFRESH_ICON))
        refresh.setFixedSize(QtCore.QSize(19, 19))
        refresh.released.connect(self.update)
        layout.addWidget(refresh)

        # add select button
        self.select = QtWidgets.QPushButton(self)
        self.select.setFlat(True)
        self.select.setIcon(QtGui.QIcon(icons.SELECT_ICON))
        self.select.setFixedSize(QtCore.QSize(19, 19))
        self.select.released.connect(self.doSelect)
        layout.addWidget(self.select)

        # run update
        self.update()

    # ------------------------------------------------------------------------

    @property
    def solver(self):
        """
        :return: Active solver
        :rtype: str/None
        """
        return self.combo.currentText() or None

    # ------------------------------------------------------------------------

    def update(self):
        # current
        solver = self.solver

        # block signals
        with ui.BlockSignals(self.combo):
            # get solvers
            solvers = cmds.ls(type="zSolver") or []
            self.combo.clear()
            self.combo.addItems(solvers)
            self.select.setEnabled(len(solvers) > 0)

            # set old solver
            if solver in solvers:
                index = solvers.index(solver)
                self.combo.setCurrentIndex(index)

            solver = solver if solver and solvers else solvers[0]

        # emit signal
        self.solverChanged.emit(solver)

    # ------------------------------------------------------------------------

    def doSelect(self):
        if cmds.objExists(self.solver):
            cmds.select(self.solver)
