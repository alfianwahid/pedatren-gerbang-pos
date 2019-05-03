from PyQt5 import QtCore, QtGui, QtWidgets

def showNotif(textPesan, autoClose=False):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
    msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    font = QtGui.QFont()
    font.setPointSize(10)
    msgBox.setFont(font)
    msgBox.setStyleSheet('QLabel{ color: red}')

    # msgBox.setStandardButtons(QtWidgets.QMessageBox.NoButton)
    msgBox.setText(textPesan)

    if autoClose == True:
        timerClose = QtCore.QTimer(msgBox)
        timerClose.setSingleShot(True)
        timerClose.timeout.connect(msgBox.close)
        timerClose.start(5000)

    msgBox.exec_()