import sys
from requests.exceptions import HTTPError, ConnectionError
from .identity_manager import IdManager
from .server_interface import Server


SERVER_HOST = 'localhost'
SERVER_PORT = 5000


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
            return build_result(True, "Found {} identities: {}".format(len(id_list), '\n'.join(id_list)))

        elif cmd == 'id.delete':
            check_opt_count(1)
            id = opts[0]
            id_manager = IdManager()
            id_manager.delete(id)
            return build_result(True, "Id '{}' removed".format(id))

        elif cmd == 'server.register':
            check_opt_count(1)
            id = opts[0]
            id_manager = IdManager()
            private_key = id_manager.get_key(id)
            server = Server(SERVER_HOST, SERVER_PORT)
            request_id = server.register(id, private_key)
            return build_result(True, "Registration request for id '{}' was accepted by the server [{}]".format(id, request_id))

        elif cmd == 'server.publish':
            check_opt_count(2)
            id = opts[0]
            id_manager = IdManager()
            private_key = id_manager.get_key(id)

            message = opts[1]
            server = Server(SERVER_HOST, SERVER_PORT)
            request_id = server.publish(id, private_key, message)
            return build_result(True, "Publication request for id '{}' was accepted by the server [{}]".format(id, request_id))

        else:
            return build_result(True, "Unrecognised command: '{}'".format(cmd))

    except HTTPError as e:
        return build_result(False, 'Server rejected the request - {}'.format(e))

    except ConnectionError as e:
        return build_result(False, 'Unable to connect to the http server {}:{} - {}'.format(SERVER_HOST, SERVER_PORT, e))

    except Exception as e:
        return build_result(False, str(e))


def show_usage():
    print('usage')


def process_args(args):
    if len(args) == 1:
        show_usage()
    else:
        result = process_command(args[1], args[2:])
        print(("SUCCESS" if result['ok'] else "ERROR") + ": " + result['message'])


if __name__ == '__main__':
    try:
        process_args(sys.argv)
    except ValueError as e:
        print(str(e))
