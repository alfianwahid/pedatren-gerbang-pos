import sys, os, requests, json, base64
from tempfile import gettempdir
from config import CONFIG


class PedatrenApi:
    __instance = None

    class __PedatrenApiSingleton:
        Request = None
        __baseUrl = ''
        __headers = {
            'content-type' : 'application/json',
            'connection' : 'keep-alive',
            'User-Agent' : CONFIG.get('User-Agent')
        }
        __filetoken = 'tokenpedatrengerbangpos.tmp'
        credentials = None
        __prefixScope = None


        def __init__(self):
            self.Request = requests.Session()
            self.Request.headers.update(self.__headers)
            self.__baseUrl = CONFIG.get('BASE_API_URL')

            if getattr(sys, 'frozen', False):
                application_path = gettempdir()
            elif __file__:
                application_path = os.path.dirname(os.path.abspath(__file__))

            self.__filetoken = os.path.join(application_path, self.__filetoken)

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
                    self.__initPrefixScope(self.credentials.get('scope'))

        def __initPrefixScope(self, scope):
                if 'sysadmin' in scope or 'admin' in scope or 'supervisor' in scope or 'keuangan' in scope or 'kepegawaian' in scope:
                    self.__prefixScope = ''
                elif 'biktren-putra' in scope:
                    self.__prefixScope = '/biktren-putra'
                elif 'biktren-putri' in scope:
                    self.__prefixScope = '/biktren-putri'
                else:
                    for x in scope:
                        split = x.split('-', 1)
                        if len(split) == 2:
                            if 'lembaga' in split:
                                self.__prefixScope = '/lembaga/' + split[1]
                                break
                            elif 'wilayah' in split:
                                self.__prefixScope = '/wilayah/' + split[1]
                                break


        def __responseHandler(self, response):
            if response.status_code == 401:
                self.Request.headers.pop('x-token', None)
                self.credentials = None
                self.__prefixScope = None

                with open(self.__filetoken, 'w') as f:
                    f.write('')

            return response

        def __get(self, url, query={}):
            try:
                response = self.Request.get(url, params=query)
                return self.__responseHandler(response)

            except requests.exceptions.ConnectionError:
                return {'exception': 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout. Coba ulangi lagi!\n- Server Pedatren sedang down.'}
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

                self.__initPrefixScope(self.credentials.get('scope'))

                with open(self.__filetoken, 'w') as f:
                    f.write(token)

                return True

            except requests.exceptions.ConnectionError:
                return 'Terjadi kegagalan koneksi ke server API Pedatren. Bisa jadi dikarenakan : \n- Tidak ada jaringan, coba periksa koneksi jaringan wifi/lan anda.\n- Jaringan terlalu lambat sehingga terjadi timeout. Coba ulangi lagi!\n- Server Pedatren sedang down.'

            except:
                self.Request.headers.pop('x-token', None)
                self.credentials = None
                return 'Invalid Login'

        def logout(self):
            with open(self.__filetoken, 'w') as f:
                f.write('')

            try:
                self.Request.get(self.__baseUrl + '/auth/logout')
            except:
                pass

            self.Request.headers.pop('x-token', None)
            self.credentials = None
            self.__prefixScope = None


        def getImage(self, relative_path):
            return self.__get(self.__baseUrl + relative_path)

        def getUserProfile(self):
            return self.__get(self.__baseUrl + '/person/' + str(self.credentials['uuid_person']))

        def getListPerizinan(self, cari=None):
            return self.__get(self.__baseUrl + '/penjagapos/perizinan/santri', cari)

        def getItemPerizinan(self, id_perizinan):
            return self.__get(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan)

        def setStatusKeluarDariPondok(self, id_perizinan):
            return self.__put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/pemberitahuan', {'diketahui': 'Y'})

        def setStatusKembaliKePondok(self, id_perizinan):
            return self.__put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/statuskembali', {'kembali': 'Y'})


    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = PedatrenApi.__PedatrenApiSingleton()
        return cls.__instance

    def __getattr__(self, name):
        return getattr(self.__instance, name)
