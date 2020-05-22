import sys
from .identity_manager import IdManager
from .server_interface import Server


def process_command(cmd, opts):
    def check_opt_count(expected_opt_count):
        if len(opts) != expected_opt_count:
            raise ValueError('Wrong number of arguments for command "{}", expected {} but found {}'.format(cmd, expected_opt_count, len(opts)))

    if cmd == 'id.create':
        check_opt_count(1)
        key_name = opts[0]
        id_manager = IdManager()
        id_manager.create(key_name)

    elif cmd == 'id.list':
        check_opt_count(0)
        id_manager = IdManager()
        print(list(id_manager.list()))

    elif cmd == 'id.delete':
        check_opt_count(1)
        id = opts[0]
        id_manager = IdManager()
        id_manager.delete(id)

    elif cmd == 'server.register':
        check_opt_count(1)
        id = opts[0]
        id_manager = IdManager()
        private_key = id_manager.get_key(id)
        server = Server('localhost', 5000)
        server.register(id, private_key)
        # print(verify_signature("its me", signature, private_key.public_key()))

    else:
        raise ValueError('Unrecognised command: ' + cmd)


def show_usage():
    print('usage')


def process_args(args):
    if len(args) == 1:
        show_usage()
    else:
        process_command(args[1], args[2:])


if __name__ == '__main__':
    try:
        process_args(sys.argv)
    except ValueError as e:
        print(str(e))

