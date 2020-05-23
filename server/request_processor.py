import threading

from server.exception import InvalidSignatureError
from server.message_store import MessageStore
from server.handlers.registration_handler import RegistrationHandler
from common.crypto_utils import verify_signature

class RequestProcessor:
    def __init__(self, queue):
        self.queue = queue
        message_store = MessageStore()
        self.handlers = [RegistrationHandler(message_store)]

    def start(self):
        threading.Thread(target=self._work, daemon=True).start()

    def _verify_signature(self, item):
        if not verify_signature(item['data'], item['signature'], item['publicKey']):
            raise InvalidSignatureError()
        print('sigok')

    def _work(self):
        while True:
            item = self.queue.get()
            print(item)
            self._verify_signature(item)

            [handler.process(item) for handler in self.handlers if handler.handles(item)]

            self.queue.task_done()
