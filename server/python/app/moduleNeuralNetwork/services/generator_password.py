from cryptography.fernet import Fernet

class GeneratorPassword:
    @staticmethod
    def encrypte(secret_key: bytes, password: str) -> bytes:
        f = Fernet(secret_key)
        return f.encrypt(password.encode())

    @staticmethod
    def decrypt(secret_key: bytes, hash_password: bytes) -> str:
        f = Fernet(secret_key)
        return f.decrypt(hash_password).decode()
