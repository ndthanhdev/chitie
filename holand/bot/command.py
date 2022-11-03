import telegram
import holand.config as holand_config

from holand.util import timerange
from holand.expense import filter_expense
from .ext import (
    Handler,
    Message
)


class SetupCommand(Handler):
    def exec(self, event: Message):
        if event.chat.type not in [telegram.Chat.GROUP, telegram.Chat.SUPERGROUP]:
            pass
        holand_config.set('bot.group_id', str(event.chat.id))


class ReviewCommand(Handler):
    def exec(self, event: Message):
        tr = timerange.from_str('this month')
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

        content = "\n".join([
            "```",
            f'{"D":2}| {debit_amount:>15,}',
            f'{"C":2}| {credit_amount:>15,}',
            '{:->19}'.format('-'),
            f'{"T":2}| {total_amount:>15,}',
            "```",
        ])
        event.bot.send_message(chat_id=event.chat.id, text=content, parse_mode=telegram.ParseMode.MARKDOWN_V2)
