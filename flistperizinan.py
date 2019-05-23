
import sys, os, json, base64, pedatren, notification, fdetailperizinan, fprofileuser
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime


class Ui_TablePerizinan(QtWidgets.QMainWindow):
    PedatrenApi = pedatren.PedatrenApi()
    __lastWindowState = None
    __childDialog = None
    __itemIzin = None
    __userProfile = None
    __userProfileDialog = None
    __basePath = os.path.dirname(os.path.abspath(__file__))
    __isAutoConfirmOK = False
    __isPublicIP = True
    __isLocalIP = False
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui_TablePerizinan, self).__init__()
        uic.loadUi(os.path.join(self.__basePath, 'ui_listperizinan.ui'), self)
        self.setWindowIcon( QtGui.QIcon( os.path.join(self.__basePath, 'img/logo.png') ) )
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.__lastWindowState = self.windowState()
        self.label_fotodiri.clear()

        self.buttonLogout.setIcon(QtGui.QIcon(os.path.join(self.__basePath, 'img/logout.ico')))
        self.buttonRefresh.setIcon(QtGui.QIcon(os.path.join(self.__basePath, 'img/refresh.ico')))
        self.tablePerizinan.installEventFilter(self)
        self.input_qr_code.installEventFilter(self)
        self.input_cari.installEventFilter(self)

        self.buttonLogout.clicked.connect(self.logoutOnClicked)
        self.buttonRefresh.clicked.connect(self.refreshOnClicked)
        self.tablePerizinan.doubleClicked.connect(self.doubleClickRow)
        self.input_qr_code.returnPressed.connect(self.readInputQrCode)
        self.input_cari.returnPressed.connect(self.cari)
        self.input_qr_code.addAction(QtGui.QIcon(os.path.join(self.__basePath, 'img/qr.ico')), QtWidgets.QLineEdit.LeadingPosition)

        self.menu_ManualConfirm.setChecked(True)
        self.menu_AutoConfirm.setChecked(False)
        self.menu_ManualConfirm.triggered.connect(self.toggleMenuManualConfirm)
        self.menu_AutoConfirm.triggered.connect(self.toggleMenuAutoConfirm)
        self.menu_About.triggered.connect(self.menuAbout)
        # self.input_cari.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d+'), self))
        self.menu_ProfileUser.triggered.connect(self.showUserProfile)
        self.menu_Keluar.triggered.connect(self.logoutOnClicked)
        self.__iconReadingQrPath = os.path.join(self.__basePath, 'img/qr-reading-focus.jpg').replace('\\', '/')



    def __responseApiHandler(self, response, autoCloseNotif=False):
        if response is None:
            notification.showNotif('Ops, error tidak diketahui, response API is None')
            self.close()
            sys.exit(1)
            return False

        elif 'exception' in response:
            notification.showNotif(response['exception'], autoCloseNotif)
            return False

        elif response.status_code == 401:
            self.close()
            self.switch_window.emit()
            return False
        elif response.status_code < 200 or response.status_code >= 300:
            errMsg = response.json()
            notification.showNotif(errMsg['message'], autoCloseNotif)
            return False

        return True

    def menuAbout(self):
        QtWidgets.QMessageBox.about(self, 'About', 'Aplikasi Pedatren Gerbang Pos. \n\n\nVersi : 1.0.0 \nRelease : Mei 2019 \nDeveloped by : @alfianwahid')

    def toggleMenuManualConfirm(self):
        self.menu_ManualConfirm.setChecked(True)
        self.menu_AutoConfirm.setChecked(False)

    def toggleMenuAutoConfirm(self):
        self.menu_ManualConfirm.setChecked(False)
        self.menu_AutoConfirm.setChecked(True)

    def __getProfileUser(self):
        if (not self.PedatrenApi.credentials) is False:
            responseUserProfile = self.PedatrenApi.getUserProfile()
            if responseUserProfile.status_code >= 200 and responseUserProfile.status_code < 300:
                self.__userProfile = json.loads(responseUserProfile.text)
                levelScope = self.PedatrenApi.credentials['scope'][len(self.PedatrenApi.credentials['scope'])-1]
                self.label_credential_nama_lengkap.setText( self.PedatrenApi.credentials['nama_lengkap'] + ' (' + levelScope +')' )
                self.label_credential_nama_lengkap.adjustSize()


                userProfileFoto = self.PedatrenApi.getImage(self.__userProfile['fotodiri']['small'])
                if userProfileFoto.status_code >= 200 and userProfileFoto.status_code < 300:
                    qimg = QtGui.QImage.fromData(userProfileFoto.content)
                    pixmap = QtGui.QPixmap.fromImage(qimg)
                    self.label_fotodiri.setPixmap(pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio))

                    self.label_credential_nik.setText(self.__userProfile['nik'])
                    self.label_credential_nik.adjustSize()

    def showUserProfile(self):
        if not self.__userProfile:
            notification.showNotif('Kegagalan system mendapatkan info user Anda. Silahkan coba login ulang lagi.')
            return

        self.__userProfileDialog = fprofileuser.Ui_ProfileUser()
        self.__userProfileDialog.tabWidget.setCurrentIndex(0)

        # Biodata
        fotodiri = self.PedatrenApi.getImage(self.__userProfile['fotodiri']['medium'])
        if fotodiri.status_code >= 200 and fotodiri.status_code < 300:
            qimg = QtGui.QImage.fromData(fotodiri.content)
            pixmap = QtGui.QPixmap.fromImage(qimg)
            self.__userProfileDialog.label_fotodiri.setPixmap(pixmap.scaled(190, 190, QtCore.Qt.KeepAspectRatio))

        self.__userProfileDialog.label_nokk.setText(self.__userProfile['nokk'])
        self.__userProfileDialog.label_nik.setText(self.__userProfile['nik'])
        self.__userProfileDialog.label_niup.setText(self.__userProfile['warga_pesantren']['niup'])
        self.__userProfileDialog.label_nama_lengkap.setText(self.__userProfile['nama_lengkap'])
        self.__userProfileDialog.label_gender.setText('Laki-laki' if self.__userProfile['jenis_kelamin'] == 'L'  else 'Perempuan')
        self.__userProfileDialog.label_ttl.setText(self.__userProfile['tempat_lahir'] + ', ' + self.__userProfile['tanggal_lahir'])
        self.__userProfileDialog.label_umur.setText(str(self.__userProfile['umur']) + ' Tahun')

        self.__userProfileDialog.label_anak_ke.setText(str(self.__userProfile['anak_ke']) + ' <strong>dari</strong> ' + str(self.__userProfile['jum_saudara']) + ' bersaudara')
        self.__userProfileDialog.label_kecamatan.setText(self.__userProfile['kecamatan'])
        self.__userProfileDialog.label_kabupaten.setText(self.__userProfile['kabupaten'])
        self.__userProfileDialog.label_provinsi.setText(self.__userProfile['provinsi'])
        self.__userProfileDialog.label_negara.setText(self.__userProfile['negara'])

        # Status Santri
        if 'santri' not in self.__userProfile:
            self.__userProfileDialog.tabWidget.removeTab(2)
        else:
            last_index_santri = len(self.__userProfile['santri'])-1
            self.__userProfileDialog.label_nis.setText(self.__userProfile['santri'][last_index_santri]['nis'])
            nis_sampai = ' <strong>sampai</strong> ' + self.__userProfile['santri'][last_index_santri]['tanggal_akhir'] if self.__userProfile['santri'][last_index_santri]['tanggal_akhir'] else ''
            self.__userProfileDialog.label_santri_sejak.setText(self.__userProfile['santri'][last_index_santri]['tanggal_mulai'] +  nis_sampai)

            if 'domisili_santri' in self.__userProfile:
                headers = ['Kamar', 'Wilayah', 'Tanggal Ditempati', 'Tanggal Pindah']
                self.__userProfileDialog.tableDomisiliSantri.setColumnCount(len(headers))
                self.__userProfileDialog.tableDomisiliSantri.setHorizontalHeaderLabels(headers)
                font = QtGui.QFont()
                font.setBold(True)
                self.__userProfileDialog.tableDomisiliSantri.horizontalHeader().setFont(font)
                self.__userProfileDialog.tableDomisiliSantri.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                self.__userProfileDialog.tableDomisiliSantri.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
                self.__userProfileDialog.tableDomisiliSantri.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
                self.__userProfileDialog.tableDomisiliSantri.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

                self.__userProfileDialog.tableDomisiliSantri.setRowCount(len(self.__userProfile['domisili_santri']))
                no = 0
                for row in self.__userProfile['domisili_santri']:
                    self.__userProfileDialog.tableDomisiliSantri.setItem(no, 0, QtWidgets.QTableWidgetItem(row['kamar']))
                    self.__userProfileDialog.tableDomisiliSantri.setItem(no, 1, QtWidgets.QTableWidgetItem(row['wilayah']))
                    self.__userProfileDialog.tableDomisiliSantri.setItem(no, 2, QtWidgets.QTableWidgetItem(row['tanggal_mulai']))
                    self.__userProfileDialog.tableDomisiliSantri.setItem(no, 3, QtWidgets.QTableWidgetItem(row['tanggal_akhir']))
                    no += 1

        # Keluarga
        if 'keluarga' not in self.__userProfile:
            self.__userProfileDialog.tabWidget.removeTab(1)
        else:
            headers = ['NIK', 'Nama Lengkap', 'Status Keluarga', 'Sebagai Wali']
            self.__userProfileDialog.tableKeluarga.setColumnCount(len(headers))
            self.__userProfileDialog.tableKeluarga.setHorizontalHeaderLabels(headers)
            font = QtGui.QFont()
            font.setBold(True)
            self.__userProfileDialog.tableKeluarga.horizontalHeader().setFont(font)
            self.__userProfileDialog.tableKeluarga.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.__userProfileDialog.tableKeluarga.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            self.__userProfileDialog.tableKeluarga.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            self.__userProfileDialog.tableKeluarga.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

            self.__userProfileDialog.tableKeluarga.setRowCount(len(self.__userProfile['keluarga']))
            no = 0
            for row in self.__userProfile['keluarga']:
                self.__userProfileDialog.tableKeluarga.setItem(no, 0, QtWidgets.QTableWidgetItem(row['nik']))
                self.__userProfileDialog.tableKeluarga.setItem(no, 1, QtWidgets.QTableWidgetItem(row['nama_lengkap']))
                self.__userProfileDialog.tableKeluarga.setItem(no, 2, QtWidgets.QTableWidgetItem(row['status_relasi']))
                sbgWali = QtWidgets.QTableWidgetItem(row['sebagai_wali'])
                sbgWali.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                self.__userProfileDialog.tableKeluarga.setItem(no, 3, sbgWali)
                no += 1

        self.__userProfileDialog.exec_()

    def buildTable(self, cari=None):
        response = self.PedatrenApi.getListPerizinan(cari)
        if self.__responseApiHandler(response):
            listPerizinan = json.loads(response.text)
            self.__buildHeaderTable()
            self.__buildRowTable(listPerizinan)

            self.tablePerizinan.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(9, QtWidgets.QHeaderView.Stretch)
            self.tablePerizinan.horizontalHeader().setSectionResizeMode(10, QtWidgets.QHeaderView.ResizeToContents)

            self.statusBar().showMessage(' Data terakhir diperbaharui: ' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )

    def __buildHeaderTable(self):
        headers = ['id_perizinan', 'NIS Santri', 'Nama Lengkap', 'Gender', 'Domisili', 'Lembaga', 'Alasan Izin', 'Bermalam', 'Rombongan', 'Tujuan', 'Status']
        self.tablePerizinan.setColumnCount(len(headers))
        self.tablePerizinan.setHorizontalHeaderLabels(headers)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.tablePerizinan.horizontalHeader().setFont(font)

    def __buildRowTable(self, data):
        no = 0
        self.tablePerizinan.setRowCount(len(data))
        for row in data:
            pemohonIzin = row['pemohon_izin']

            self.tablePerizinan.setItem(no, 0, QtWidgets.QTableWidgetItem(row['id']))
            self.tablePerizinan.setItem(no, 1, QtWidgets.QTableWidgetItem(pemohonIzin['nis_santri']))
            self.tablePerizinan.setItem(no, 2, QtWidgets.QTableWidgetItem(pemohonIzin['nama_lengkap']))

            jenis_kelamin = QtWidgets.QTableWidgetItem(pemohonIzin['jenis_kelamin'])
            jenis_kelamin.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tablePerizinan.setItem(no, 3, jenis_kelamin)

            self.tablePerizinan.setItem(no, 4, QtWidgets.QTableWidgetItem(pemohonIzin['domisili_santri']))
            self.tablePerizinan.setItem(no, 5, QtWidgets.QTableWidgetItem(pemohonIzin['lembaga']))

            self.tablePerizinan.setItem(no, 6, QtWidgets.QTableWidgetItem(row['alasan_izin']))

            self.tablePerizinan.setItem(no, 7, QtWidgets.QTableWidgetItem( row['bermalam'] + ( ' - (' + row['selama'] + ')' if row['bermalam'] == 'Y' else '') ) )
            rombongan = QtWidgets.QTableWidgetItem(row['rombongan'])
            rombongan.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tablePerizinan.setItem(no, 8, rombongan)

            self.tablePerizinan.setItem(no, 9, QtWidgets.QTableWidgetItem(row['kecamatan_tujuan']))

            statusIzin = QtWidgets.QTableWidgetItem(row['status_perizinan'])
            statusIzin.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            font = QtGui.QFont()
            font.setBold(True)
            statusIzin.setFont(font)
            if row['id_status_perizinan'] == 5:
                statusIzin.setForeground(QtGui.QColor.fromRgb(255, 0, 0))
            elif row['id_status_perizinan'] == 4:
                statusIzin.setForeground(QtGui.QColor.fromRgb(140, 140, 140))
            elif row['id_status_perizinan'] == 3:
                statusIzin.setForeground(QtGui.QColor.fromRgb(0, 170, 0))
            self.tablePerizinan.setItem(no, 10, statusIzin)

            no += 1

        self.tablePerizinan.hideColumn(0)

    def refreshOnClicked(self):
        # Preventif dari badai klik tombol refresh yg seakan-akan spt ngeflood request api
        self.buttonRefresh.setEnabled(False)
        QtCore.QTimer.singleShot(10000, lambda: self.buttonRefresh.setDisabled(False))

        self.tablePerizinan.clear()
        self.tablePerizinan.setRowCount(0)
        self.tablePerizinan.setColumnCount(0)
        self.buildTable()
        self.input_qr_code.setFocus()

    def konfirmasiPosOnclicked(self):
        if self.__itemIzin['id_status_perizinan'] == 3:
            response = self.PedatrenApi.setStatusKeluarDariPondok(self.__itemIzin['id_perizinan'])
        elif self.__itemIzin['id_status_perizinan'] == 4 or self.__itemIzin['id_status_perizinan'] == 5:
            response = self.PedatrenApi.setStatusKembaliKePondok(self.__itemIzin['id_perizinan'])
        else:
            notification.showNotif('Status perizinan tidak valid. \nYang bisa input disini yg berstatus, perizinan sudah diacc atau yang kembali ke pondok')
            return

        if self.__responseApiHandler(response):
            self.refreshOnClicked()

        self.__childDialog.close()

    def doubleClickRow(self):
        self.tablePerizinan.showColumn(0)
        selectedIdPerizinan = self.tablePerizinan.selectedItems()[0].text()
        self.tablePerizinan.hideColumn(0)
        self.showIdPerizinan(selectedIdPerizinan)

    def showIdPerizinan(self, id_perizinan):
        response = self.PedatrenApi.getItemPerizinan(id_perizinan)
        if self.__responseApiHandler(response):
            self.__childDialog = fdetailperizinan.Ui_DetailPerizinan()
            self.__childDialog.label_autoconfirminfo.clear()
            self.__childDialog.label_autoconfirminfo.setVisible(False)

            dataPerizinan = json.loads(response.text)

            pemohonIzin = dataPerizinan['pemohon_izin']

            pengantar = dataPerizinan['pengantar']
            pembuatIzin = dataPerizinan['pembuat_izin']
            persetujuanPengasuh = dataPerizinan['persetujuan_pengasuh']
            persetujuanBiktren = dataPerizinan['persetujuan_biktren']
            pemberitahuanKamtib = dataPerizinan['pemberitahuan_kamtib']

            fotodiri = pemohonIzin['fotodiri']
            fotoPemohonIzin = self.PedatrenApi.getImage(fotodiri['medium'])
            if fotoPemohonIzin.status_code >= 200 and fotoPemohonIzin.status_code < 300:
                pixmap = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(fotoPemohonIzin.content))
                self.__childDialog.label_fotodiri.setPixmap(pixmap.scaled(190, 190, QtCore.Qt.KeepAspectRatio))

            self.__childDialog.label_nama_lengkap.setText(pemohonIzin['nama_lengkap'])
            self.__childDialog.label_nama_lengkap.adjustSize()
            self.__childDialog.label_domisili.setText(pemohonIzin['domisili_santri'])
            self.__childDialog.label_domisili.adjustSize()
            lembaga = pemohonIzin['lembaga'] if pemohonIzin['lembaga'] else '-'
            jurusan = ' - ' + pemohonIzin['jurusan'] if pemohonIzin['jurusan'] else ''
            kelas = ' [' + pemohonIzin['kelas'] + ']' if pemohonIzin['kelas'] else ''
            self.__childDialog.label_lembaga.setText(lembaga+jurusan+kelas)
            self.__childDialog.label_lembaga.adjustSize()
            self.__childDialog.label_alamat.setText(pemohonIzin['alamat'])
            self.__childDialog.label_alamat.adjustSize()

            self.__childDialog.label_alasan_izin.setText(dataPerizinan['alasan_izin'])
            self.__childDialog.label_alasan_izin.adjustSize()
            self.__childDialog.label_tujuan.setText(dataPerizinan['kecamatan_tujuan'])
            self.__childDialog.label_tujuan.adjustSize()
            self.__childDialog.label_lama_izin.setText(dataPerizinan['selama'] + '\nSejak      ' + dataPerizinan['sejak_tanggal'] + '\nSampai   ' + dataPerizinan['sampai_tanggal'])
            self.__childDialog.label_lama_izin.adjustSize()
            self.__childDialog.label_bermalam.setText(dataPerizinan['bermalam'])
            self.__childDialog.label_rombongan.setText(dataPerizinan['rombongan'])

            id_status_perizinan = int(dataPerizinan['id_status_perizinan'])
            if id_status_perizinan == 5:
                self.__childDialog.label_status_perizinan.setStyleSheet('QLabel { color: rgb(255, 0, 0); font-weight: bold}')
                self.__childDialog.buttonKonfirmasiPos.setStyleSheet('QPushButton{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 #5cc151, stop: 1 #28a745); border: 1px solid #39892f; border-radius: 10px; color: white; font-weight: bold;} QPushButton:hover{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 rgba(92, 193, 81, 0.9), stop: 1 rgba(40, 167, 69, 0.9))} QPushButton:pressed {background-color: rgb(40, 167, 69)}')
                self.__childDialog.buttonKonfirmasiPos.setText('Konfirmasi\n \nKembali \nke Pondok')
            elif id_status_perizinan == 4:
                self.__childDialog.label_status_perizinan.setStyleSheet('QLabel { color: rgb(140, 140, 140); font-weight: bold}')
                self.__childDialog.buttonKonfirmasiPos.setStyleSheet('QPushButton{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 #5cc151, stop: 1 #28a745); border: 1px solid #39892f; border-radius: 10px; color: white; font-weight: bold;} QPushButton:hover{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 rgba(92, 193, 81, 0.9), stop: 1 rgba(40, 167, 69, 0.9))} QPushButton:pressed {background-color: rgb(40, 167, 69)}')
                self.__childDialog.buttonKonfirmasiPos.setText('Konfirmasi\n \nKembali \nke Pondok')
            elif id_status_perizinan == 3:
                self.__childDialog.label_status_perizinan.setStyleSheet('QLabel { color: rgb(0, 170, 0); font-weight: bold}')
                self.__childDialog.buttonKonfirmasiPos.setStyleSheet('QPushButton{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 #008eff, stop: 1 #0078d7); border: 1px solid #007bff; border-radius: 10px; color: white; font-weight: bold;} QPushButton:hover{background-color: qlineargradient(x1: 0,y1: 0,x2: 0,y2: 1,stop: 0 rgba(0, 142, 255, 0.9), stop: 1 rgba(0, 120, 215, 0.9))} QPushButton:pressed {background-color: rgb(0, 120, 215)}')
                self.__childDialog.buttonKonfirmasiPos.setText('Konfirmasi\n \nIzin Keluar \nPondok')

            self.__childDialog.label_status_perizinan.setText(dataPerizinan['status_perizinan'])

            self.__itemIzin = {'id_status_perizinan': id_status_perizinan, 'id_perizinan': id_perizinan}
            self.__childDialog.buttonKonfirmasiPos.clicked.connect(self.konfirmasiPosOnclicked)

            if dataPerizinan['tanggal_kembali'] and id_status_perizinan >= 4:
                self.__childDialog.label_tanggal_kembali_info.setText(dataPerizinan['tanggal_kembali'])
            else:
                self.__childDialog.label_tanggal_kembali_info.setText('Belum kembali')
                self.__childDialog.label_tanggal_kembali_info.setStyleSheet('QLabel { color : rgb(140, 140, 140);}')

            self.__childDialog.label_pengantar.setText(pengantar['nama_lengkap'] if pengantar['nama_lengkap'] else '-')
            self.__childDialog.label_pengantar.adjustSize()
            self.__childDialog.label_pembuat_izin.setText(pembuatIzin['nama_lengkap'] if pembuatIzin['nama_lengkap'] else '-')
            self.__childDialog.label_pembuat_izin.adjustSize()
            self.__childDialog.label_biktren.setText(persetujuanBiktren['nama_lengkap'] if persetujuanBiktren['nama_lengkap'] else '-')
            self.__childDialog.label_biktren.adjustSize()
            self.__childDialog.label_pengasuh.setText(persetujuanPengasuh['nama_lengkap'] if persetujuanPengasuh['nama_lengkap'] else '-')
            self.__childDialog.label_pengasuh.adjustSize()
            self.__childDialog.label_kamtib.setText(pemberitahuanKamtib['nama_lengkap'] if pemberitahuanKamtib['nama_lengkap'] else '-')
            self.__childDialog.label_kamtib.adjustSize()

            if self.menu_AutoConfirm.isChecked() == True:
                self.__childDialog.buttonKonfirmasiPos.setVisible(False)

                timerClose = QtCore.QTimer(self.__childDialog)
                timerClose.setSingleShot(True)
                timerClose.timeout.connect(self.__childDialog.close)
                timerClose.start(5000)

                if self.__isAutoConfirmOK == True:
                    self.__childDialog.label_autoconfirminfo.setVisible(True)
                    pixmapCheckbox = QtGui.QPixmap.fromImage(QtGui.QImage( os.path.join(self.__basePath, 'img/checkbox.png') ))
                    self.__childDialog.label_autoconfirminfo.setPixmap(pixmapCheckbox.scaled(100, 100, QtCore.Qt.KeepAspectRatio))
                    self.__isAutoConfirmOK = False

            self.__childDialog.exec_()

    def readInputQrCode(self):
        textqrcode = self.input_qr_code.text().strip()
        self.input_qr_code.clear()
        if not textqrcode or textqrcode == '':
            notification.showNotif('Input QR Code tidak boleh kosong', True)
            return
        try:
            decoded64 = base64.b64decode(textqrcode)
            resJson = json.loads(decoded64)
            id_perizinan = resJson['id_perizinan_santri']
        except:
            notification.showNotif('Input QR Code bukan jenis QR Code Perizinan atau bukan dari Pedatren', True)
            return

        if self.menu_AutoConfirm.isChecked() == True:
            self.__isAutoConfirmOK = self.autoConfim(id_perizinan)
            if self.__isAutoConfirmOK == False:
                return

        self.showIdPerizinan(id_perizinan)

    def autoConfim(self, id_perizinan):
        response = self.PedatrenApi.getItemPerizinan(id_perizinan)
        if self.__responseApiHandler(response, True):
            itemPerizinan = json.loads(response.text)
            if itemPerizinan['id_status_perizinan'] == 3:
                resKeluar = self.PedatrenApi.setStatusKeluarDariPondok(id_perizinan)
                self.__responseApiHandler(resKeluar, True)

            elif itemPerizinan['id_status_perizinan'] == 4 or itemPerizinan['id_status_perizinan'] == 5:
                resKembali = self.PedatrenApi.setStatusKembaliKePondok(id_perizinan)
                self.__responseApiHandler(resKembali, True)

            else:
                notification.showNotif('Status perizinan tidak valid. \nYang bisa diproses adalah perizinan yg berstatus sudah disetujui (di-acc) atau yang kembali ke pondok', True)
                return False

        self.refreshOnClicked()
        return True

    def cari(self):
        strCari = self.input_cari.text().strip()
        self.input_cari.clear()
        self.buildTable(strCari)

    def eventFilter(self, source, event):
        if source is self.tablePerizinan:
            if event.type() == QtCore.QEvent.FocusOut or event.type() == QtCore.QEvent.FocusIn:
                self.input_qr_code.setFocus()
                self.tablePerizinan.setStyleSheet('QTableView{ selection-background-color: rgba(0, 120, 215, 255); selection-color: rgb(255, 255, 255); }')
        elif source is self.input_qr_code:
            if event.type() == QtCore.QEvent.FocusIn:
                self.input_qr_code.setStyleSheet('QLineEdit { background : url("'+self.__iconReadingQrPath+'") center no-repeat; }')
            elif event.type() == QtCore.QEvent.FocusOut:
                self.input_qr_code.setStyleSheet('')
        elif source is self:
            if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.FocusIn:
                self.input_qr_code.setFocus()

        return super(Ui_TablePerizinan, self).eventFilter(source, event)

    def logoutOnClicked(self):
        close = QtWidgets.QMessageBox.question(self, 'Konfirmasi', 'Yakin akan logout? \nSelanjutnya akan diminta untuk login', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            self.PedatrenApi.logout()
            self.close()
            self.switch_window.emit()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_F11:
            if self.isFullScreen() == False:
                self.__lastWindowState = self.windowState()
                self.showFullScreen()
            else:
                self.setWindowState(self.__lastWindowState)

    def show(self):
        super(Ui_TablePerizinan, self).show()
        self.__getProfileUser()
        self.buildTable()