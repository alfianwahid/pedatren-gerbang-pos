import requests, json, base64
from config import CONFIG


def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class Pedatren:
    __instance = None
    __baseUrl = ''
    __headers = {
        'content-type' : 'application/json',
        'connection' : 'keep-alive',
        'User-Agent' : CONFIG.get('User-Agent')
    }
    __token = ''
    credentials = None
    __filetoken = 'token.tmp'

    def __init__(self):
        try:
            open(self.__filetoken, 'r')
        except IOError:
            open(self.__filetoken, 'w')

        with open('token.tmp', 'r') as f:
            token = f.read()
            if token:
                self.__token = token
                self.__headers['x-token'] = token
                jwtPayload = token.split('.')[0]
                jwtPayload += "=" * ((4 - len(jwtPayload) % 4) % 4)
                self.credentials = json.loads(base64.b64decode(jwtPayload))

        self.__baseUrl = CONFIG.get('BASE_API_URL')

    def getToken(self):
        return self.__token

    def getHeaders(self):
        return self.__headers

    def login(self, username=None, password=None):
        # saat login jika dengan self.__headers yg sudah ada token, maka akan selalu ok dan adalah user di token, bukan dari user & pass yg dikirim
        freshHeaders = {
            'content-type' : 'application/json',
            'connection' : 'keep-alive',
            'User-Agent' : CONFIG.get('User-Agent')
        }

        response = requests.get(self.__baseUrl + '/auth/login', headers=freshHeaders, auth=(username,password))

        if response.status_code >= 200 and response.status_code < 300:
            self.__token = response.headers['x-token']
            self.__headers['x-token'] = response.headers['x-token']
            jwtPayload = response.headers['x-token'].split('.')[0]
            jwtPayload += "=" * ((4 - len(jwtPayload) % 4) % 4)
            self.credentials = json.loads(base64.b64decode(jwtPayload))

            with open('token.tmp', 'w') as f:
                f.write(self.__token)

        else:
            self.__token = ''
            self.__headers.pop('x-token', None)

        return response

    def logout(self):
        response = requests.get(self.__baseUrl + '/auth/logout', headers=self.__headers)

        with open('token.tmp', 'w') as f:
            f.write('')

        return response

    def getListPerizinan(self, cari=None):
        queryUrl = {}
        if cari:
            queryUrl = {'cari':cari}
        response = requests.get(self.__baseUrl + '/penjagapos/perizinan/santri', headers=self.__headers, params=queryUrl)
        return response

    def getItemPerizinan(self, id_perizinan):
        response = requests.get(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan, headers=self.__headers)
        return response

    def setStatusKeluarDariPondok(self, id_perizinan):
        response = requests.put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/pemberitahuan', headers=self.__headers, data=json.dumps({'diketahui': 'Y'}))
        return response

    def setStatusKembaliKePondok(self, id_perizinan):
        response = requests.put(self.__baseUrl + '/penjagapos/perizinan/santri/' + id_perizinan + '/statuskembali', headers=self.__headers, data=json.dumps({'kembali': 'Y'}))
        return response

    def getImage(self, relative_path):
        response = requests.get(self.__baseUrl + relative_path, headers=self.__headers)
        return response

    def getUserProfile(self):
        response = requests.get(self.__baseUrl + '/person/' + str(self.credentials['uuid_person']), headers=self.__headers)
        return response
