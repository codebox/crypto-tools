from flask import Flask, request, jsonify
import uuid
from queue import Queue
from .request_processor import RequestProcessor
from .exception import InvalidRequest
from common.logging import log, LogLevel
import logging

app = Flask(__name__)

work_queue = Queue()
processor = RequestProcessor(work_queue)

LogLevel.currentLevel = LogLevel.DEBUG

flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.ERROR)

@app.before_first_request
def start_up():
    processor.start()

@app.after_request
def after_request_func(response):
    log(LogLevel.DEBUG, '"{} {}" {}'.format(request.method, request.path, response.status_code))
    return response

@app.route('/api/register', methods=['POST'])
def register():
    request_body = request.get_json()
    # print(request_body)
    client_id = get_request_value(request_body, 'clientId')
    signature = get_request_value(request_body, 'signature')
    data = get_request_value(request_body, 'data')
    request_id = str(uuid.uuid4())

    work_item = {
        'type': 'registration',
        'requestId': request_id,
        'clientId': client_id,
        'signature': signature,
        'publicKey': data['publicKey'],
        'data': data
    }

    work_queue.put(work_item, block=False)
    # signature_valid = verify_signature(data, signature, public_key)
    # print(signature_valid)

    # meta_data = request_body.get('metaData', {})
    # service.register(public_key, meta_data)
    return jsonify({'requestId': request_id}), 202

@app.route('/api/publish', methods=['POST'])
def publish():
    request_body = request.get_json()
    # print(request_body)
    client_id = get_request_value(request_body, 'clientId')
    signature = get_request_value(request_body, 'signature')
    data = get_request_value(request_body, 'data')
    request_id = str(uuid.uuid4())

    work_item = {
        'type': 'publication',
        'requestId': request_id,
        'clientId': client_id,
        'signature': signature,
        'publicKey': None,
        'data': data
    }

    work_queue.put(work_item, block=False)

    return jsonify({'requestId': request_id}), 202

@app.errorhandler(InvalidRequest)
def handle_invalid_request(e):
    return jsonify({'error': str(e)}), 400


def get_request_value(request, key):
    if key in request:
        return request[key]
    raise InvalidRequest("Key '{}' missing from request".format(key))
