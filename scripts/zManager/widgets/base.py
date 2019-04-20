from PySide2 import QtWidgets


class Label(QtWidgets.QLabel):
    def __init__(self, parent, text):
        super(Label, self).__init__(parent)
        self.setText(text)


class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, parent, text):
        super(CheckBox, self).__init__(parent)
        self.setText(text)


class Button(QtWidgets.QPushButton):
    def __init__(self, parent, text):
        super(Button, self).__init__(parent)
        self.setText(text)
        self.setFlat(True)
        self.setFixedHeight(19)
        self.setStyleSheet("text-align: left")
