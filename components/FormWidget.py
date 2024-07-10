from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QTimer
from reader.sireader2 import SIReaderReadout
from PySide6.QtWidgets import * 
from PySide6.QtGui import * 
from components import PointsBox, QRcode_maker
from trackChecking import *
import requests


BASE_URL="http://127.0.0.1:5000"

class FormWidget(QtWidgets.QWidget):

    #signal emitted when reader detects chip
    deviceDetected = Signal(list)
    sirConnected = False
    formShowed = False
    resultTime = 0
    trackSucc = False
    track = ''

    def __init__(self):
        super().__init__()

        
        #elements
        self.nameLabel = QtWidgets.QLabel(alignment=Qt.AlignCenter)
        self.timeLabel = QtWidgets.QLabel("", alignment = Qt.AlignCenter)
        self.sayResultLabel = QtWidgets.QLabel("", alignment = Qt.AlignCenter)

        self.nameInput = QtWidgets.QLineEdit()
        self.nameInput.setPlaceholderText("zde zadej jméno...")
        self.nameInput.setFixedSize(900, 50)
        self.nameInput.setFont(QFont("Arial", 20))

        self.sendButton =  QtWidgets.QPushButton("Odeslat")
        self.sendButton.setFixedSize(200, 50)
        self.sendButton.setFont(QFont("Arial", 20))

        self.pBox = PointsBox.PointsBox()

        #layout
        self.grid = QtWidgets.QGridLayout(self)

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
        #self.setLayout(self.grid)
        self.grid.addWidget(self.pBox, 0, 0, -1, 2, Qt.AlignLeft)
        self.grid.addWidget(self.nameLabel, 1, 2, Qt.AlignLeft)
        self.grid.addWidget(self.sayResultLabel, 1, 2, Qt.AlignCenter)
        self.grid.addWidget(self.timeLabel, 2, 2, Qt.AlignCenter)
        self.grid.addLayout(self.SH1layout, 3, 2, Qt.AlignCenter)

        # self.layout.addWidget(self.pBox)
        # self.layout.addWidget(self.nameLabel)
        self.SH1layout.addWidget(self.nameInput)
        self.SH1layout.addWidget(self.sendButton)

        # self.SVlayout.addWidget(self.sayResultLabel)
        # self.SVlayout.addWidget(self.timeLabel)
        # self.SVlayout.addLayout(self.SH1layout)

        # self.layout.addLayout(self.SVlayout)

        
        self.timeLabel.hide()
        self.timeLabel.setFont(QFont("Arial", 40))
        self.sayResultLabel.hide()
        self.sayResultLabel.setFont(QFont("Arial", 40))
        self.nameInput.hide()
        self.sendButton.hide()
        
        self.nameLabel.setText("Čekám na čip...")
        self.nameLabel.setFont(QFont("Arial", 40))

        #some spider web connections 
        self.sendButton.clicked.connect(self.sendButtonHandle)
        # self.sendButton.clicked.connect(self.hideForm)
        # self.sendButton.clicked.connect(self.pBox.clean)
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
                    self.resultTime = (data["finish"]-data["start"]).total_seconds()*1000
                    self.showForm()
                    self.deviceDetected.emit(arr)
                    self.sir.ack_sicard()
                
            except Exception as e:
                print(e, "in checkDevice")
                self.sirConnected = False

    def formateTime(self, time_in_millisec):
        time_in_sec = time_in_millisec // 1000
        millis = time_in_millisec % 1000
        hours = time_in_sec // 3600
        minutes = (time_in_sec % 3600) // 60
        seconds = time_in_sec % 60

        formatted = ""
        if hours:
            formatted += f"{hours:02d}:"
        formatted += f"{minutes:02d}:{seconds:02d}.{millis:03d}"

        return formatted
    
    def showForm(self):
        self.sendButton.show()
        
        self.nameInput.show()
        self.nameInput.setFocus()

        time = "Čas: "+ str(self.formateTime(int(self.resultTime)))
        self.timeLabel.setText(time)
        self.timeLabel.show()
        
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
        self.nameInput.setText("")
        self.sendButton.hide()
        self.sayResultLabel.hide()
        self.timeLabel.hide()
        self.pBox.clean()
        self.resultTime = 0

        
    @QtCore.Slot()
    def showPoints(self, points):

        data = requests.get(BASE_URL+"/tracks_data")
        tracksData = data.json()

        routesArr=[]

        for track in tracksData:
            r = Route(track["name"])
            rPoints = []
            for point in track["points"]:
                rPoints.append(int(point["number"]))
            r.setRoute(rPoints)
            routesArr.append(r)    

        
        self.pBox.clean()

        completeRoutePresent = False
        maxPointsIndex = [0, 0] #count, index 


        for i, r in enumerate(routesArr):
                a = checkRoute(r, points)
                if a.succes:
                    completeRoutePresent = True
                    self.track = r.name
                    self.trackSucc = True
                    for p in a.points:
                        self.pBox.append(id = p.id, type = p.type, inSuc = completeRoutePresent)
                    self.showResultLabel(r.name, True)
                    break
                elif a.count > maxPointsIndex[1]:
                    maxPointsIndex[0] = a.count
                    maxPointsIndex[1] = i
        if(not completeRoutePresent):
            a = checkRoute(routesArr[maxPointsIndex[1]], points)
            for p in a.points:
                self.pBox.append(id = p.id, type = p.type, inSuc = completeRoutePresent)
                self.showResultLabel(routesArr[maxPointsIndex[1]].name, False)

    @QtCore.Slot()
    def sendButtonHandle(self):
        if(self.trackSucc == True):
            name = self.nameInput.text()

            msg = QMessageBox()
            

            resp = self.sendReq(self.resultTime, name, self.track, "12.7.")

            if(resp[0]):

                msg.setText(str("Pro zobrazení výsledků načtěte qrcode"))
                image = QRcode_maker.QRcode(resp[1])

                layout = msg.layout()
                layout.addWidget(image, 1, 1, alignment=Qt.AlignCenter)
            else:
                msg.setText(str("Nastala chyba, zkuste znovu"))


            msg.exec()

            self.trackSucc = False
            self.hideForm()
        else:
            msg = QMessageBox()
            msg.setText(str("Nezdolanou trať nelze nahrat!"))
            msg.exec()


    def sendReq(self, time, name, track, date):
        url = BASE_URL+"/external_rslts_upload"
        secret = "mamamia"
        data_to_send={
            "name": name, 
            "time": time, 
            "track": track,
            "date": date,
            "secret": secret
        }

        r = requests.post(url, json=data_to_send)
        print( r)
        data = r.json()

        return (True, data["id"])
