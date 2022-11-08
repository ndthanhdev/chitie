from typing import List
from .callback import (
    SelectExpenseCategoryCallback,
    ShowMoreExpenseCategoryCallback
)
from .command import (
    SetupCommand,
    ReviewCommand,
    ShortcutCommand
)
from .ext import Handler
from .group import (
    NewJoinUser,
    LeftUser,
    AddExpenseItem
)


def _build_chain(*args: List['Handler']) -> 'Handler':
    first = current = args[0]
    for i in range(1, len(args)):
        current = current.set_next(args[i])
    return first


chatmessage_handler = _build_chain(
    SetupCommand(),
    ReviewCommand(),
    ShortcutCommand(),
    NewJoinUser(),
    LeftUser(),
    AddExpenseItem()
)
callbackquery_handler = _build_chain(
    SelectExpenseCategoryCallback(),
    ShowMoreExpenseCategoryCallback()
)
