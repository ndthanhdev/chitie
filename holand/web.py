import collections
import hashlib
import holand.config as hconfig
import hmac
import telegram
import telegram.error

from holand.bot import bot
from flask import Flask, Blueprint, abort, current_app, flash, g, redirect, render_template, request, session, url_for
from urllib.parse import unquote
from .auth import user


def _load_auth():
    if 'user_id' in session:
        g.user = user.find_by_id(session.get('user_id'))
    else:
        g.user = None


def login_required(view):
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('web.login'))
        return view(**kwargs)
    return wrapped_view


def index():
    return render_template('index.html')


def login():
    return render_template('login.html')


def telegram_auth():
    query_params = request.args.to_dict()
    hash_check = query_params.pop('hash')
    sortParams = collections.OrderedDict(sorted(query_params.items()))
    message = "\n".join(["{}={}".format(k, unquote(v)) for k, v in sortParams.items()])
    secret = hashlib.sha256(current_app.config.get('TELEGRAM_SECRET').encode('utf-8'))
    hash_message = hmac.new(secret.digest(), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    if hash_check != hash_message:
        return abort(401)
    u = user.find_by_telegram_uid(query_params.get('id'))
    if hconfig.get('bot.group_type').value == telegram.Chat.SUPERGROUP and u is None:
        try:
            chatmember = bot.get_chat_member(hconfig.get('bot.group_id').value, query_params['id'])
            u = user.User(chatmember.user.username, chatmember.user.id)
            u.save()
        except telegram.error.TelegramError:
            pass
    if u is None or not u.is_active:
        error = 'Unknowed user'
        flash(error)
        return redirect(url_for('web.login'))
    session.clear()
    session['user_id'] = u.uuid
    return redirect(url_for('web.index'))


def init_app(app: Flask):
    web = Blueprint('web', __name__)
    web.add_url_rule('/', endpoint='index', view_func=login_required(index))
    web.add_url_rule('/login', endpoint='login', view_func=login)
    web.add_url_rule('/tauth', endpoint='telegram_auth', view_func=telegram_auth)
    web.before_request(_load_auth)
    app.register_blueprint(web)
    pass
