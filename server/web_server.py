from bottle import Bottle, ServerAdapter, request
import uuid, json
from .exception import InvalidRequest

from common.logging import log, LogLevel
from wsgiref.simple_server import make_server


class Adapter(ServerAdapter):
    def __init__ (self, host, port):
        self.server = None
        self.host = host
        self.port = port
        self.options = {}

    def run(self, handler):
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


class WebServer:
    def __init__(self, host, port, work_queue):
        self.server_adapter = Adapter(host, port)
        self._app = Bottle()
        self.work_queue = work_queue
        self._set_routes()

    def start(self):
        self._app.run(server=self.server_adapter)

    def stop(self):
        self.server_adapter.server.shutdown()

    def _set_routes(self):
        self._app.route('/api/register', method="POST", callback=self._register)
        self._app.route('/api/publish', method="POST", callback=self._publish)
        self._app.route('/api/status/<request_id>', method="GET", callback=self._status)

    def _register(self):
        request_body = request.json
        client_id = self._get_request_value(request_body, 'clientId')
        signature = self._get_request_value(request_body, 'signature')
        data = self._get_request_value(request_body, 'data')
        request_id = str(uuid.uuid4())

        work_item = {
            'type': 'registration',
            'requestId': request_id,
            'clientId': client_id,
            'signature': signature,
            'publicKey': data['publicKey'],
            'data': data
        }

        self.work_queue.add(work_item)
        return json.dumps({'requestId': request_id}), 202

    def _publish(self):
        request_body = request.json
        client_id = self._get_request_value(request_body, 'clientId')
        signature = self._get_request_value(request_body, 'signature')
        data = self._get_request_value(request_body, 'data')
        request_id = str(uuid.uuid4())

        work_item = {
            'type': 'publication',
            'requestId': request_id,
            'clientId': client_id,
            'signature': signature,
            'data': data
        }

        self.work_queue.add(work_item)

        return json.dumps({'requestId': request_id}), 202

    def _status(self, request_id):
        request_status = self.work_queue.query(request_id)

        return json.dumps({'requestId': request_id, 'status': request_status.name}), 200

    def _get_request_value(self, request, key):
        if key in request:
            return request[key]
        raise InvalidRequest("Key '{}' missing from request".format(key))

# @app.after_request
# def after_request_func(response):
#     log(LogLevel.DEBUG, '"{} {}" {}'.format(request.method, request.path, response.status_code))
#     return response
#








# @app.errorhandler(InvalidRequest)
# def handle_invalid_request(e):
#     return jsonify({'error': str(e)}), 400


