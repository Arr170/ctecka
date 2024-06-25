from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QTimer
from reader.sireader2 import SIReaderReadout
from components import PointsBox
from trackChecking import *



class FormWidget(QtWidgets.QWidget):

    #signal emitted when reader detects chip
    deviceDetected = Signal(list)
    sirConnected = False
    formShowed = False
    resultTime = 0

    def __init__(self):
        super().__init__()

        
        #elements
        self.nameLabel = QtWidgets.QLabel("jméno:", alignment=Qt.AlignCenter)
        self.timeLabel = QtWidgets.QLabel("", alignment = Qt.AlignCenter)
        self.sayResultLabel = QtWidgets.QLabel("", alignment = Qt.AlignCenter)

        self.nameInput = QtWidgets.QLineEdit()
        self.nameInput.setPlaceholderText("zde zadej jméno...")

        self.sendButton =  QtWidgets.QPushButton("Odeslat")

        self.pBox = PointsBox.PointsBox()

        #layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.SVlayout = QtWidgets.QVBoxLayout()
        self.SH1layout = QtWidgets.QHBoxLayout()
        self.SH2layout = QtWidgets.QHBoxLayout()       
        #timer to check for available chip
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.connectDevice)
        self.timer.timeout.connect(self.checkDevice)
        self.timer.start(1000) 

        #add needed elements to layout
        self.layout.addWidget(self.pBox)
        self.layout.addWidget(self.nameLabel)
        self.SH1layout.addWidget(self.nameInput)
        self.SH1layout.addWidget(self.sendButton)

        self.SVlayout.addWidget(self.sayResultLabel)
        self.SVlayout.addLayout(self.SH1layout)

        self.layout.addLayout(self.SVlayout)

        

        self.nameInput.hide()
        self.sendButton.hide()
        
        self.nameLabel.setText("Čekám na čip...")

        #some spider web connections 
        self.sendButton.clicked.connect(self.hideForm)
        self.sendButton.clicked.connect(self.pBox.clean)
        self.deviceDetected.connect(self.showPoints)


    @QtCore.Slot()
    def connectDevice(self):
        if not self.sirConnected:
            try:
                self.sir = SIReaderReadout()
                self.sirConnected = True
                return True
            except Exception as e:
                print(e)
                return False
        
    def checkDevice(self):
        if self.sirConnected:
            try:
                if self.sir.poll_sicard():
                    data = self.sir.read_sicard()
                    arr=[]
                    for a in data["punches"]:
                        arr.append(a[0])
                    self.resultTime = (data["finish"]-data["start"]).total_seconds()
                    self.showForm()
                    self.deviceDetected.emit(arr)
                    self.sir.ack_sicard()
                
            except Exception as e:
                print(e, "in checkDevice")
                self.sirConnected = False
    
    def showForm(self):
        self.sendButton.show()
        
        self.nameInput.show()
        self.nameInput.setFocus()
        
        self.nameLabel.hide()
        
    def showResultLabel(self, routeName, succes):
        message = f"Trať {routeName} "
        succTrack = "zdolána úspěšně!"
        unsuccTrack = "nebyla zcela splněna, vlevo můžeš vidět, kde je chyba."
        if succes:
            message = message + succTrack
        else:
            message = message + unsuccTrack
        self.sayResultLabel.setText(message)
        self.sayResultLabel.show()


    @QtCore.Slot()
    def hideForm(self):
        print("removing...")
        self.nameLabel.show()
        self.nameInput.hide()
        self.sendButton.hide()
        self.sayResultLabel.hide()

        self.resultTime = 0

        
    @QtCore.Slot()
    def showPoints(self, points):

        completeRoutePresent = False

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
        maxPointsIndex = [0, 0] #count, index 


        for i, r in enumerate(routeArr):
                a = checkRoute(r, points)
                if a.succes:
                    completeRoutePresent = True
                    for p in a.points:
                        self.pBox.append(id = p.id, type = p.type)
                    self.showResultLabel(r.name, True)
                    break
                elif a.count > maxPointsIndex[1]:
                    maxPointsIndex[0] = a.count
                    maxPointsIndex[1] = i
        if(not completeRoutePresent):
            a = checkRoute(routeArr[maxPointsIndex[1]], points)
            for p in a.points:
                self.pBox.append(id = p.id, type = p.type)
                self.showResultLabel(routeArr[maxPointsIndex[1]].name, False)


