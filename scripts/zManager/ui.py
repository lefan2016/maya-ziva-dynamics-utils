from PySide2 import QtWidgets, QtCore, QtGui
from . import items, icons, widgets
from zUtils.ui import mayaWindow


class Manager(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Manager, self).__init__(parent)

        # set as window
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Manager")
        self.setWindowIcon(QtGui.QIcon(icons.ZIVA_ICON))
        self.resize(350, 500)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create selector
        self.solver = widgets.SolverSelector(self)
        layout.addWidget(self.solver)

        # create search
        self.search = widgets.SearchField(self)
        self.search.searchChanged.connect(self.filter)
        layout.addWidget(self.search)

        # create scroll
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setRootIsDecorated(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tree.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tree.header().setVisible(False)
        layout.addWidget(self.tree)

        # update with current solver
        self.update(self.solver.solver)

    # ------------------------------------------------------------------------

    def getSearchableItems(self):
        """
        :return: MeshItem's in the tree
        :rtype: generator
        """
        iter = QtWidgets.QTreeWidgetItemIterator(self.tree)
        while iter.value():
            widget = iter.value()
            if isinstance(widget, items.MeshItem):
                yield widget

            iter += 1

    # ------------------------------------------------------------------------

    def reset(self):
        """
        Unhide all of the searchable items and their parents.
        """
        for item in self.getSearchableItems():
            item.setHidden(False)

            for parent in item.allParents():
                parent.setHidden(False)

    def filter(self, search):
        """
        Hide and expand the tree widget based on the search string.

        :param str search:
        """
        # change search to lower case
        search = search.lower()

        # validate search
        if len(search) < 2:
            self.reset()
            return

        # match widgets with search string
        matches = []
        items = self.getSearchableItems()
        for item in items:
            state = False if item.search.count(search) else True
            item.setHidden(state)

            for parent in item.allParents():
                if state and str(parent) in matches:
                    continue

                if not state:
                    matches.append(str(parent))
                    parent.setExpanded(True)

                parent.setHidden(state)

    # ------------------------------------------------------------------------

    def update(self, solver):
        """
        Update the ui with the provided solver.

        :param str solver:
        """
        # clear layout
        self.tree.clear()

        # validate solver
        if not solver:
            return

        # add items
        items.BonesItem(self.tree, solver)
        items.TissuesItem(self.tree, solver)

        # do search
        self.filter(self.search.text)


def show():
    parent = mayaWindow()
    widget = Manager(parent)
    widget.show()
