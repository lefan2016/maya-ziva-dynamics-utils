from PySide2 import QtWidgets
from .. import widgets


class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent):
        super(TreeItem, self).__init__(parent)

        # variable
        self._widget = None

    # ------------------------------------------------------------------------

    @property
    def widget(self):
        """
        :return: Widget
        :rtype: QWidget
        """
        return self._widget

    # ------------------------------------------------------------------------

    def allParents(self):
        """
        :return: All parents
        :rtype: list
        """
        parents = []
        parent = self.parent()
        while parent:
            parents.append(parent)
            parent = parent.parent()

        return parents

    # ------------------------------------------------------------------------

    def addWidget(self, widget):
        """
        :param QWidget widget:
        """
        self._widget = widget
        self.treeWidget().setItemWidget(self, 0, widget)


class LabelItem(TreeItem):
    def __init__(self, parent, text):
        super(LabelItem, self).__init__(parent)

        widget = widgets.Label(self.treeWidget(), text)
        self.addWidget(widget)


class CheckBoxItem(TreeItem):
    def __init__(self, parent, text):
        super(CheckBoxItem, self).__init__(parent)

        widget = widgets.CheckBox(self.treeWidget(), text)
        self.addWidget(widget)
