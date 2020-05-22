import json, base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

ENCODING='utf-8'


def sign_data_with_key(data, key):
    text = __dict_to_json(data)
    return key.sign(
        data=text.encode(ENCODING),
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )


def verify_signature(data, signature, public_key):
    if isinstance(public_key, str):
        public_key = parse_public_key(public_key)

    if isinstance(signature, str):
        signature = parse_signature(signature)

    text = __dict_to_json(data)
    try:
        public_key.verify(
            signature=signature,
            data=text.encode(ENCODING),
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        return True

    except InvalidSignature:
        return False

def parse_public_key(public_key_string):
    return load_pem_public_key(public_key_string.encode(ENCODING), backend=default_backend())

def parse_signature(signature_string):
    return base64.standard_b64decode(signature_string)


def __dict_to_json(dict):
    return json.dumps(dict, sort_keys=True)
