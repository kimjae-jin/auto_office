# app/core/security.py
from .config import FERNET

def encrypt_data(data: str) -> bytes:
    """주어진 문자열 데이터를 암호화합니다."""
    if not isinstance(data, str):
        data = str(data)
    return FERNET.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data: bytes) -> str:
    """암호화된 데이터를 복호화하여 문자열로 반환합니다."""
    decrypted_bytes = FERNET.decrypt(encrypted_data)
    return decrypted_bytes.decode('utf-8')

