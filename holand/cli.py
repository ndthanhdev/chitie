from flask import Flask
from click import Command
from flask.cli import with_appcontext


def init_app(app: Flask):

    import holand.expense.category_recommendation
    app.cli.add_command(Command('expense:listen-item-category-update',
                                callback=with_appcontext(holand.expense.category_recommendation.listen_item_category_update)))
