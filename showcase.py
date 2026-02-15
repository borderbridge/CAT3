# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QWidget
from ui_showcase import Ui_Form  # Prüfe den Klassennamen in ui_mein_widget.py!

class ShowcaseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)














