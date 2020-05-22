from flask import Flask, request, jsonify
import uuid
from queue import Queue
from .request_processor import RequestProcessor

app = Flask(__name__)

work_queue = Queue()
processor = RequestProcessor(work_queue)


@app.before_first_request
def start_up():
    processor.start()


@app.route('/api/register', methods=['POST'])
def register():
    request_body = request.get_json()
    print(request_body)
    client_id = request_body.get('clientId')
    signature = request_body.get('signature')
    data = request_body.get('data')
    request_id = str(uuid.uuid4())

    work_item = {
        'type': 'registration',
        'requestId': request_id,
        'clientId': client_id,
        'signature': signature,
        'data': data
    }

    work_queue.put(work_item, block=False)
    # signature_valid = verify_signature(data, signature, public_key)
    # print(signature_valid)

    # meta_data = request_body.get('metaData', {})
    # service.register(public_key, meta_data)
    return jsonify({'requestId': request_id}), 202



