import telegram
import holand.config as hconfig

from holand.auth.user import User
from holand.exceptions import ExpenseItemIsInvalid
from holand.expense import (
    ExpenseItem,
    list_expense_category
)
from holand.i18n import t
from flask import current_app
from .ext import (
    Handler,
    Message,
)
from .callback import SelectExpenseCategoryCallback, ShowMoreExpenseCategoryCallback


class NewJoinUser(Handler):
    def require_auth(self) -> bool:
        return False

    def exec(self, event: Message):
        for us in event.new_chat_members:
            nu = User.query.filter_by(telegram_userid=us.id).first()
            if nu is None:
                nu = User(us.username, us.id)
            nu.is_active = True
            nu.save()
            pass
        if event.chat.id != current_app.config['bot.group_id']:
            hconfig.set('bot.group_id', str(event.chat.id))


class LeftUser(Handler):

    def exec(self, event: Message):
        u = User.query.filter_by(telegram_userid=event.left_chat_member.id).first()
        if u is not None:
            u.is_active = False
            u.save()


class AddExpenseItem(Handler):
    def exec(self, event: Message):
        if len(event.text) == 0:
            return
        try:
            item = ExpenseItem.from_text(event.text)
            item.telegram_message_id = event.message_id
            item.save()
        except ExpenseItemIsInvalid:
            event.bot.send_message(event.chat.id, t('invalid format'))
            return

        categories, op = list_expense_category(item.subject)
        buttons = [
            [
                telegram.InlineKeyboardButton(
                    f"{category.name}",
                    callback_data=SelectExpenseCategoryCallback.build_callback_data(item_id=item.id, category_id=category.id))
            ]
            for category in categories
        ]
        if op:
            buttons.append([
                telegram.InlineKeyboardButton(
                    "...",
                    callback_data=ShowMoreExpenseCategoryCallback.build_callback_data(item_id=item.id))
            ])
        event.bot.send_message(event.chat.id, t('select category'), reply_markup=telegram.InlineKeyboardMarkup(buttons))
        pass
