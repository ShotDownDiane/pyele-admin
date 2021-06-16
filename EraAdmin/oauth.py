import base64
import requests
from EraAdmin import utools
from EraAdmin.app import AppConfig


class OAuth:
    client_id = None
    client_secret = None
    # oauth授权中心地址
    authEndpoint = 'http://localhost:8080'

    # 'http://127.0.0.1:8100'

    def __init__(self, config: AppConfig, authEndpoint=None):
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        if authEndpoint:
            self.authEndpoint = authEndpoint

    def get_auth_uri(self, redirect_uri="", state=None, scope='read'):
        uri = self.authEndpoint + '/oauth/authorize?state=%s&client_id=%s&response_type=code&redirect_uri=%s&scope=%s' % (
            state, self.client_id, redirect_uri, scope)
        return uri

    def get_token(self, code) -> dict:
        data = str("grant_type=authorization_code&code=" + code).replace("+", "%2B").encode("utf-8")
        u = self.client_id + ":" + self.client_secret
        u = str(base64.b64encode(u.encode('utf-8')), "utf-8")
        r = requests.session().post(self.authEndpoint + "/oauth/token/",
                                    headers={"Content-Type": "application/x-www-form-urlencoded",
                                             'Authorization': 'Basic ' + u}, data=data)
        result = utools.json_decode(r.content)
        return result

    def revoke_token(self):
        pass
