
import sys, os, json, pedatren, notification
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class Ui_Login(QtWidgets.QDialog):
    switch_window = QtCore.pyqtSignal()
    PedatrenApi = pedatren.PedatrenApi()

    def __init__(self):
        super(Ui_Login, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui_login.ui'), self)
        self.setWindowIcon( QtGui.QIcon( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img/logo.png') ) )
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        qimg = QtGui.QImage( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img/logo.png') )
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.logo.setPixmap(pixmap)

        self.buttonReset.clicked.connect(self.resetOnClicked)
        self.buttonLogin.clicked.connect(self.loginOnClicked)

    def resetOnClicked(self):
        self.username.clear()
        self.password.clear()

    def loginOnClicked(self):
        username = self.username.text()
        password = self.password.text()
        self.username.clear()
        self.password.clear()
        self.username.setFocus()

        if username == '':
            notification.showNotif('Username tidak boleh kosong')
            return
        if password == '':
            notification.showNotif('Password tidak boleh kosong')
            return

        loginResult = self.PedatrenApi.login(username, password)
        if loginResult != True:
            textBody = json.loads(loginResult.text)
            notification.showNotif(textBody['message'])
        else:
            checkAksesPerizinan = self.PedatrenApi.getListPerizinan()
            if checkAksesPerizinan.status_code < 200 or checkAksesPerizinan.status_code >= 300:
                textBody = json.loads(checkAksesPerizinan.text)
                notification.showNotif(textBody['message'])
            else:
                self.switch_window.emit()
                self.close()

