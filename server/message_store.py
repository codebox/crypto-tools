class MessageStore:
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages.append(message)

    def get_all(self):
        return self.messages
