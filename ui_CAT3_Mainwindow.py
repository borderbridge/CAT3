# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CAT3_Mainwindow.ui'
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
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStackedWidget, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1167, 755)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAutoFillBackground(False)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.NavigationListWidget = QListWidget(self.centralwidget)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        __qlistwidgetitem = QListWidgetItem(self.NavigationListWidget)
        __qlistwidgetitem.setIcon(icon);
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        __qlistwidgetitem1 = QListWidgetItem(self.NavigationListWidget)
        __qlistwidgetitem1.setIcon(icon1);
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.WeatherClear))
        __qlistwidgetitem2 = QListWidgetItem(self.NavigationListWidget)
        __qlistwidgetitem2.setIcon(icon2);
        self.NavigationListWidget.setObjectName(u"NavigationListWidget")
        self.NavigationListWidget.setMinimumSize(QSize(220, 0))
        self.NavigationListWidget.setMaximumSize(QSize(220, 16777215))
        self.NavigationListWidget.setMouseTracking(False)

        self.horizontalLayout.addWidget(self.NavigationListWidget)

        self.DisplayedWindwoWidget = QStackedWidget(self.centralwidget)
        self.DisplayedWindwoWidget.setObjectName(u"DisplayedWindwoWidget")
        self.NewEntry = QWidget()
        self.NewEntry.setObjectName(u"NewEntry")
        self.horizontalLayout_3 = QHBoxLayout(self.NewEntry)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.MainView = QFrame(self.NewEntry)
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


        self.horizontalLayout_3.addWidget(self.MainView)

        self.DisplayedWindwoWidget.addWidget(self.NewEntry)
        self.MyObjects = QWidget()
        self.MyObjects.setObjectName(u"MyObjects")
        self.verticalLayout_7 = QVBoxLayout(self.MyObjects)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.filterInput = QLineEdit(self.MyObjects)
        self.filterInput.setObjectName(u"filterInput")

        self.verticalLayout_7.addWidget(self.filterInput)

        self.objectsList = QListWidget(self.MyObjects)
        self.objectsList.setObjectName(u"objectsList")

        self.verticalLayout_7.addWidget(self.objectsList)

        self.DisplayedWindwoWidget.addWidget(self.MyObjects)
        self.Starmap = QWidget()
        self.Starmap.setObjectName(u"Starmap")
        self.label = QLabel(self.Starmap)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(240, 290, 341, 20))
        self.DisplayedWindwoWidget.addWidget(self.Starmap)
        self.ObjectDetails = QWidget()
        self.ObjectDetails.setObjectName(u"ObjectDetails")
        self.horizontalLayout_4 = QHBoxLayout(self.ObjectDetails)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.frame = QFrame(self.ObjectDetails)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_8.addWidget(self.frame_6)


        self.horizontalLayout_4.addWidget(self.frame)

        self.DisplayedWindwoWidget.addWidget(self.ObjectDetails)

        self.horizontalLayout.addWidget(self.DisplayedWindwoWidget)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1167, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.NavigationListWidget.currentRowChanged.connect(self.DisplayedWindwoWidget.setCurrentIndex)

        self.DisplayedWindwoWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"CAT 3 - Catalog of Astronomical Things", None))

        __sortingEnabled = self.NavigationListWidget.isSortingEnabled()
        self.NavigationListWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.NavigationListWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"Neues Objekt", None));
        ___qlistwidgetitem1 = self.NavigationListWidget.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Meine Objekte", None));
        ___qlistwidgetitem2 = self.NavigationListWidget.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Sternkarte", None));
        self.NavigationListWidget.setSortingEnabled(__sortingEnabled)

        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"speichern", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Hier gibts noch nichts zu sehen", None))
    # retranslateUi

