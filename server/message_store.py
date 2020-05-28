import json, os.path

file_path = 'store.json'

class MessageStore:
    def __init__(self):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.messages = json.load(file)
        else:
            self.messages = []

    def add(self, message):
        self.messages.append(message)
        self._save()

    def get_all(self):
        return self.messages

    def _save(self):
        with open(file_path, 'w') as file:
            json.dump(self.messages, file, indent=4)
