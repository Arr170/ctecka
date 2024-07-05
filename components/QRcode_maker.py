from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from PIL import Image
from io import BytesIO
import qrcode 

class QRcode(QtWidgets.QWidget):
    def __init__(self, id):
        super().__init__()

        self.qrcode = QLabel()


        url = "http://192.168.0.104:5000/" + "?forceFocus=" + str(id)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color = "black", back_color ="white")

        qr_image_bytes = BytesIO()
        img.save(qr_image_bytes)
        img.seek(0)

        img = Image.open(qr_image_bytes)
        img = self.formateImage(img)


        pixmap = QPixmap(img)
        label = QLabel()
        label.setPixmap(pixmap)

        layout = QHBoxLayout(self)
        layout.addWidget(label)


    def formateImage(self, image):
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)

