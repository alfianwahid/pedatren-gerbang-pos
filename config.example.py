import platform

CONFIG = {
    'BASE_API_URL': 'http://127.0.0.1:3000/api/v1',
    'User-Agent': 'DesktopApp/1.0.0 Pos Gerbang (' + platform.system() + '; ' + platform.node() + '; ' + platform.machine() + '; ' + platform.processor() + ')'
}