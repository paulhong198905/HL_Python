# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file '_32_UI_2025_10_16.ui'
##
## Created by: Qt User Interface Compiler version 6.2.0
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
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(839, 539)
        MainWindow.setStyleSheet(u"r: #A71E2A;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_1 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_1.setSpacing(0)
        self.verticalLayout_1.setObjectName(u"verticalLayout_1")
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.QFrame_Header_1 = QFrame(self.centralwidget)
        self.QFrame_Header_1.setObjectName(u"QFrame_Header_1")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.QFrame_Header_1.sizePolicy().hasHeightForWidth())
        self.QFrame_Header_1.setSizePolicy(sizePolicy)
        self.QFrame_Header_1.setStyleSheet(u"QFrame#QFrame_Header_1 {\n"
"	background-color: lightgray;\n"
"}")
        self.QFrame_Header_1.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Header_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_header = QHBoxLayout(self.QFrame_Header_1)
        self.horizontalLayout_header.setObjectName(u"horizontalLayout_header")
        self.Header_Label = QLabel(self.QFrame_Header_1)
        self.Header_Label.setObjectName(u"Header_Label")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.Header_Label.setFont(font)
        self.Header_Label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_header.addWidget(self.Header_Label)


        self.verticalLayout_1.addWidget(self.QFrame_Header_1)

        self.QFrame_Bottom_1 = QFrame(self.centralwidget)
        self.QFrame_Bottom_1.setObjectName(u"QFrame_Bottom_1")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(20)
        sizePolicy1.setHeightForWidth(self.QFrame_Bottom_1.sizePolicy().hasHeightForWidth())
        self.QFrame_Bottom_1.setSizePolicy(sizePolicy1)
        self.QFrame_Bottom_1.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Bottom_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.QFrame_Bottom_1)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.QFrame_Left_2 = QFrame(self.QFrame_Bottom_1)
        self.QFrame_Left_2.setObjectName(u"QFrame_Left_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(18)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.QFrame_Left_2.sizePolicy().hasHeightForWidth())
        self.QFrame_Left_2.setSizePolicy(sizePolicy2)
        self.QFrame_Left_2.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Left_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.QFrame_Left_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.QFrame_CKPT_3 = QFrame(self.QFrame_Left_2)
        self.QFrame_CKPT_3.setObjectName(u"QFrame_CKPT_3")
        sizePolicy.setHeightForWidth(self.QFrame_CKPT_3.sizePolicy().hasHeightForWidth())
        self.QFrame_CKPT_3.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.QFrame_CKPT_3)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.PN_Title_Label = QLabel(self.QFrame_CKPT_3)
        self.PN_Title_Label.setObjectName(u"PN_Title_Label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(18)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.PN_Title_Label.sizePolicy().hasHeightForWidth())
        self.PN_Title_Label.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.PN_Title_Label.setFont(font1)
        self.PN_Title_Label.setStyleSheet(u"color: black;")
        self.PN_Title_Label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.PN_Title_Label)

        self.PN_Value_LineEdit = QLineEdit(self.QFrame_CKPT_3)
        self.PN_Value_LineEdit.setObjectName(u"PN_Value_LineEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(28)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.PN_Value_LineEdit.sizePolicy().hasHeightForWidth())
        self.PN_Value_LineEdit.setSizePolicy(sizePolicy4)
        self.PN_Value_LineEdit.setFont(font1)
        self.PN_Value_LineEdit.setStyleSheet(u"background-color: #333333; color: white; border: 0px;")
        self.PN_Value_LineEdit.setMaxLength(8)
        self.PN_Value_LineEdit.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.PN_Value_LineEdit)

        self.Program_Title_Label = QLabel(self.QFrame_CKPT_3)
        self.Program_Title_Label.setObjectName(u"Program_Title_Label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(10)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.Program_Title_Label.sizePolicy().hasHeightForWidth())
        self.Program_Title_Label.setSizePolicy(sizePolicy5)
        self.Program_Title_Label.setFont(font1)
        self.Program_Title_Label.setStyleSheet(u"color: black;")
        self.Program_Title_Label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.Program_Title_Label)

        self.QLabel_ProgramName = QLabel(self.QFrame_CKPT_3)
        self.QLabel_ProgramName.setObjectName(u"QLabel_ProgramName")
        sizePolicy4.setHeightForWidth(self.QLabel_ProgramName.sizePolicy().hasHeightForWidth())
        self.QLabel_ProgramName.setSizePolicy(sizePolicy4)
        self.QLabel_ProgramName.setFont(font1)
        self.QLabel_ProgramName.setStyleSheet(u"background-color: #333333; color: white;")
        self.QLabel_ProgramName.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.QLabel_ProgramName)


        self.verticalLayout_2.addWidget(self.QFrame_CKPT_3)

        self.QFrame_Program_3 = QFrame(self.QFrame_Left_2)
        self.QFrame_Program_3.setObjectName(u"QFrame_Program_3")
        sizePolicy.setHeightForWidth(self.QFrame_Program_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Program_3.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.QFrame_Program_3)

        self.QFrame_Tests_3 = QFrame(self.QFrame_Left_2)
        self.QFrame_Tests_3.setObjectName(u"QFrame_Tests_3")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(5)
        sizePolicy6.setHeightForWidth(self.QFrame_Tests_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Tests_3.setSizePolicy(sizePolicy6)
        self.lbl_PowerMode_Off = QLabel(self.QFrame_Tests_3)
        self.lbl_PowerMode_Off.setObjectName(u"lbl_PowerMode_Off")
        self.lbl_PowerMode_Off.setGeometry(QRect(10, 10, 101, 31))
        self.lbl_PowerMode_Run = QLabel(self.QFrame_Tests_3)
        self.lbl_PowerMode_Run.setObjectName(u"lbl_PowerMode_Run")
        self.lbl_PowerMode_Run.setGeometry(QRect(130, 10, 101, 31))
        self.lbl_Wiper_Off = QLabel(self.QFrame_Tests_3)
        self.lbl_Wiper_Off.setObjectName(u"lbl_Wiper_Off")
        self.lbl_Wiper_Off.setGeometry(QRect(10, 60, 101, 31))
        self.lbl_Wiper_Intermittent = QLabel(self.QFrame_Tests_3)
        self.lbl_Wiper_Intermittent.setObjectName(u"lbl_Wiper_Intermittent")
        self.lbl_Wiper_Intermittent.setGeometry(QRect(130, 60, 101, 31))
        self.lbl_Wiper_Slow = QLabel(self.QFrame_Tests_3)
        self.lbl_Wiper_Slow.setObjectName(u"lbl_Wiper_Slow")
        self.lbl_Wiper_Slow.setGeometry(QRect(260, 60, 101, 31))

        self.verticalLayout_2.addWidget(self.QFrame_Tests_3)

        self.QFrame_Malfunction_3 = QFrame(self.QFrame_Left_2)
        self.QFrame_Malfunction_3.setObjectName(u"QFrame_Malfunction_3")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(2)
        sizePolicy7.setHeightForWidth(self.QFrame_Malfunction_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Malfunction_3.setSizePolicy(sizePolicy7)
        self.horizontalLayout_Malfunction = QHBoxLayout(self.QFrame_Malfunction_3)
        self.horizontalLayout_Malfunction.setSpacing(0)
        self.horizontalLayout_Malfunction.setObjectName(u"horizontalLayout_Malfunction")
        self.horizontalLayout_Malfunction.setContentsMargins(0, 0, 0, 0)
        self.QFrame_Malfunction_Left = QFrame(self.QFrame_Malfunction_3)
        self.QFrame_Malfunction_Left.setObjectName(u"QFrame_Malfunction_Left")
        sizePolicy8 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy8.setHorizontalStretch(1)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.QFrame_Malfunction_Left.sizePolicy().hasHeightForWidth())
        self.QFrame_Malfunction_Left.setSizePolicy(sizePolicy8)
        self.QFrame_Malfunction_Left.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Malfunction_Left.setFrameShadow(QFrame.Raised)
        self.lbl_Wiper_CurrentState = QLabel(self.QFrame_Malfunction_Left)
        self.lbl_Wiper_CurrentState.setObjectName(u"lbl_Wiper_CurrentState")
        self.lbl_Wiper_CurrentState.setGeometry(QRect(10, 10, 101, 31))

        self.horizontalLayout_Malfunction.addWidget(self.QFrame_Malfunction_Left)

        self.QFrame_Malfunction_Right = QFrame(self.QFrame_Malfunction_3)
        self.QFrame_Malfunction_Right.setObjectName(u"QFrame_Malfunction_Right")
        sizePolicy8.setHeightForWidth(self.QFrame_Malfunction_Right.sizePolicy().hasHeightForWidth())
        self.QFrame_Malfunction_Right.setSizePolicy(sizePolicy8)
        self.QFrame_Malfunction_Right.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Malfunction_Right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_Malfunction_Right = QVBoxLayout(self.QFrame_Malfunction_Right)
        self.verticalLayout_Malfunction_Right.setSpacing(0)
        self.verticalLayout_Malfunction_Right.setObjectName(u"verticalLayout_Malfunction_Right")
        self.verticalLayout_Malfunction_Right.setContentsMargins(0, 0, 0, 0)
        self.Label_continuity_result = QLabel(self.QFrame_Malfunction_Right)
        self.Label_continuity_result.setObjectName(u"Label_continuity_result")
        self.Label_continuity_result.setAlignment(Qt.AlignCenter)

        self.verticalLayout_Malfunction_Right.addWidget(self.Label_continuity_result)


        self.horizontalLayout_Malfunction.addWidget(self.QFrame_Malfunction_Right)


        self.verticalLayout_2.addWidget(self.QFrame_Malfunction_3)


        self.horizontalLayout_2.addWidget(self.QFrame_Left_2)

        self.QFrame_Right_2 = QFrame(self.QFrame_Bottom_1)
        self.QFrame_Right_2.setObjectName(u"QFrame_Right_2")
        sizePolicy8.setHeightForWidth(self.QFrame_Right_2.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_2.setSizePolicy(sizePolicy8)
        font2 = QFont()
        font2.setPointSize(17)
        self.QFrame_Right_2.setFont(font2)
        self.QFrame_Right_2.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_Right_3 = QVBoxLayout(self.QFrame_Right_2)
        self.verticalLayout_Right_3.setSpacing(0)
        self.verticalLayout_Right_3.setObjectName(u"verticalLayout_Right_3")
        self.verticalLayout_Right_3.setContentsMargins(0, 0, 0, 0)
        self.QFrame_Right_Section1_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section1_3.setObjectName(u"QFrame_Right_Section1_3")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(1)
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section1_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section1_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section1_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section1_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section1_3)

        self.QFrame_Right_Section2_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section2_3.setObjectName(u"QFrame_Right_Section2_3")
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section2_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section2_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section2_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section2_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_Section2_3 = QHBoxLayout(self.QFrame_Right_Section2_3)
        self.horizontalLayout_Section2_3.setObjectName(u"horizontalLayout_Section2_3")
        self.horizontalLayout_Section2_3.setContentsMargins(0, 0, 0, 0)
        self.pushButton_STOP = QPushButton(self.QFrame_Right_Section2_3)
        self.pushButton_STOP.setObjectName(u"pushButton_STOP")
        sizePolicy10 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.pushButton_STOP.sizePolicy().hasHeightForWidth())
        self.pushButton_STOP.setSizePolicy(sizePolicy10)
        font3 = QFont()
        font3.setPointSize(17)
        font3.setBold(True)
        self.pushButton_STOP.setFont(font3)
        self.pushButton_STOP.setStyleSheet(u"QPushButton {\n"
"    border-radius: 15px;\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #FF8A8A,\n"
"        stop:0.5 #E57373,\n"
"        stop:1 #D32F2F);\n"
"    color: white;\n"
"    border: 1px solid #B71C1C;\n"
"    font-weight: bold;\n"
"    padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #FF9E9E,\n"
"        stop:0.5 #EF5350,\n"
"        stop:1 #E53935);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #D32F2F,\n"
"        stop:0.5 #C62828,\n"
"        stop:1 #B71C1C);\n"
"    padding: 9px 7px 7px 9px;\n"
"}")

        self.horizontalLayout_Section2_3.addWidget(self.pushButton_STOP)


        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section2_3)

        self.QFrame_Right_Section3_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section3_3.setObjectName(u"QFrame_Right_Section3_3")
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section3_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section3_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section3_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section3_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section3_3)

        self.QFrame_Right_Section4_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section4_3.setObjectName(u"QFrame_Right_Section4_3")
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section4_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section4_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section4_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section4_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_Section4_3 = QHBoxLayout(self.QFrame_Right_Section4_3)
        self.horizontalLayout_Section4_3.setObjectName(u"horizontalLayout_Section4_3")
        self.horizontalLayout_Section4_3.setContentsMargins(0, 0, 0, 0)
        self.pushButton_Start_REDO_ = QPushButton(self.QFrame_Right_Section4_3)
        self.pushButton_Start_REDO_.setObjectName(u"pushButton_Start_REDO_")
        self.pushButton_Start_REDO_.setEnabled(True)
        sizePolicy10.setHeightForWidth(self.pushButton_Start_REDO_.sizePolicy().hasHeightForWidth())
        self.pushButton_Start_REDO_.setSizePolicy(sizePolicy10)
        font4 = QFont()
        font4.setPointSize(13)
        font4.setBold(True)
        self.pushButton_Start_REDO_.setFont(font4)
        self.pushButton_Start_REDO_.setStyleSheet(u"QPushButton {\n"
"    border-radius: 15px;\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #E8F5E9,\n"
"        stop:0.5 #C8E6C9,\n"
"        stop:1 #A5D6A7);\n"
"    color: #4A5568;\n"
"    border: 1px solid #81C784;\n"
"    font-weight: bold;\n"
"    padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #F1F8E9,\n"
"        stop:0.5 #DCEDC8,\n"
"        stop:1 #C5E1A5);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"        stop:0 #A5D6A7,\n"
"        stop:0.5 #81C784,\n"
"        stop:1 #66BB6A);\n"
"    color: white;\n"
"    padding: 9px 7px 7px 9px;\n"
"}")

        self.horizontalLayout_Section4_3.addWidget(self.pushButton_Start_REDO_)


        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section4_3)

        self.QFrame_Right_Section5_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section5_3.setObjectName(u"QFrame_Right_Section5_3")
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section5_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section5_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section5_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section5_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section5_3)

        self.QFrame_Right_Section6_3 = QFrame(self.QFrame_Right_2)
        self.QFrame_Right_Section6_3.setObjectName(u"QFrame_Right_Section6_3")
        sizePolicy9.setHeightForWidth(self.QFrame_Right_Section6_3.sizePolicy().hasHeightForWidth())
        self.QFrame_Right_Section6_3.setSizePolicy(sizePolicy9)
        self.QFrame_Right_Section6_3.setFrameShape(QFrame.StyledPanel)
        self.QFrame_Right_Section6_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_DateTime = QVBoxLayout(self.QFrame_Right_Section6_3)
        self.verticalLayout_DateTime.setSpacing(0)
        self.verticalLayout_DateTime.setObjectName(u"verticalLayout_DateTime")
        self.verticalLayout_DateTime.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_ServerStatus = QHBoxLayout()
        self.horizontalLayout_ServerStatus.setObjectName(u"horizontalLayout_ServerStatus")
        self.QLabel_ServerStatusLabel = QLabel(self.QFrame_Right_Section6_3)
        self.QLabel_ServerStatusLabel.setObjectName(u"QLabel_ServerStatusLabel")
        font5 = QFont()
        font5.setPointSize(12)
        self.QLabel_ServerStatusLabel.setFont(font5)
        self.QLabel_ServerStatusLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_ServerStatus.addWidget(self.QLabel_ServerStatusLabel)

        self.QFrame_ServerStatusIndicator = QFrame(self.QFrame_Right_Section6_3)
        self.QFrame_ServerStatusIndicator.setObjectName(u"QFrame_ServerStatusIndicator")
        self.QFrame_ServerStatusIndicator.setMinimumSize(QSize(20, 20))
        self.QFrame_ServerStatusIndicator.setMaximumSize(QSize(20, 20))
        self.QFrame_ServerStatusIndicator.setStyleSheet(u"\n"
"					/* Initial style: Always Green (Simulated Connection) */\n"
"					QFrame#QFrame_ServerStatusIndicator {\n"
"					 background-color: red;\n"
"					 border-radius: 10px; /* Makes it a circle */\n"
"					}\n"
"				   ")
        self.QFrame_ServerStatusIndicator.setFrameShape(QFrame.NoFrame)
        self.QFrame_ServerStatusIndicator.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_ServerStatus.addWidget(self.QFrame_ServerStatusIndicator)


        self.verticalLayout_DateTime.addLayout(self.horizontalLayout_ServerStatus)

        self.QLabel_DateTime = QLabel(self.QFrame_Right_Section6_3)
        self.QLabel_DateTime.setObjectName(u"QLabel_DateTime")
        font6 = QFont()
        font6.setPointSize(11)
        self.QLabel_DateTime.setFont(font6)

        self.verticalLayout_DateTime.addWidget(self.QLabel_DateTime)


        self.verticalLayout_Right_3.addWidget(self.QFrame_Right_Section6_3)


        self.horizontalLayout_2.addWidget(self.QFrame_Right_2)


        self.verticalLayout_1.addWidget(self.QFrame_Bottom_1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 839, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Header_Label.setText(QCoreApplication.translate("MainWindow", u"SGM CKPT Elec Validation V0.9", None))
        self.PN_Title_Label.setText(QCoreApplication.translate("MainWindow", u"\u603b\u6210\u96f6\u4ef6\u53f7:", None))
        self.PN_Value_LineEdit.setText("")
        self.PN_Value_LineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"*\u626b\u63cf\u96f6\u4ef6\u53f7*", None))
        self.Program_Title_Label.setText(QCoreApplication.translate("MainWindow", u"\u9879\u76ee:", None))
        self.QLabel_ProgramName.setText("")
        self.lbl_PowerMode_Off.setText(QCoreApplication.translate("MainWindow", u"PM_Off", None))
        self.lbl_PowerMode_Run.setText(QCoreApplication.translate("MainWindow", u"PM_Run", None))
        self.lbl_Wiper_Off.setText(QCoreApplication.translate("MainWindow", u"Wiper_Off", None))
        self.lbl_Wiper_Intermittent.setText(QCoreApplication.translate("MainWindow", u"Wiper_Intermittent", None))
        self.lbl_Wiper_Slow.setText(QCoreApplication.translate("MainWindow", u"Wiper_Slow", None))
        self.lbl_Wiper_CurrentState.setText(QCoreApplication.translate("MainWindow", u"Wiper_CurrentState", None))
        self.Label_continuity_result.setText(QCoreApplication.translate("MainWindow", u"Continuity Result", None))
        self.pushButton_STOP.setText(QCoreApplication.translate("MainWindow", u"\u6025\u505c", None))
        self.pushButton_Start_REDO_.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8/\u91cd\u6d4b", None))
        self.QLabel_ServerStatusLabel.setText(QCoreApplication.translate("MainWindow", u"MES\u670d\u52a1\u5668", None))
    # retranslateUi

