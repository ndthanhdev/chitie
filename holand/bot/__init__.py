import os

from flask import Flask, Blueprint, current_app, g, make_response, request, url_for
from holand.config import get_bulk as config_get_bulk
from .dispatcher import Dispatcher
from .ext import Bot


bot = Bot(os.getenv("TELEGRAM_SECRET"))
webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET').strip()
dispatcher = Dispatcher(bot)


def _before_webhook_request():
    configs = config_get_bulk([
        'bot.group_id',
        'bot.group_type',
    ])
    for path, val in configs.items():
        if path in ['bot.group_id']:
            current_app.config[path] = int(val)
        else:
            current_app.config[path] = val


def listen_webhook_event(secret: str):
    if secret.strip() != webhook_secret:
        return make_response('Unauthorized!', 401)
    payload = request.get_json(force=True)
    if payload is None:
        return make_response({"status": "Error"}, 400)
    try:
        dispatcher.process(payload)
    except Exception as e:
        errormsg = str(e)
        bot.talks(text=f'Error! {errormsg}')
    finally:
        return make_response('OK', 200)


def init_app(app: Flask):
    botbp = Blueprint('bot', __name__)
    botbp.add_url_rule("/tlg/<secret>", endpoint='callback', methods=['POST'], view_func=listen_webhook_event)
    botbp.before_request(_before_webhook_request)
    app.register_blueprint(botbp)
    bot.setWebhook(url_for('bot.callback', _external=True, _scheme='https', secret=os.getenv('TELEGRAM_WEBHOOK_SECRET')))
    g.bot = bot
    pass
