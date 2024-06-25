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



    

    @QtCore.Slot()
    def showPoints(self, points):
        track_a = [38, 35, 31, 34, 39, 32, 33, 36, 37]
        track_b = [35, 31, 38, 39, 32, 33, 36, 34, 37]
        track_c = [34, 32, 36, 38, 35, 31, 37, 35, 33, 39]

        Ra = Route("A")
        Ra.setRoute(track_a)

        Rb = Route("B")
        Rb.setRoute(track_b)

        Rc = Route("C")
        Rc.setRoute(track_c)

        routeArr = [Ra, Rb, Rc]

        for r in routeArr:
                a = checkRoute(r, points)
                if a.succes:
                    for p in a.points:
                        self.pBox.append(id = p.id, type = p.type)

        


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = FormWidget.FormWidget()
    widget.showMaximized()

    sys.exit(app.exec())