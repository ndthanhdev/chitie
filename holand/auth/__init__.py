__all__ = [
    'init_app'
]

from click import echo

from .user import User
from .jwt import init_app


def add_user(telegram_username, telegram_userid):
    user = User(telegram_username, telegram_userid)
    user.save()
    echo("Create success")
