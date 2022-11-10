import sqlalchemy as sa
import holand.channel

from holand.db import connection, ActiveRecord
from holand.exceptions import ExpenseItemIsInvalid
from holand.util import is_number


TRANSACTION_TYPE_CREDIT = "credit"
TRANSACTION_TYPE_DEBIT = "debit"

CREDIT_AMOUNT_SYMBOL = 'c'


class Item(connection.Model, ActiveRecord):
    __tablename__ = "expense_items"

    id = sa.Column(sa.Integer, primary_key=True)
    subject = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    category_id = sa.Column(sa.Integer, nullable=True)
    transaction_type = sa.Column(sa.String, nullable=False)
    telegram_message_id = sa.Column(sa.Integer, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)

    def save(self):
        self.amount = float(self.amount)
        if self.amount <= 0 or len(self.subject) == 0:
            raise ExpenseItemIsInvalid
        super().save()

    @classmethod
    def from_text(cls, text: str):
        item = cls()
        stripped_text = text.strip()
        chunks = stripped_text.split(' ')

        last_chunk = chunks[len(chunks) - 1].lower()
        if last_chunk.endswith(CREDIT_AMOUNT_SYMBOL):
            item.transaction_type = TRANSACTION_TYPE_CREDIT
        else:
            item.transaction_type = TRANSACTION_TYPE_DEBIT
        amount = last_chunk.removesuffix(CREDIT_AMOUNT_SYMBOL)
        if not is_number(amount):
            raise ExpenseItemIsInvalid
        if len(chunks[0:len(chunks) - 1]) == 0:
            raise ExpenseItemIsInvalid

        item.amount = float(amount)
        item.subject = ' '.join(chunks[0:len(chunks) - 1])
        return item

    def update_category(self, category_id: int):
        self.category_id = category_id
        self.save()
        holand.channel.notify(
            holand.channel.CHANNEL_EXPENSE_ITEM_CATEGORY_UPDATE,
            {
                'id': self.id,
                'subject': self.subject,
                'amount': self.amount,
                'category_id': self.category_id
            }
        )

    def is_debit(self) -> bool:
        return self.transaction_type == TRANSACTION_TYPE_DEBIT

    def is_credit(self) -> bool:
        return self.transaction_type == TRANSACTION_TYPE_CREDIT
