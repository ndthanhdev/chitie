import os

from click import echo
from flask import Flask, Blueprint, current_app, make_response, request
from holand.config import get_bulk as config_get_bulk
from telegram import Bot
from .dispatcher import Dispatcher


bot = Bot(os.getenv("TELEGRAM_SECRET"))
webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET').strip()
dispatcher = Dispatcher(bot)


def setup_webhook_endpoint(url: str):
    webhook_endpoint = f"{url}/{webhook_secret}"
    result = bot.setWebhook(webhook_endpoint)
    echo("Endpoint {} result: {}".format(webhook_endpoint, result))


def _before_webhook_request():
    configs = config_get_bulk([
        'bot.group_id',
    ])
    for path, val in configs.items():
        if path == 'bot.group_id':
            current_app.config[path] = int(val)
        else:
            current_app.config[path] = val


def listen_webhook_event(secret: str):
    if secret.strip() != webhook_secret:
        return make_response('Unauthorized!', 401)
    payload = request.get_json(force=True)
    if payload is None:
        return make_response({"status": "Error"}, 400)
    dispatcher.process(payload)
    return make_response('OK', 200)


def init_app(app: Flask):
    blueprint = Blueprint('bot', __name__)
    blueprint.add_url_rule("/<secret>", methods=['POST'], view_func=listen_webhook_event)
    blueprint.before_request(_before_webhook_request)
    app.register_blueprint(blueprint)
    pass
