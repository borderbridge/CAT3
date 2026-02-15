from PySide6.QtWidgets import QWidget
from ui_objectView import Ui_Form

class ObjectViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

    def set_data(self, obj: dict):
        self.ui.TE_NAME.setPlainText(obj.get("name", ""))
       #pass
