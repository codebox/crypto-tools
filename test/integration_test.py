import unittest, os, glob, re, time, json
from server.main import server_manager

from client.main import process_args
from client.server_interface import ServerInterface
from server.message_store import MessageStore
from common.logging import get_log_messages, clear_log_messages, LogLevel

BACKUP_FILE_EXT = '.bak'
SERVER_FILE = MessageStore.file_path
ID_1 = 'test1'
ID_2 = 'test2'
MSG_1 = 'hello'
MSG_2 = 'where am i?'
BAD_COMMAND = 'lobster.telephone'

def log_info(msg):
    return (LogLevel.INFO, msg)

class IntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        IntegrationTest._backup_client_keys()
        IntegrationTest._backup_server_data()

    def setUp(self):
        clear_log_messages()

    def tearDown(self):
        clear_log_messages()
        self._delete_client_keys()
        self._delete_server_data()
        self._stop_server()
        ServerInterface.post_interceptor = None

    @classmethod
    def tearDownClass(cls):
        IntegrationTest._restore_client_keys()
        IntegrationTest._restore_server_data()

    @classmethod
    def _backup_client_keys(cls):
        for key_file in glob.glob('keys/*.pem'):
            os.rename(key_file, key_file + BACKUP_FILE_EXT)

    @classmethod
    def _backup_server_data(cls):
        if os.path.exists(SERVER_FILE):
            os.rename(SERVER_FILE, SERVER_FILE + BACKUP_FILE_EXT)

    @classmethod
    def _restore_client_keys(cls):
        for key_file in glob.glob('keys/*.pem' + BACKUP_FILE_EXT):
            os.rename(key_file, key_file[:-len(BACKUP_FILE_EXT)])

    @classmethod
    def _restore_server_data(cls):
        if os.path.exists(SERVER_FILE + BACKUP_FILE_EXT):
            os.rename(SERVER_FILE + BACKUP_FILE_EXT, SERVER_FILE)

    def test_unknown_client_command(self):
        self._when_unknown_command()
        self._then_bad_command_message_shown()

    def test_list_keys_when_no_keys_exist(self):
        self._given_no_client_keys_exist()
        self._when_list_ids()
        self._then_no_ids_message_shown()

    def test_list_keys_when_keys_exist(self):
        self._given_keys_exist(ID_1, ID_2)
        clear_log_messages()
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_2, ID_1)

    def test_ids_created(self):
        self._when_create_id(ID_1)
        self._then_id_created_message_shown_for(ID_1)
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_1)
        self._when_create_id(ID_2)
        self._then_id_created_message_shown_for(ID_2)
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_2, ID_1)

    def test_create_duplicate_id(self):
        self._when_create_id(ID_1)
        self._then_id_created_message_shown_for(ID_1)
        self._when_create_id(ID_1)
        self._then_id_already_exists_message_shown_for(ID_1)
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_1)

    def test_delete_id(self):
        self._when_create_id(ID_1)
        self._when_create_id(ID_2)
        self._when_delete_id(ID_1)
        self._then_id_deleted_message_shown_for(ID_1)

    def test_delete_non_existent_id(self):
        self._when_delete_id(ID_1)
        self._then_id_not_deleted_message_shown_for(ID_1)

    def test_register_id_with_server(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._then_id_registered_message_shown_for(ID_1)
        self._then_registration_record_saved_for(ID_1)

    def test_register_id_when_server_down_server(self):
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._then_server_down_message_shown()

    def test_register_non_existent_id_with_server(self):
        self._start_server()
        self._when_register_id(ID_1)
        self._then_id_does_not_exist_message_shown_for(ID_1)
        self._then_registration_record_not_saved_for(ID_1)

    def test_register_duplicate_id_with_server(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._when_register_id(ID_1)
        self._then_id_already_registered_message_shown_for(ID_1)
        self._then_registration_record_saved_for(ID_1)

    def test_register_id_with_bad_signature(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id_with_bad_signature(ID_1)
        self._then_bad_signature_message_shown_for(ID_1)
        self._then_registration_record_not_saved_for(ID_1)

    def test_publishes_message_to_server(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._when_publish_message(ID_1, MSG_1)
        self._then_published_message_shown_for(ID_1)
        self._then_publication_record_saved_for(ID_1, MSG_1)

    def test_publishes_message_with_invalid_signature_to_server(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._when_publish_message_with_bad_signature(ID_1, MSG_1)
        self._then_bad_signature_message_shown_for(ID_1)
        self._then_publication_record_not_saved_for(ID_1, MSG_1)

    def test_query_returns_no_matches(self):
        self._start_server()
        self._when_query_for(('type', 'ographic'))
        self._then_no_matches_found_message_is_shown()

    def test_query_returns_matches(self):
        self._start_server()
        self._when_create_id(ID_1)
        self._when_register_id(ID_1)
        self._when_publish_message(ID_1, MSG_1)
        self._when_publish_message(ID_1, MSG_2)
        self._when_create_id(ID_2)
        self._when_register_id(ID_2)
        self._when_publish_message(ID_2, MSG_1)

        self._when_query_for()
        self._then_matches_found_message_is_shown_for(
            'Registration for [{}]'.format(ID_1),
            '[{}]: {}'.format(ID_1, MSG_1),
            '[{}]: {}'.format(ID_1, MSG_2),
            'Registration for [{}]'.format(ID_2),
            '[{}]: {}'.format(ID_2, MSG_1),
        )

        self._when_query_for(('type', 'registration'))
        self._then_matches_found_message_is_shown_for('Registration for [{}]'.format(ID_1), 'Registration for [{}]'.format(ID_2))

        self._when_query_for(('clientId', ID_1), ('data.message', MSG_1))
        self._then_matches_found_message_is_shown_for('[{}]: {}'.format(ID_1, MSG_1))

    def _start_server(self):
        server_manager.start()

    def _stop_server(self):
        server_manager.stop()

    def _delete_client_keys(self):
        for key_file in glob.glob('keys/*.pem'):
            self._delete_file_if_exists(key_file)

    def _delete_server_data(self):
        self._delete_file_if_exists(SERVER_FILE)

    def _delete_file_if_exists(self, file):
        if os.path.exists(file):
            os.remove(file)

    def _given_no_client_keys_exist(self):
        self._delete_client_keys()

    def _given_keys_exist(self, *keys):
        for key in keys:
            process_args(['', 'id.create', key])

    def _when_unknown_command(self):
        process_args(['', BAD_COMMAND])

    def _when_list_ids(self):
        process_args(['', 'id.list'])

    def _when_create_id(self, id):
        process_args(['', 'id.create', id])

    def _when_delete_id(self, id):
        process_args(['', 'id.delete', id])

    def _when_register_id(self, id):
        process_args(['', 'server.register', id])

    def _when_publish_message(self, id, msg):
        process_args(['', 'server.publish', id, msg])

    def _when_query_for(self, *criteria):
        process_args(['', 'server.query'] + list(map(lambda p: '{}={}'.format(p[0], p[1]), criteria)))

    def _invalidate_signature(self, data):
        data['signature'] = data['signature'].lower()
        return data

    def _when_register_id_with_bad_signature(self, id):
        ServerInterface.post_interceptor = self._invalidate_signature
        self._when_register_id(id)

    def _when_publish_message_with_bad_signature(self, id, msg):
        ServerInterface.post_interceptor = self._invalidate_signature
        self._when_publish_message(id, msg)

    def _assert_message_logged(self, expected_msg):
        matching_messages = [logged_msg for logged_msg in get_log_messages() if logged_msg[1].strip() == expected_msg.strip()]
        if not matching_messages:
            self.fail('No matching message found, expected "{}", existing messages were:\n{}'.format(expected_msg, get_log_messages()))

    def _assert_message_pattern_logged(self, expected_msg_pattern):
        regex = re.compile(expected_msg_pattern)
        matching_messages = [logged_msg for logged_msg in get_log_messages() if regex.match(logged_msg[1])]
        if not matching_messages:
            self.fail('No matching message found, expected pattern "{}", existing messages were:\n{}'.format(expected_msg_pattern, get_log_messages()))

    def _then_no_ids_message_shown(self):
        self._assert_message_logged('Found 0 identities')

    def _then_correct_ids_message_shown_for(self, *ids):
        self._assert_message_logged('Found {} identities{}'.format(len(ids), '\n- ' + '\n- '.join(ids)))

    def _then_id_created_message_shown_for(self, id):
        self._assert_message_logged("New id '{}' created".format(id))

    def _then_id_already_exists_message_shown_for(self, id):
        self._assert_message_logged("The id '{}' already exists".format(id))

    def _then_id_deleted_message_shown_for(self, id):
        self._assert_message_logged("Id '{}' removed".format(id))

    def _then_id_not_deleted_message_shown_for(self, id):
        self._assert_message_logged("Id '{}' not removed".format(id))

    def _then_id_registered_message_shown_for(self, id):
        self._assert_message_pattern_logged("Registration request for id '{}' was accepted by the server \[[0-9a-f-]+\]".format(id))

    def _then_id_does_not_exist_message_shown_for(self, id):
        self._assert_message_logged("The id '{}' does not exist".format(id))

    def _then_id_already_registered_message_shown_for(self, id):
        self._assert_message_logged("The id '{}' has already been registered".format(id))

    def _then_registration_record_saved_for(self, id):
        self._assert_server_record_match_count({'type': 'registration', 'clientId': id}, 1)

    def _then_registration_record_not_saved_for(self, id):
        self._assert_server_record_match_count({'type': 'registration', 'clientId': id}, 0)

    def _then_bad_signature_message_shown_for(self, id):
        self._assert_message_logged("Bad message signature for client_id '{}'".format(id))

    def _then_bad_command_message_shown(self):
        self._assert_message_logged("Unrecognised command: '{}'".format(BAD_COMMAND))

    def _then_matches_found_message_is_shown_for(self, *expected_msgs):
        self._assert_message_logged('\n'.join([str(len(expected_msgs)) + ' matches found'] + list(expected_msgs)))

    def _then_server_down_message_shown(self):
        self._assert_message_pattern_logged("Unable to connect to the http server localhost:5000 .*")

    def _then_published_message_shown_for(self, id):
        self._assert_message_pattern_logged("Publication request for id '{}' was accepted by the server \[[0-9a-f-]+\]".format(id))

    def _then_no_matches_found_message_is_shown(self):
        self._assert_message_logged("0 matches found")

    def _then_publication_record_saved_for(self, id, msg):
        self._assert_server_record_match_count({'type': 'publication', 'clientId': id, 'data': {'message': msg}}, 1)

    def _then_publication_record_not_saved_for(self, id, msg):
        self._assert_server_record_match_count({'type': 'publication', 'clientId': id, 'data': {'message': msg}}, 0)

    def _assert_server_record_match_count(self, search_criteria, expected_count):
        if os.path.exists(SERVER_FILE):
            with open(SERVER_FILE, 'r') as f:
                messages = json.load(f)
                self.assertEqual(len([msg for msg in messages if all(search_criteria[k] == msg[k] for k in search_criteria.keys())]), expected_count)
        else:
            self.assertEqual(expected_count, 0)


if __name__ == '__main__':
    unittest.main()
