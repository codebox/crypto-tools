from server.handlers.base_handler import BaseHandler


class RegistrationHandler(BaseHandler):
    def __init__(self, message_store):
        super().__init__(message_store)

    def handles(self, details):
        return details['type'] == 'registration'

    def process(self, details):
        self.message_store.add(details)
