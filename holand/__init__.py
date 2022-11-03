from __future__ import absolute_import
from flask import Flask
from flask_cors import CORS
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def create_app():
    app = Flask(__name__)
    CORS(app, resources=r'/*')
    app.config.from_object("config.Local")

    with app.app_context():
        from . import db, bot, cli, config, auth
        db.init_app(app)
        config.load(app)
        bot.init_app(app)
        cli.init_app(app)
        auth.init_app(app)

    return app


_ = create_app
