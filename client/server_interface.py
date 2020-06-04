import requests
import base64
import time
from cryptography.hazmat.primitives import serialization
from common.crypto_utils import sign_data_with_key
from requests.exceptions import HTTPError
from common.logging import log, LogLevel
from urllib.parse import quote

ENCODING = 'utf-8'


class ServerInterface:
    post_interceptor = None

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def register(self, client_id, private_key):
        return self._sign_and_post_and_wait(client_id, private_key, 'register', {
            'publicKey': private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(ENCODING)
        })

    def publish(self, client_id, private_key, message):
        return self._sign_and_post_and_wait(client_id, private_key, 'publish', {
            'message': message
        })

    def query_messages(self, key_value_pairs):
        return self._get('query?{}'.format('&'.join(map(lambda p: '{}={}'.format(quote(p[0]), quote(p[1])), key_value_pairs))))

    def _query_status(self, request_id):
        return self._get('status/{}'.format(request_id))

    def _sign_and_post_and_wait(self, client_id, private_key, url_path, data):
        request_id = self._sign_and_post(client_id, private_key, url_path, data)
        while True:
            time.sleep(1)
            log(LogLevel.DEBUG, 'Polling server...')
            status = self._query_status(request_id)
            if status != 'PENDING':
                return status

    def _sign_and_post(self, client_id, private_key, url_path, data):
        signature = sign_data_with_key(data, private_key)
        body = {
            'clientId': client_id,
            'signature': base64.standard_b64encode(signature).decode(ENCODING),
            'data': data
        }

        return self._post(url_path, body)

    def _post(self, url_path, body):
        body = self._apply_post_interceptor(body)
        response = requests.post("http://{}:{}/api/{}".format(self.host, self.port, url_path), json=body)
        if response.status_code == requests.codes.accepted:
            return response.json()['requestId']
        else:
            raise HTTPError(response.json()['error'])

    def _get(self, url_path):
        response = requests.get("http://{}:{}/api/{}".format(self.host, self.port, url_path))
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise HTTPError(response.json())

    def _apply_post_interceptor(self, json_body):
        return ServerInterface.post_interceptor(json_body) if ServerInterface.post_interceptor else json_body
