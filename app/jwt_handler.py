import jwt
from decouple import config
from fastapi import Depends, HTTPException, status

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
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        headers = {"WWW-Authenticate": "Bearer"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers=headers)
