import json, os.path


class MessageStore:
    file_path = 'store.json'

    def __init__(self):
        if os.path.exists(MessageStore.file_path):
            with open(MessageStore.file_path, 'r') as file:
                self.messages = json.load(file)
        else:
            self.messages = []

    def add(self, message):
        self.messages.append(message)
        self._save()

    def get_all(self):
        return self.messages

    def _save(self):
        with open(MessageStore.file_path, 'w') as file:
            json.dump(self.messages, file, indent=4)
