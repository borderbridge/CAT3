# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'objectView.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(923, 688)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.MainView = QFrame(Form)
        self.MainView.setObjectName(u"MainView")
        self.MainView.setFrameShape(QFrame.Shape.StyledPanel)
        self.MainView.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.MainView)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.HeaderFrame = QFrame(self.MainView)
        self.HeaderFrame.setObjectName(u"HeaderFrame")
        self.HeaderFrame.setMaximumSize(QSize(16777215, 40))
        self.HeaderFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.HeaderFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.HeaderFrame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.TE_NAME = QTextEdit(self.HeaderFrame)
        self.TE_NAME.setObjectName(u"TE_NAME")

        self.verticalLayout_3.addWidget(self.TE_NAME)


        self.verticalLayout_2.addWidget(self.HeaderFrame)

        self.ContentFrame = QFrame(self.MainView)
        self.ContentFrame.setObjectName(u"ContentFrame")
        self.ContentFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ContentFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.ContentFrame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_2 = QFrame(self.ContentFrame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.gridLayout.addWidget(self.frame_2, 0, 0, 1, 1)

        self.frame_3 = QFrame(self.ContentFrame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.gridLayout.addWidget(self.frame_3, 0, 1, 1, 1)

        self.frame_4 = QFrame(self.ContentFrame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_4)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")

        self.gridLayout.addWidget(self.frame_4, 1, 0, 1, 1)

        self.frame_5 = QFrame(self.ContentFrame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton_2 = QPushButton(self.frame_5)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_6.addWidget(self.pushButton_2)


        self.gridLayout.addWidget(self.frame_5, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.ContentFrame)


        self.horizontalLayout.addWidget(self.MainView)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"speichern", None))
    # retranslateUi

