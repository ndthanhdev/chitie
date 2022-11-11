__all__ = [
    'ExpenseCategory',
    'ExpenseItem',
    'filter_expense',
    'list_expense_category'
]
import datetime
import sqlalchemy as sa

from .item import (
    Item as ExpenseItem,
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


def filter_expense(conditions: dict, order_by_column=None, order_type="asc"):
    query = ExpenseItem.query
    if conditions.get('time_from') is not None and conditions.get('time_to') is not None:
        query = query.filter(sa.and_(
            ExpenseItem.created_at >= conditions['time_from'],
            ExpenseItem.created_at <= conditions['time_to']
        ))
        del conditions['time_from']
        del conditions['time_to']

    for key in conditions:
        if not hasattr(ExpenseItem, key) or conditions[key] is None or len(str(conditions[key])) == 0:
            continue
        query = query.filter(getattr(ExpenseItem, key) == conditions[key])

    if order_by_column is not None:
        if order_type == "asc":
            query = query.order_by(getattr(ExpenseItem, order_by_column).asc())
        elif order_type == "desc":
            query = query.order_by(getattr(ExpenseItem, order_by_column).desc())

    expense_items = query.all()
    category_ids = list(set(map(lambda item: item.category_id, expense_items)))
    categories = ExpenseCategory.query.filter(ExpenseCategory.id.in_(category_ids)).all()
    category_map = {}
    for cate in categories:
        category_map.setdefault(cate.id, cate)

    result = []
    for item in expense_items:
        item.set_category(category_map[item.category_id])
        result.append(item)

    return result
