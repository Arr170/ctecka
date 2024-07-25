import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QTimer
from components import PointsBox, FormWidget

from trackChecking import *
        


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    widget = FormWidget.FormWidget()
    # widget.showMaximized()
    widget.show()

    sys.exit(app.exec())
