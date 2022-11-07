import os
import telegram
import holand.config as holand_config
import holand.auth.user as user

from flask import url_for
from holand.i18n import t
from holand.util import timerange
from holand.expense import filter_expense
from .ext import (
    Handler,
    Message
)


class SetupCommand(Handler):
    def require_auth(self) -> bool:
        return False

    def exec(self, event: Message):
        if event.chat.type not in [telegram.Chat.GROUP, telegram.Chat.SUPERGROUP]:
            return
        admin = user.User.query.first()
        secret = event.argumentstr()
        if admin is None:
            if os.getenv('TELEGRAM_WEBHOOK_SECRET') != secret:
                event.bot.send_message(event.chat.id, 'Unauthorized!')
                return
            admin = user.User(event.from_user.username, event.from_user.id)
            admin.save()
        holand_config.set('bot.group_id', str(event.chat.id))
        holand_config.set('bot.group_type', event.chat.type)
        reply_markup = telegram.InlineKeyboardMarkup([
            [
                telegram.InlineKeyboardButton(
                    "Open",
                    login_url=telegram.LoginUrl(url_for('web.telegram_auth', _external=True, _scheme='https')),
                )
            ]
        ])
        event.bot.send_message(event.chat.id, t('setup done'))
        mess = event.bot.send_message(event.chat.id, 'Web', reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)
        mess.pin(disable_notification=True)
        event.delete()


class ReviewCommand(Handler):
    def exec(self, event: Message):
        if len(event.argumentstr()) == 0:
            tr = timerange.from_str('this month')
        else:
            tr = timerange.from_str(event.argumentstr())
        if tr.time_from is None or tr.time_to is None:
            raise ValueError('Invalide date')
        records = filter_expense({'time_from': tr.time_from, 'time_to': tr.time_to})
        debit_amount = 0
        credit_amount = 0
        total_amount = 0
        for r in records:
            if r.is_credit():
                credit_amount += r.amount
            if r.is_debit():
                debit_amount += r.amount

            total_amount += r.amount

        maxlength = 0
        for amount in [debit_amount, credit_amount, total_amount]:
            if maxlength < len(f'{amount:,}'):
                maxlength = len(f'{amount:,}')

        content = "\n".join([
            "```",
            f'{"d":2}| {debit_amount:>{maxlength},}',
            f'{"c":2}| {credit_amount:>{maxlength},}',
            f'{"-":->{maxlength + 4}}',
            f'{"t":2}| {total_amount:>{maxlength},}',
            "```",
        ])
        event.bot.talks(text=content, parse_mode=telegram.ParseMode.MARKDOWN_V2)


class ShortcutCommand(Handler):
    def exec(self, event: Message):
        event.bot.unpin_all_chat_messages(event.chat.id)
        reply_markup = telegram.InlineKeyboardMarkup([
            [
                telegram.InlineKeyboardButton(
                    "Open",
                    login_url=telegram.LoginUrl(url_for('web.telegram_auth', _external=True, _scheme='https')),
                )
            ]
        ])
        mess = event.bot.send_message(event.chat.id, 'Web', reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)
        mess.pin(disable_notification=True)
        event.delete()
