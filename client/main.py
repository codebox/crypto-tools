import sys, json
from requests.exceptions import HTTPError, ConnectionError

from client.client_cache import PublicKeyCache
from common.crypto_utils import verify_signature
from .identity_manager import IdManager
from .server_interface import ServerInterface
from common.logging import log, LogLevel

SERVER_HOST = 'localhost'
SERVER_PORT = 5000


def get_public_key_for_id(id):
    cache = PublicKeyCache()
    if not cache.get(id):
        server = ServerInterface(SERVER_HOST, SERVER_PORT)
        id_details = server.query_messages([('type', 'registration'), ('clientId', id)])
        if not id_details:
            raise ValueError('No id {} was found on the server'.format(id))
        if not verify_signature(id_details[0]['data'], id_details[0]['signature'], id_details[0]['publicKey']):
            raise ValueError('Invalid signature in registration details for {}'.format(id))
        cache.add(id, id_details[0]['publicKey'])

    return cache.get(id)

def message_signature_ok(msg):
    public_key = get_public_key_for_id(msg['clientId'])
    return verify_signature(msg['data'], msg['signature'], public_key)

def process_command(cmd, opts):
    def check_opt_count(expected_opt_count):
        if len(opts) != expected_opt_count:
            raise ValueError('Wrong number of arguments for command "{}", expected {} but found {}'.format(cmd, expected_opt_count, len(opts)))

    def build_result(ok, msg):
        return {'ok': ok, 'message': msg}

    try:
        if cmd == 'id.create':
            check_opt_count(1)
            id = opts[0]
            id_manager = IdManager()
            id_manager.create(id)
            return build_result(True, "New id '{}' created".format(id))

        elif cmd == 'id.list':
            check_opt_count(0)
            id_manager = IdManager()
            id_list = list(id_manager.list())
            return build_result(True, "Found {} identities\n{}".format(len(id_list), '\n'.join(map(lambda s: '- ' + s, id_list))))

        elif cmd == 'id.delete':
            check_opt_count(1)
            id = opts[0]
            id_manager = IdManager()
            if id_manager.delete(id):
                return build_result(True, "Id '{}' removed".format(id))
            else:
                return build_result(False, "Id '{}' not removed".format(id))

        elif cmd == 'server.register':
            check_opt_count(1)
            id = opts[0]
            id_manager = IdManager()
            private_key = id_manager.get_key(id)
            server = ServerInterface(SERVER_HOST, SERVER_PORT)
            result = server.register(id, private_key)
            return build_result(True, "Registration request for id '{}' was accepted by the server [{}]".format(id, result['requestId']))

        elif cmd == 'server.publish':
            check_opt_count(2)
            id = opts[0]
            id_manager = IdManager()
            private_key = id_manager.get_key(id)

            message = opts[1]
            server = ServerInterface(SERVER_HOST, SERVER_PORT)
            result = server.publish(id, private_key, message)
            return build_result(True, "Publication request for id '{}' was accepted by the server [{}]".format(id, result['requestId']))

        elif cmd == 'server.status':
            check_opt_count(1)
            request_id = opts[0]
            server = ServerInterface(SERVER_HOST, SERVER_PORT)
            status = server.query_status(request_id)
            return build_result(True, "Status of request '{}' was {}".format(request_id, status))

        elif cmd == 'server.query':
            server = ServerInterface(SERVER_HOST, SERVER_PORT)
            key_value_pairs = [pair.split('=') for pair in opts]
            matches = [msg for msg in server.query_messages(key_value_pairs) if message_signature_ok(msg)]

            return build_result(True, '\n'.join(['{} matches found'.format(len(matches))] + [format_message(msg) for msg in matches]))

        else:
            return build_result(True, "Unrecognised command: '{}'".format(cmd))

    except HTTPError as e:
        return build_result(False, 'Server rejected the request - {}'.format(e))

    except ConnectionError as e:
        return build_result(False, 'Unable to connect to the http server {}:{} - {}'.format(SERVER_HOST, SERVER_PORT, e))

    except Exception as e:
        return build_result(False, str(e))

def format_message(msg):
    if msg['type'] == 'publication':
        return '[{}]: {}'.format(msg['clientId'], msg['data']['message'])
    elif msg['type'] == 'registration':
        return 'Registration for [{}]'.format(msg['clientId'])
    else:
        return json.dumps(msg, indent=4)

def show_usage():
    print('usage')


def process_args(args):
    if len(args) == 1:
        show_usage()
    else:
        result = process_command(args[1], args[2:])
        if result['ok']:
            log(LogLevel.INFO, result['message'])
        else:
            log(LogLevel.ERROR, result['message'])


if __name__ == '__main__':
    try:
        process_args(sys.argv)
    except ValueError as e:
        log(LogLevel.ERROR, str(e))
