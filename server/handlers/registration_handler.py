from server.handlers.base_handler import BaseHandler


class RegistrationHandler(BaseHandler):
    def __init__(self, message_store):
        super().__init__(message_store)

    def handles(self, details):
        return details['type'] == 'registration'

    def process(self, details):
        print(details)
        if filter(lambda msg: msg['type'] == 'registration' and msg['clientId'] == details['clientId'], self.message_store.messages):
            raise ValueError("The id '{}' has already been registered".format(details['clientId']))
        self.message_store.add(details)
