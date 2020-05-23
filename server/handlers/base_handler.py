class BaseHandler:
    def __init__(self, message_store):
        self.message_store = message_store

    def handles(self, details):
        raise NotImplementedError()

    def process(self, details):
        raise NotImplementedError()
