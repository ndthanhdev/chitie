import os
import hashlib

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from .user import User


jwt = JWTManager()
secret = os.getenv('SECRET_KEY')


def init_app(app: Flask):
    jwt.init_app(app)


def sign(text: str) -> str:
    h = hashlib.new('sha256')
    hashed_text = f'{text}:{secret}'
    h.update(hashed_text.encode())
    return h.hexdigest()


def verify_sign(text: str, hash: str) -> bool:
    checked = sign(text)
    return checked == hash


def generate_token(user: User) -> str:
    print(user.uuid)
    sub = user.uuid + '.' + sign(user.uuid)
    token = create_access_token(sub)
    return token


@jwt.user_lookup_loader
def load_user_from_db(jwt_header, jwt_payload):
    _ = jwt_header
    user_uuid, sign = jwt_payload['sub'].split('.')
    if not verify_sign(user_uuid, sign):
        return None
    return User.query.filter_by(uuid=user_uuid).first()
