from server.handlers.base_handler import BaseHandler


class PublicationHandler(BaseHandler):
    def __init__(self, message_store):
        super().__init__(message_store)

    def handles(self, details):
        return details['type'] == 'publication'

    def process(self, details):
        self.message_store.add(details)
