import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QTimer
from components import PointsBox, FormWidget

from trackChecking import *

class MyWidget(QtWidgets.QWidget):

    

    def __init__(self):
        super().__init__()



        self.horLayout = QtWidgets.QHBoxLayout(self)

        self.pBox = PointsBox.PointsBox()
        self.form = FormWidget.FormWidget()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.form.connectDevice)
        self.timer.start(2000)

        self.form.deviceDetected.connect(self.showPoints)

        self.horLayout.addWidget(self.pBox)
        self.horLayout.addWidget(self.form)

        


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = FormWidget.FormWidget()
    widget.showMaximized()

    sys.exit(app.exec())