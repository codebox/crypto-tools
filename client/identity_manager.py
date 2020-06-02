from os import makedirs, listdir, remove
from os.path import join, isfile
from common.logging import log, LogLevel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class IdManager:
    key_extension = '.pem'

    def __init__(self, key_dir='./keys', key_password=None):
        self.key_dir = key_dir
        self.key_password = key_password
        makedirs(self.key_dir, exist_ok=True)
        self.__load_keys()

    def __load_keys(self):
        self.keys = {}
        for file_name in listdir(self.key_dir):
            if file_name.endswith(IdManager.key_extension):
                key_name = file_name[:-len(IdManager.key_extension)]
                key_file_name = join(self.key_dir, file_name)
                with open(key_file_name, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None if self.key_password is None else self.key_password.encode(),
                        backend=default_backend()
                    )
                    self.keys[key_name] = private_key
                    log(LogLevel.DEBUG, 'Loaded key {}'.format(key_name))

    def create(self, name):
        if name in self.keys:
            raise ValueError("The id '{}' already exists".format(name))

        key =rsa.generate_private_key(
            backend=default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        encryption_algorithm=serialization.NoEncryption() if self.key_password is None else serialization.BestAvailableEncryption(self.key_password.encode())
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        file_name = join(self.key_dir, name + IdManager.key_extension)
        with open(file_name, 'wb') as key_file:
            key_file.write(pem)

    def list(self):
        return self.keys.keys()

    def delete(self, name):
        pem_file_path = '{}/{}{}'.format(self.key_dir, name, IdManager.key_extension)
        if isfile(pem_file_path):
            remove(pem_file_path)
            log(LogLevel.DEBUG, 'Removed id {}'.format(name))
        else:
            log(LogLevel.WARN, 'No id {} could be found'.format(name))

    def get_key(self, name):
        if name not in self.keys:
            raise ValueError('The id "{}" does not exist'.format(name))

        return self.keys[name]
