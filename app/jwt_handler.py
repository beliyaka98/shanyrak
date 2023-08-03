import time
import jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def signJWT(user_id: str):
    payload = {
        "user_id": user_id,
        #"expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decodeJWT(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    