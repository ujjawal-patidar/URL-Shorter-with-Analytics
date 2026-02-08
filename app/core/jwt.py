import os
from datetime import datetime, timedelta
from jose import jwt
import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM_TO_ENCODE = os.getenv("ALGORITHM_TO_ENCODE")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM_TO_ENCODE)
