# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'obj_Details.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(647, 499)
        Form.setMinimumSize(QSize(300, 300))
        self.fr_title = QFrame(Form)
        self.fr_title.setObjectName(u"fr_title")
        self.fr_title.setGeometry(QRect(20, 10, 320, 36))
        self.fr_title.setMinimumSize(QSize(300, 20))
        self.fr_title.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_title.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_title)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.l_title = QLabel(self.fr_title)
        self.l_title.setObjectName(u"l_title")
        self.l_title.setMinimumSize(QSize(300, 0))

        self.horizontalLayout.addWidget(self.l_title)

        self.fr_subtitle = QFrame(Form)
        self.fr_subtitle.setObjectName(u"fr_subtitle")
        self.fr_subtitle.setGeometry(QRect(20, 50, 320, 36))
        self.fr_subtitle.setMinimumSize(QSize(300, 20))
        self.fr_subtitle.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_subtitle.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.fr_subtitle)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.l_subtitle = QLabel(self.fr_subtitle)
        self.l_subtitle.setObjectName(u"l_subtitle")
        self.l_subtitle.setMinimumSize(QSize(300, 0))

        self.horizontalLayout_2.addWidget(self.l_subtitle)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.l_title.setText(QCoreApplication.translate("Form", u"Name", None))
        self.l_subtitle.setText(QCoreApplication.translate("Form", u"Name", None))
    # retranslateUi

