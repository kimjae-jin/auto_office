# app/core/config.py
from cryptography.fernet import Fernet

# 중요: 이 키는 한 번 생성되면 절대 변경하면 안 됩니다.
# 만약 변경되면 기존에 암호화된 모든 데이터를 읽을 수 없게 됩니다.
SECRET_KEY = Fernet.generate_key()
FERNET = Fernet(SECRET_KEY)

DATABASE_FILE = "auto_office.db"

