from app.config.settings import PASS_SECRET_KEY
from cryptography.fernet import Fernet
import base64



def get_cipher():
    secret_key = PASS_SECRET_KEY

    key = base64.urlsafe_b64encode(secret_key.encode().ljust(32)[:32])
    return Fernet(key)


def encrypt_password(password: str) -> str:
    cipher = get_cipher()
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> str:
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_password.encode())
    return decrypted.decode()