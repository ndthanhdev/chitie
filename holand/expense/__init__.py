__all__ = [
    'ExpenseCategory',
    'ExpenseItem',
    'filter_expense',
    'list_expense_category'
]

from .item import (
    Item as ExpenseItem,
    filter as filter_expense
)
from .category import (
    Category as ExpenseCategory,
)
from .category_recommendation import (
    get_category_id_by_subject
)


def list_expense_category(subject: str = ''):
    optimized = False
    if len(subject) > 0:
        category_ids = get_category_id_by_subject(subject)
        if len(category_ids) > 0:
            categories = ExpenseCategory.query.filter(ExpenseCategory.id.in_(category_ids)).all()
            optimized = True
        else:
            categories = ExpenseCategory.query.filter_by(is_active=True).all()
    else:
        categories = ExpenseCategory.query.filter_by(is_active=True).all()
    return categories, optimized
