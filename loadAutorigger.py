import importlib
import eyelid_autorigger_script
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

importlib.reload(eyelid_autorigger_script)
import eyerigUI
importlib.reload(eyerigUI)

if __name__ == "__main__":
    
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "AutoEyeRig":
            widget.close()
            widget.deleteLater()

    eyerigUI.runAutorigger()