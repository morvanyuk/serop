from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from queries import create_user, get_user

import environ

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env("SECRET_KEY")
ALGORITHM = env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = env("ACCESS_TOKEN_EXPIRE_MINUTES")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_new_user():
    username = input("Ім'я користувача: ")
    password = input("Пароль: ")
    password2 = input("Підтвердіть пароль: ")

    if password == password2:
        create_user(username, pwd_context.hash(password))
    else: 
        print("\nПаролі не співпадають\n")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "date": f"{datetime.utcnow()}"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_user(token):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        password = payload.get("password")
        user = get_user(username)
    except ExpiredSignatureError:
        return 401

    if user and password == user[0][1]:
        return {"username" : username, "password" : password}
    

    print(token, user, password, verify_password(plain_password=password, hashed_password=user[0][1]))
    raise HTTPException(status_code=401, detail="Invalid token")
    

if __name__ == "__main__":
    create_new_user()