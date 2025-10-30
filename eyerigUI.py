# oj

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import sys 
import importlib
import maya.cmds as cmds
import eyelid_autorigger_script
from eyelid_autorigger_script import eyeAutorigger
importlib.reload(eyelid_autorigger_script)

Ui_AutoEyeRig = None

def maya_main_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QtWidgets.QWidget)    

def runAutorigger():
    try:
        AutoEyeRig.close()
        AutoEyeRig.deleteLater()
    except:
        pass
    
    #if not QtWidgets.QApplication.instance():
    #    app = QtWidgets.QApplication(sys.argv)
    #else:
    #    app = QtWidgets.QApplication.instance()
    AutoEyeRig = Ui_AutoEyeRig()
    AutoEyeRig.show()

    #sys.exit(app.exec())

class Ui_AutoEyeRig(QtWidgets.QMainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("Eye Rig Generator")
        
        self.eyeAR = eyeAutorigger(self)
        self.setupUi()

        
        #self.setMinimumSize(200, 300)
        
        #on macOS, make window a tool to keep it on top
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.QT.Tool, True)
    
    def setupUi(self):

        self.setObjectName("AutoEyeRig")
        self.resize(375, 400)
        
        self.chooseSide_widget = QtWidgets.QWidget(parent=self)
        self.chooseSide_widget.setGeometry(QtCore.QRect(25, 15, 325, 20))
        self.chooseSide_widget.setObjectName("chooseSide_widget")
        self.baseRig_widget = QtWidgets.QWidget(parent=self)
        self.baseRig_widget.setGeometry(QtCore.QRect(30, 45, 325, 140))
        self.baseRig_widget.setObjectName("baseRig_widget")

        self.locCheck_widget = QtWidgets.QWidget(parent=self)
        self.locCheck_widget.setGeometry(QtCore.QRect(30, 190, 325, 44))
        self.locCheck_widget.setObjectName("locCheck_widget")
        self.lowerButton_widget = QtWidgets.QWidget(parent=self)
        self.lowerButton_widget.setGeometry(QtCore.QRect(30, 250, 325, 111))
        self.lowerButton_widget.setObjectName("lowerButton_widget")

        self.chooseSideHLayout = QtWidgets.QHBoxLayout(self.chooseSide_widget)
        self.chooseSideHLayout.setContentsMargins(0, 0, 0, 0)
        self.chooseSideHLayout.setObjectName("chooseSideHLayout")
        self.chooseSideText = QtWidgets.QLabel(parent=self.chooseSide_widget)
        self.chooseSideText.setObjectName("chooseSideText")
        self.chooseSideHLayout.addWidget(self.chooseSideText)
        self.L_check = QtWidgets.QCheckBox(parent=self.chooseSide_widget)
        #self.L_check.setChecked(True)
        self.L_check.setObjectName("L_check")
        self.chooseSideHLayout.addWidget(self.L_check)
        self.R_check = QtWidgets.QCheckBox(parent=self.chooseSide_widget)
        self.R_check.setObjectName("R_check")
        #self.R_check.setChecked(False)

        self.chooseSideHLayout.addWidget(self.R_check)
        
        self.baseRigVLayout = QtWidgets.QVBoxLayout(self.baseRig_widget)
        self.baseRigVLayout.setContentsMargins(0, 0, 0, 0)
        self.baseRigVLayout.setObjectName("baseRigVLayout")
        self.descText = QtWidgets.QPlainTextEdit(parent=self.baseRig_widget)
        self.descText.setMaximumSize(QtCore.QSize(16777215, 100))
        self.descText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.descText.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.descText.setReadOnly(True)
        self.descText.setObjectName("descText")
        self.baseRigVLayout.addWidget(self.descText)
        self.baseRig_Button = QtWidgets.QPushButton(parent=self.baseRig_widget)
        self.baseRig_Button.setObjectName("baseRig_Button")
        self.baseRig_Button.clicked.connect(self.eyeAR.generate_base_rig)
        self.baseRigVLayout.addWidget(self.baseRig_Button)
        
        self.locGridLayout = QtWidgets.QGridLayout(self.locCheck_widget)
        self.locGridLayout.setContentsMargins(0, 0, 0, 0)
        self.locGridLayout.setObjectName("locGridLayout")
        self.upperLid_Check = QtWidgets.QCheckBox(parent=self.locCheck_widget)
        self.upperLid_Check.setChecked(True)
        self.upperLid_Check.setObjectName("upperLidCheck")
        self.locGridLayout.addWidget(self.upperLid_Check, 0, 0, 1, 1)
        self.lowerLid_Check = QtWidgets.QCheckBox(parent=self.locCheck_widget)
        self.lowerLid_Check.setChecked(True)
        self.lowerLid_Check.setObjectName("lowerLid_Check")
        self.locGridLayout.addWidget(self.lowerLid_Check, 0, 1, 1, 1)
        self.upperCrease_Check = QtWidgets.QCheckBox(parent=self.locCheck_widget)
        self.upperCrease_Check.setChecked(True)
        self.upperCrease_Check.setObjectName("upperCrease_Check")
        self.locGridLayout.addWidget(self.upperCrease_Check, 1, 0, 1, 1)
        self.misc_Check = QtWidgets.QCheckBox(parent=self.locCheck_widget)
        self.misc_Check.setChecked(True)
        self.misc_Check.setObjectName("misc_Check")
        self.locGridLayout.addWidget(self.misc_Check, 1, 1, 1, 1)

        self.lowButtonVLayout = QtWidgets.QVBoxLayout(self.lowerButton_widget)
        self.lowButtonVLayout.setContentsMargins(0, 0, 0, 0)
        self.lowButtonVLayout.setObjectName("lowButtonVLayout")
        self.SelLoc_Button = QtWidgets.QPushButton(parent=self.lowerButton_widget)
        self.SelLoc_Button.setObjectName("SelLoc_Button")
        self.lowButtonVLayout.addWidget(self.SelLoc_Button)
        self.SelLoc_Button.clicked.connect(self.eyeAR.generate_locators)   
        self.eyeRig_Button = QtWidgets.QPushButton(parent=self.lowerButton_widget)
        self.eyeRig_Button.setObjectName("eyeRig_Button")
        self.lowButtonVLayout.addWidget(self.eyeRig_Button)
        self.eyeRig_Button.clicked.connect(self.eyeAR.generate_rig)   
        self.mirrorRig_Button = QtWidgets.QPushButton(parent=self.lowerButton_widget)
        self.mirrorRig_Button.setObjectName("mirrorRig_Button")
        self.lowButtonVLayout.addWidget(self.mirrorRig_Button)
        self.mirrorRig_Button.clicked.connect(self.eyeAR.mirror_rig)   
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def FGetLeftLock(self):
        return self.L_check.isChecked()
    
    def FGetRightLock(self):
        return self.R_check.isChecked()

    def FGetUpperLock(self):
        return self.upperLid_Check.isChecked()
    
    def FGetLowerLock(self):
        return self.lowerLid_Check.isChecked()
    
    def FGetUpperCreaseLock(self):
        return self.upperCrease_Check.isChecked()
    
    def FGetMiscLock(self):
        return self.misc_Check.isChecked()

        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AutoEyeRig", "Eye Rigger"))
        self.chooseSideText.setText(_translate("AutoEyeRig", "Choose side to generate:  "))
        self.L_check.setText(_translate("AutoEyeRig", "Left"))
        self.R_check.setText(_translate("AutoEyeRig", "Right"))
        self.descText.setPlainText(_translate("AutoEyeRig", "Select eye mesh, then create base eye rig.\n"
        "Once base rig is created, create & place locators, then click generate rig"))
        self.baseRig_Button.setText(_translate("AutoEyeRig", "Create base eye rig"))

        self.upperLid_Check.setText(_translate("AutoEyeRig", "Upper Lid Locators"))
        self.lowerLid_Check.setText(_translate("AutoEyeRig", "Lower Lid Locators"))
        self.upperCrease_Check.setText(_translate("AutoEyeRig", "Upper Crease Locators"))
        self.misc_Check.setText(_translate("AutoEyeRig", "Misc Eye Locators"))

        self.SelLoc_Button.setText(_translate("AutoEyeRig", "Generate Selected Locators"))
        self.eyeRig_Button.setText(_translate("AutoEyeRig", "Generate Eye Rig"))
        self.mirrorRig_Button.setText(_translate("AutoEyeRig", "Mirror L_ to R_"))

if __name__ == "__main__":
    runAutorigger()