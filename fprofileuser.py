import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic



class Ui_ProfileUser(QtWidgets.QDialog):

    def __init__(self):
        super(Ui_ProfileUser, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui_profileuser.ui'), self)
        self.setWindowIcon( QtGui.QIcon( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img/logo.png') ) )
        # only close button dan disable resize dengan cursor
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)

