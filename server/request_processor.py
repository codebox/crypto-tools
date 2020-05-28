import threading
from common.logging import log, LogLevel
from server.exception import InvalidSignatureError
from server.message_store import MessageStore
from server.handlers.registration_handler import RegistrationHandler
from server.handlers.publication_handler import PublicationHandler
from common.crypto_utils import verify_signature


class RequestProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.message_store = MessageStore()
        self.handlers = [RegistrationHandler(self.message_store), PublicationHandler(self.message_store)]

    def start(self):
        threading.Thread(target=self._work, daemon=True).start()

    def _verify_signature(self, item):
        public_key = item.get('publicKey', self._get_public_key_for_client_id(item['clientId']))
        if not verify_signature(item['data'], item['signature'], public_key):
            raise InvalidSignatureError()
        log(LogLevel.DEBUG, 'Signature for {} ok'.format(item['clientId']))

    def _work(self):
        while True:
            item = self.queue.get()
            self._verify_signature(item)

            [handler.process(item) for handler in self.handlers if handler.handles(item)]

            self.queue.task_done()

    def _get_public_key_for_client_id(self, client_id):
        registrations_for_client = [item for item in self.message_store.messages if item['clientId'] == client_id and item['type'] == 'registration']
        if registrations_for_client:
            return registrations_for_client[0]['data']['publicKey']
        raise ValueError('No public key found for client_id "{}"'.format(client_id))
