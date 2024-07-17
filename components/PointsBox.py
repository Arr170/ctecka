from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import * 
from PySide6.QtGui import * 

class PointsBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.setFixedWidth(200)
        self.groupbox = QtWidgets.QGroupBox()
       # self.groupbox.setAlignment(Qt.AlignCenter)
        self.innerLayout = QtWidgets.QVBoxLayout()

        
        self.groupbox.setLayout(self.innerLayout)


        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.groupbox)
        scroll.setWidgetResizable(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll)

    def append(self, type=1, id=1, inSuc=True):
        point = Point(type, id, inSuc)
        self.innerLayout.addWidget(point)

    def setTrackName(self, trackName):
        trackName = "trať "+ trackName
        self.groupbox.setTitle(trackName)
    
    @QtCore.Slot()
    def clean(self):
        for i in reversed(range(self.innerLayout.count())): 
            self.innerLayout.itemAt(i).widget().deleteLater()

class Point(QtWidgets.QWidget):
    def __init__(self, pointType=None, pointId = None, inSuc = False):
        super().__init__()
        
        self.setFixedSize(150, 75)
        if pointType == "suc":
            self.setStyleSheet("background-color: green; border-radius: 20px; color: black")
            self.setToolTip("správně")
        elif pointType == "sign":
            self.setStyleSheet("background-color: grey; border-radius: 20px; color: black")
        elif inSuc:

            self.setStyleSheet("background-color: yellow; border-radius: 20px; color: black")
            self.setToolTip("navíc")
        else:
            self.setStyleSheet("background-color: red; border-radius: 20px; color: black")
            self.setToolTip("chyba")


        #self.setStyleSheet("background-color: red")

        trackId = QtWidgets.QLabel(str(pointId), alignment = Qt.AlignCenter)
        trackId.setFont(QFont("Arial", 20))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(trackId)

    