from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from PIL import Image
from io import BytesIO
import os 
import qrcode 


def create_qrcode(id='', base = ''):
    url =  "https://festival.obteplice.cz/" + "?forceFocus=" + str(id)
    qr = qrcode.QRCode(version=1, box_size=7, border=3)
    qr.add_data(url)


    qr.make()

    img = qr.make_image(fill_color = "black", back_color ="white")

    qr_image_bytes = BytesIO()
    img.save(qr_image_bytes)
    img.seek(0)

    img = Image.open(qr_image_bytes)
    img = formateImage(img)


    return img


def formateImage(image):
    image = image.convert("RGBA")
    data = image.tobytes("raw", "RGBA")
    qimage = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimage)

