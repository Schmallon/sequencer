import sys
from PyQt4 import QtGui, QtCore
from matrix import *


class SigSlot(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('signal & slot')

        lcd = QtGui.QLCDNumber(self)
        slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(slider)

        self.setLayout(vbox)
        self.connect(slider,  QtCore.SIGNAL('valueChanged(int)'), lcd, 
		QtCore.SLOT('display(int)') )

        self.resize(250, 150)


app = QtGui.QApplication(sys.argv)
matrix = Matrix()
matrix.add_note(Note(Pitch.from_name("c", "", 0), 0, 1 / 4.0))
matrix.add_note(Note(Pitch.from_name("e", "", 0), 1 / 4.0, 1 / 4.0))
matrix.add_note(Note(Pitch.from_name("g", "", 0), 2 / 4.0, 2 / 4.0))
matrix.add_note(Note(Pitch.from_name("c", "", 0), 5 / 4.0, 1 / 4.0))

matrixEditor = MatrixEditor(matrix)
matrixEditor.show()
sys.exit(app.exec_())

