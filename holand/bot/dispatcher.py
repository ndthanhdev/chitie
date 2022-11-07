import telegram
from flask import current_app

import holand.auth.user as user

from .callback import (
    SelectExpenseCategoryCallback,
    ShowMoreExpenseCategoryCallback
)
from .command import (
    SetupCommand,
    ReviewCommand,
    ShortcutCommand
)
from .ext import CallbackQuery, Message
from .group import (
    NewJoinUser,
    LeftUser,
    AddExpenseItem
)


class Dispatcher:

    def __init__(self, bot: telegram.Bot):
        self.bot = bot
        self.commands = [
            SetupCommand(),
            ReviewCommand(),
            ShortcutCommand()
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
            if event.is_command():
                handler = self.command_handler(event.command())
            elif event.new_chat_members is not None and len(event.new_chat_members) > 0:
                handler = NewJoinUser()
            elif event.left_chat_member is not None:
                handler = LeftUser()
            elif event.text is not None and event.chat.id == current_app.config['bot.group_id']:
                handler = AddExpenseItem()

        if event is None:
            raise ValueError("Invalid message")
        if event.from_user.is_bot:
            return
        if handler is None:
            return
        u = user.find_by_telegram_uid(event.from_user.id)
        if u is None and current_app.config['bot.group_type'] == telegram.Chat.SUPERGROUP:
            try:
                chatmember = self.bot.get_chat_member(current_app.config['bot.group_id'], event.from_user.id)
                u = user.User(chatmember.user.username, chatmember.user.id)
                u.save()
            except telegram.error.TelegramError:
                pass
        if handler.require_auth() and (u is None or not u.is_active):
            return
        handler.exec(event)
        pass
