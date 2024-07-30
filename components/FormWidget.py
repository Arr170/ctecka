from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QTimer
from reader.sireader2 import SIReaderReadout
from PySide6.QtWidgets import * 
from PySide6.QtGui import * 
from components import PointsBox, QRcode_maker
from trackChecking import *
import requests
import os
from datetime import date



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
        self.signLabel = QLabel("Čekám na čip...", alignment = Qt.AlignCenter)
        self.timeLabel = QLabel(alignment = Qt.AlignCenter)
        self.sayResultLabel = QLabel(alignment = Qt.AlignCenter)
        self.sayResultLabelBot = QLabel("Vlevo můžeš vědět, kde je chyba.", alignment = Qt.AlignCenter)
        self.linkLabel = QLabel("Odkaz na stránku s výsledky:")
        self.warningLabel = QLabel("Odesláním souhlasíte se zveřejněním vašeho času a vámi zadané přezdívky na online výsledkové listině.")

        self.nameInput = QtWidgets.QLineEdit()
        self.nameInput.setMaxLength(40)
        self.nameInput.setPlaceholderText("Zde zadej přezdívku...")
        self.nameInput.setFixedHeight(50)
        self.nameInput.setFont(QFont("Arial", 20))

        self.sendButton =  QtWidgets.QPushButton(" Odeslat ")
        self.sendButton.setFixedHeight(50)
        self.sendButton.setFont(QFont("Arial", 20))

        self.cancelButton = QPushButton(" Zrušit ")
        self.cancelButton.hide()

        ### testing only ###
        # self.testButton = QPushButton("TEST")
        # self.testButton.clicked.connect(self.showForm)


        self.pBox = PointsBox.PointsBox()

        self.linkImage = QLabel()
        self.qrImage = QPixmap(QRcode_maker.create_qrcode()) 
        self.linkImage.setPixmap(self.qrImage)

        #layout
        self.grid = QtWidgets.QGridLayout(self)

        self.SH1layout = QtWidgets.QHBoxLayout()
        #timer to check for available chip
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.connectDevice)
        self.timer.timeout.connect(self.checkDevice)
        self.timer.start(1000) 

        #add needed elements to layout
    
        self.grid.addWidget(self.pBox, 0, 0, -1, 1, Qt.AlignLeft)
        self.grid.addWidget(self.signLabel, 0, 1, Qt.AlignCenter)
        # self.grid.addWidget(self.testButton, 0, 2, Qt.AlignLeft)
        self.grid.addWidget(self.cancelButton, 0, 2, Qt.AlignLeft)
        self.grid.addWidget(self.sayResultLabel, 1, 2, Qt.AlignCenter)
        self.grid.addWidget(self.linkLabel, 1, 1, Qt.AlignLeft)
        self.grid.addWidget(self.linkImage, 1, 2, Qt.AlignLeft)
        self.grid.addWidget(self.sayResultLabelBot, 2, 2, Qt.AlignCenter)
        self.grid.addWidget(self.timeLabel, 3, 2, Qt.AlignCenter)
        self.grid.addLayout(self.SH1layout, 4, 2, Qt.AlignBottom)
        self.grid.addWidget(self.warningLabel, 5, 2, Qt.AlignTop)

       
        self.SH1layout.addWidget(self.nameInput)
        self.SH1layout.addWidget(self.sendButton)

        # self.SVlayout.addWidget(self.sayResultLabel)
        # self.SVlayout.addWidget(self.timeLabel)
        # self.SVlayout.addLayout(self.SH1layout)

        # self.layout.addLayout(self.SVlayout)

        
        self.timeLabel.hide()
        self.timeLabel.setFont(QFont("Arial", 40))
        self.linkLabel.setFont(QFont("Arial", 30))
        self.sayResultLabel.hide()
        self.sayResultLabel.setFont(QFont("Arial", 40))
        self.sayResultLabelBot.hide()
        self.sayResultLabelBot.setFont(QFont("Arial", 40))
        self.nameInput.hide()
        self.sendButton.hide()
        self.warningLabel.hide()
        
        self.signLabel.setFont(QFont("Arial", 40))

        #some spider web connections 
        self.sendButton.clicked.connect(self.sendButtonHandle)
        self.nameInput.returnPressed.connect(self.sendButtonHandle)
        self.cancelButton.clicked.connect(self.hideForm)
        self.deviceDetected.connect(self.showPoints)



    @QtCore.Slot()
    def connectDevice(self):
        if not self.sirConnected:
            try:
                self.sir = None
                self.sirConnected = False
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
                    print(type(data["finish"]-data["start"]))
                    self.resultTime = (data["finish"]-data["start"]).total_seconds()*100

                    self.showForm()
                    self.deviceDetected.emit(arr)
                    self.sir.ack_sicard()
                    
                
            except Exception as e:
                print(e, "in checkDevice")
                self.sirConnected = False
                msg = QMessageBox()
                msg.setWindowTitle(str("Chyba!"))
                msg.setStyleSheet("background-color: rgb(255, 160, 160);")
                match str(e):
                    case "No card in the device.":
                        return
                    case "SI-Card removed during command.":
                        return
                    case "unsupported operand type(s) for +=: 'NoneType' and 'datetime.timedelta'":
                        msg.setText("Nebyl oražen 'Start' nebo 'Finish'")
                    case _:
                        msg.setText(str(e))
                msg.exec()



    def formateTime(self, time_in_tens_of_millisec):
        time_in_sec = time_in_tens_of_millisec // 100
        millis = time_in_tens_of_millisec % 100
        hours = time_in_sec // 3600
        minutes = (time_in_sec % 3600) // 60
        seconds = time_in_sec % 60

        formatted = ""
        if hours:
            formatted += f"{hours:02d}:"
        formatted += f"{minutes:02d}:{seconds:02d}.{millis:02d}"

        return formatted
    

    def showResultLabel(self, routeName, succes):
        message = f"{routeName} "
        unsuccTrack = "nebyla zcela splněna."
        if succes:
            self.nameInput.setReadOnly(False)
            self.sendButton.setEnabled(True)
            message = f"{routeName} zdolána úspěšně!"
        else:
            self.nameInput.setReadOnly(True)
            self.sendButton.setEnabled(False)
            message = f"Nesplněnou trať nejde dokončit ({routeName})"
            self.sayResultLabelBot.show()
        self.sayResultLabel.setText(message)
        self.sayResultLabel.show()
    
    @QtCore.Slot()
    def showForm(self):
        self.sayResultLabelBot.hide()
        self.linkImage.hide()
        self.linkLabel.hide()
        self.signLabel.hide()

        self.cancelButton.show()
        self.sendButton.show()
        self.warningLabel.show()
        self.nameInput.show()
        self.nameInput.setFocus()

        time = "Čas: "+ str(self.formateTime(int(self.resultTime)))
        self.timeLabel.setText(time)
        self.timeLabel.show()
        


    @QtCore.Slot()
    def hideForm(self):
        self.signLabel.show()
        self.linkImage.show()
        self.linkLabel.show()

        self.cancelButton.hide()
        self.warningLabel.hide()
        self.nameInput.hide()
        self.nameInput.setText("")
        self.sendButton.hide()
        self.sayResultLabel.hide()
        self.sayResultLabelBot.hide()
        self.timeLabel.hide()
        self.pBox.clean()
        self.resultTime = 0

        
    @QtCore.Slot()
    def showPoints(self, points):

        try:
            data = requests.get("https://festival.obteplice.cz" + "/tracks_data")
            tracksData = data.json()
        except Exception as e: 
            msg = QMessageBox()
            err = "Chyba spojení, "+ str(e)
            msg.setWindowTitle(str("Chyba!"))
            msg.setText(str(err))
            msg.exec()
            return

        routesArr=[]

        for track in tracksData:
            r = Route(track["name"])
            rPoints = []
            for point in track["points"]:
                rPoints.append(int(point["number"]))
            r.setRoute(rPoints)
            routesArr.insert(0, r)    

        
        self.pBox.clean()

        completeRoutePresent = False
        maxPointsIndex = [0, 0] #count, index 

        self.pBox.append(id = "start", type="sign", inSuc=True)
        for i, r in enumerate(routesArr):
                a = checkRoute(r, points)
                if a.succes:
                    completeRoutePresent = True
                    self.track = r.name
                    self.trackSucc = True
                    for p in a.points:
                        tp=""
                        if p.type:
                            tp = "suc"
                        else:
                            tp = "unsuc"
                        self.pBox.append(id = p.id, type = tp, inSuc = completeRoutePresent)
                    self.showResultLabel(r.name, True)
                    break
                elif a.count > maxPointsIndex[1]:
                    maxPointsIndex[0] = a.count
                    maxPointsIndex[1] = i
        if(not completeRoutePresent):
            a = checkRoute(routesArr[maxPointsIndex[1]], points)
            for p in a.points:
                tp=""
                if p.type:
                    tp = "suc"
                else:
                    tp = "unsuc"
                self.pBox.append(id = p.id, type = tp, inSuc = completeRoutePresent)
                self.showResultLabel(routesArr[maxPointsIndex[1]].name, False)
        self.pBox.append(id = "konec", type="sign", inSuc=True)

    @QtCore.Slot()
    def sendButtonHandle(self):

        name = self.nameInput.text()

        if name == '':

                # msg = QMessageBox()
                # msg.setWindowTitle(str("Chyba!"))
                # msg.setText(str("Zadejte přezdívku!"))
                # msg.exec()

                # lze bud vyuzit odeslani prazdneho jmena jako zruzeni formulare, nebo zobrazit okenko s chybou

                self.hideForm()

        elif(self.trackSucc):

            
                
            
            tday = date.today()
            ftday = tday.strftime("%d.%m.")
            resp = self.sendReq(self.resultTime, name, self.track, ftday)

            if(resp[0]):

                
                self.qrImage = QPixmap(QRcode_maker.create_qrcode(resp[1]))
                self.linkImage.setPixmap(self.qrImage)
                linkText = "Výsledky pro: " + name 
                self.linkLabel.setText(linkText)
           

            self.trackSucc = False
            self.hideForm()

        ### ADDED FOR TESTING
        # elif 1:
        #     name = self.nameInput.text()

            
            
        #     tday = date.today()
        #     ftday = tday.strftime("%d.%m.")
        #     resp = self.sendReq(111111, name, "A", ftday)

        #     if(resp[0]):

                
        #         self.qrImage = QPixmap(QRcode_maker.create_qrcode(resp[1]))
        #         linkText = "Výsledky pro: " + name 
        #         self.linkLabel.setText(linkText)

        #     else:
        #         msg = QMessageBox()
        #         msg.setWindowTitle(str("Chyba!"))
        #         msg.setText(str("Nastala chyba, zkuste znovu"))
        #         msg.exec()

        #     self.trackSucc = False
        #     self.hideForm()
        else:
            msg = QMessageBox()
            msg.setWindowTitle(str("Chyba!"))
            msg.setText(str("Nezdolanou trať nelze nahrat!"))
            msg.exec()


    def sendReq(self, time, name, track, date):
        time = int(time)
        url = "https://festival.obteplice.cz"+"/external_rslts_upload"
        secret = "mamamia"
        data_to_send={
            "name": name, 
            "time": time, 
            "track": track,
            "date": date,
            "secret": secret
        }

        try:
            r = requests.post(url, json=data_to_send)
        except Exception as e:
            msg = QMessageBox()
            err = "Chyba spojení, "+ str(e)
            msg.setWindowTitle(str("Chyba!"))
            msg.setText(str(err))
            msg.exec()
        data = r.json()

        return (True, data["id"])
