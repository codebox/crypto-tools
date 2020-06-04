import json, os.path


class PublicKeyCache:
    file_path = 'public_key_cache.json'

    def __init__(self):
        if os.path.exists(PublicKeyCache.file_path):
            with open(PublicKeyCache.file_path, 'r') as file:
                self.cache = json.load(file)
        else:
            self.cache = {}

    def add(self, id, public_key):
        self.cache[id] = public_key
        self._save()

    def get(self, id):
        return self.cache.get(id, None)

    def _save(self):
        with open(PublicKeyCache.file_path, 'w') as file:
            json.dump(self.cache, file, indent=4)
