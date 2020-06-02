import unittest, os, glob

from client.main import process_args
from server.message_store import MessageStore
from common.logging import get_log_messages, clear_log_messages, LogLevel

BACKUP_FILE_EXT = '.bak'
SERVER_FILE = MessageStore.file_path
ID_1 = 'test1'
ID_2 = 'test2'

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
        os.rename(SERVER_FILE, SERVER_FILE + BACKUP_FILE_EXT)

    @classmethod
    def _restore_client_keys(cls):
        for key_file in glob.glob('keys/*.pem' + BACKUP_FILE_EXT):
            os.rename(key_file, key_file[:-len(BACKUP_FILE_EXT)])

    @classmethod
    def _restore_server_data(cls):
        os.rename(SERVER_FILE + BACKUP_FILE_EXT, SERVER_FILE)

    def test_client_list_keys_when_no_keys_exist(self):
        self._given_no_client_keys_exist()
        self._when_list_ids()
        self._then_no_ids_message_shown()

    def test_client_list_keys_when_keys_exist(self):
        self._given_keys_exist(ID_1, ID_2)
        clear_log_messages()
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_2, ID_1)

    def test_client_creates_valid_ids(self):
        clear_log_messages()
        self._when_create_id(ID_1)
        self._then_id_created_message_shown_for(ID_1)
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_1)
        self._when_create_id(ID_2)
        self._then_id_created_message_shown_for(ID_2)
        self._when_list_ids()
        self._then_correct_ids_message_shown_for(ID_2, ID_1)

    def test_client_creates_invalid_id(self):
        clear_log_messages()
        self._when_create_id(ID_1)
        self._then_id_created_message_shown_for(ID_1)
        self._when_create_id(ID_1)
        self._then_id_already_exists_message_shown_for(ID_1)

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

    def _when_list_ids(self):
        process_args(['', 'id.list'])

    def _when_create_id(self, id):
        process_args(['', 'id.create', id])

    def _assert_message_logged(self, expected_msg):
        matching_messages = [logged_msg for logged_msg in get_log_messages() if logged_msg[1].strip() == expected_msg.strip()]
        if not matching_messages:
            self.fail('No matching message found, existing messages were:\n{}'.format(get_log_messages()))

    def _then_no_ids_message_shown(self):
        self._assert_message_logged('Found 0 identities')

    def _then_correct_ids_message_shown_for(self, *ids):
        self._assert_message_logged('Found {} identities{}'.format(len(ids), '\n- ' + '\n- '.join(ids)))

    def _then_id_created_message_shown_for(self, id):
        self._assert_message_logged("New id '{}' created".format(id))

    def _then_id_already_exists_message_shown_for(self, id):
        self._assert_message_logged("The id '{}' already exists".format(id))


if __name__ == '__main__':
    unittest.main()
