import requests, json, base64
from config import CONFIG


class Pedatren:
    Request = None
    __singleton = None
    __baseUrl = ''
    __headers = {
        'content-type' : 'application/json',
        'connection' : 'keep-alive',
        'User-Agent' : CONFIG.get('User-Agent')
    }
    __filetoken = 'token.tmp'
    credentials = None

    def __new__(cls, *args, **kwargs):
        if not cls.__singleton:
            cls.__singleton = super(Pedatren, cls).__new__(cls, *args, **kwargs)
        return cls.__singleton

    def __init__(self):
        self.Request = requests.Session()
        self.Request.headers.update(self.__headers)
        self.__baseUrl = CONFIG.get('BASE_API_URL')

        try:
            open(self.__filetoken, 'r')
        except IOError:
            open(self.__filetoken, 'w')

        with open(self.__filetoken, 'r') as f:
            token = f.read()
            if token:
                self.Request.headers.update({'x-token': token})
                jwtPayload = token.split('.')[0]
                jwtPayload += "=" * ((4 - len(jwtPayload) % 4) % 4)
                self.credentials = json.loads(base64.b64decode(jwtPayload))

    def __responseHandler(self, response):
        if response.status_code == 401:
            self.Request.headers.pop('x-token', None)
            self.credentials = None

            with open(self.__filetoken, 'w') as f:
                f.write('')

        return response

    def __get(self, url, query={}):
        try:
            response = self.Request.get(url, params=query)
            return self.__responseHandler(response)

        except requests.exceptions.ConnectionError:
            return {'exception': 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout koneksi.\n- Server Pedatren sedang down.'}
        except Exception as e:
            return {'exception': str(e)}

    def __post(self, url, dataPost={}):
        try:
            response = self.Request.post(url, data=json.dumps(dataPost))
            return self.__responseHandler(response)

        except requests.exceptions.ConnectionError:
            return {'exception': 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout koneksi.\n- Server Pedatren sedang down.'}
        except Exception as e:
            return {'exception': str(e)}

    def __put(self, url, dataPost={}):
        try:
            response = self.Request.put(url, data=json.dumps(dataPost))
            return self.__responseHandler(response)

        except requests.exceptions.ConnectionError:
            return {'exception': 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout koneksi.\n- Server Pedatren sedang down.'}
        except Exception as e:
            return {'exception': str(e)}

    def __delete(self, url):
        try:
            response = self.Request.delete(url)
            return self.__responseHandler(response)

        except requests.exceptions.ConnectionError:
            return {'exception': 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout koneksi.\n- Server Pedatren sedang down.'}
        except Exception as e:
            return {'exception': str(e)}

    def login(self, username=None, password=None):
        try:
            response = self.Request.get(self.__baseUrl + '/auth/login', auth=(username,password))
            response.raise_for_status()

            token = response.headers.get('x-token')
            self.Request.headers.update({'x-token': token})

            jwtPayload = token.split('.')[0]
            jwtPayload += "=" * ((4 - len(jwtPayload) % 4) % 4)
            self.credentials = json.loads(base64.b64decode(jwtPayload))

            with open(self.__filetoken, 'w') as f:
                f.write(token)

            return True

        except:
            self.Request.headers.pop('x-token', None)
            self.credentials = None

        return response

    def logout(self):
        with open(self.__filetoken, 'w') as f:
            f.write('')

        try:
            self.Request.get(self.__baseUrl + '/auth/logout')
        except:
            pass

    def getListPerizinan(self, cari=None):
        return self.__get(self.__baseUrl + '/penjagapos/perizinan/santri', cari)

    def getItemPerizinan(self, id_perizinan):
        return self.__get(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan)

    def setStatusKeluarDariPondok(self, id_perizinan):
        return self.__put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/pemberitahuan', {'diketahui': 'Y'})

    def setStatusKembaliKePondok(self, id_perizinan):
        return self.__put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/statuskembali', {'kembali': 'Y'})

    def getImage(self, relative_path):
        return self.__get(self.__baseUrl + relative_path)

    def getUserProfile(self):
        return self.__get(self.__baseUrl + '/person/' + str(self.credentials['uuid_person']))
