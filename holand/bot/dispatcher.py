import telegram
from flask import current_app

from holand.auth.user import find_by_telegram_uid

from .callback import (
    SelectExpenseCategoryCallback,
    ShowMoreExpenseCategoryCallback
)
from .command import (
    SetupCommand,
    ReviewCommand
)
from .ext import CallbackQuery, Message
from .group import AddExpenseItem


class Dispatcher:

    def __init__(self, bot: telegram.Bot):
        self.bot = bot
        self.commands = [
            SetupCommand(),
            ReviewCommand()
        ]
        self.callbacks = [
            SelectExpenseCategoryCallback(),
            ShowMoreExpenseCategoryCallback()
        ]

    def callback_handler(self, name: str):
        for handler in self.callbacks:
            if handler.__class__.str_alias() == name:
                return handler
        return None

    def command_handler(self, name: str):
        for handler in self.commands:
            if handler.__class__.str_alias() == name:
                return handler
        return None

    def process(self, payload: dict):
        event = None
        handler = None
        if 'callback_query' in payload:
            event = CallbackQuery.de_json(payload['callback_query'], self.bot)
            if event is None:
                return
            handler = self.callback_handler(event.function())

        if 'message' in payload:
            event = Message.de_json(payload['message'], self.bot)
            if event is None:
                return
            print(event.is_command())
            print(event.command())
            if event.is_command():
                handler = self.command_handler(event.command())
            elif event.text is not None and event.chat.id == current_app.config['bot.group_id']:
                handler = AddExpenseItem()

        if event is None:
            return

        user = find_by_telegram_uid(event.from_user.id)
        if user is None:
            return

        if handler is None:
            return
        handler.exec(event)
        pass
