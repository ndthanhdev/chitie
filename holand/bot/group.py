import telegram

from holand.exceptions import ExpenseItemIsInvalid
from holand.expense import (
    ExpenseItem,
    list_expense_category
)
from holand.i18n import t
from .ext import (
    Handler,
    Message,
)
from .callback import SelectExpenseCategoryCallback, ShowMoreExpenseCategoryCallback


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
