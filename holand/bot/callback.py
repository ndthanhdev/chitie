import telegram

from holand.expense import (
    ExpenseItem,
    ExpenseCategory,
    list_expense_category
)
from .ext import (
    CallbackQuery,
    CallbackHandler
)
from holand.i18n import t


class SelectExpenseCategoryCallback(CallbackHandler):
    def exec(self, event: CallbackQuery):
        args = event.arguments()
        item = ExpenseItem.query.get(int(args['item_id']))
        item.update_category(int(args['category_id']))
        category = ExpenseCategory.query.get(item.category_id)
        event.edit_message_text(f'> {category.name}')
        return True


class ShowMoreExpenseCategoryCallback(CallbackHandler):
    def exec(self, event: CallbackQuery):
        args = event.arguments()

        categories, _ = list_expense_category()
        buttons = [
            [
                telegram.InlineKeyboardButton(
                    f"{category.name}",
                    callback_data=SelectExpenseCategoryCallback.build_callback_data(item_id=args['item_id'], category_id=category.id))
            ]
            for category in categories
        ]
        event.edit_message_text(t('select category'), reply_markup=telegram.InlineKeyboardMarkup(buttons))
        return True
