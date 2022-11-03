from flask import Flask
from click import Argument, Command
from flask.cli import with_appcontext


def init_app(app: Flask):
    import holand.auth as auth
    app.cli.add_command(Command('auth:add_user',
                                callback=with_appcontext(auth.add_user),
                                params=[
                                    Argument(['telegram_username'], required=True),
                                    Argument(['telegram_userid'], required=True),
                                ]))

    import holand.bot as bot
    app.cli.add_command(Command('bot:setup-webhook',
                                callback=with_appcontext(bot.setup_webhook_endpoint),
                                params=[Argument(['url'], required=True)]))

    import holand.expense.category as expense_category
    app.cli.add_command(Command('expense:add-category',
                                callback=with_appcontext(expense_category.add),
                                params=[Argument(['name'], required=True)]))
    app.cli.add_command(Command('expense:list-category',
                                callback=with_appcontext(expense_category.list)))
    import holand.expense.category_recommendation
    app.cli.add_command(Command('expense:listen-item-category-update',
                                callback=with_appcontext(holand.expense.category_recommendation.listen_item_category_update)))
