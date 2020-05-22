from flask import Flask, request, jsonify, abort, Response
import uuid
from common.crypto_utils import verify_signature

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    request_body = request.get_json()
    print(request_body)
    client_id = request_body.get('clientId')
    signature = request_body.get('signature')
    data = request_body.get('data')
    public_key = data['publicKey']

    signature_valid = verify_signature(data, signature, public_key)
    print(signature_valid)

    # meta_data = request_body.get('metaData', {})
    # service.register(public_key, meta_data)
    return jsonify({'requestId' : str(uuid.uuid4())}), 202



