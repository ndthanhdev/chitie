import re
import sqlalchemy as sa
import holand.channel

from flask import current_app
from holand.db import connection, ActiveRecord


class CategoryRecommendation(connection.Model, ActiveRecord):

    __tablename__ = 'expense_category_recommendations'

    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String, nullable=False)
    category_id = sa.Column(sa.Integer, nullable=False)
    score = sa.Column(sa.Integer, nullable=False)
    hit_count = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)

    def __init__(self, word, category_id):
        self.word = word
        self.category_id = category_id
        self.hit_count = 0
        self.score = 10


def count_word_hit_with_category(subject: str, category_id: int):
    words = subject.split(' ')
    for i in range(0, len(words)):
        if re.match(r'^\D+$', words[i]) is None:
            continue

        record = CategoryRecommendation.query.filter_by(word=words[i], category_id=category_id).first()
        if record is None:
            record = CategoryRecommendation(words[i], category_id)
        record.hit_count = record.hit_count + 1
        record.save()


def get_category_id_by_subject(subject: str):
    words = subject.split(' ')
    first_word = words[0]

    options = CategoryRecommendation.query.filter_by(word=first_word).order_by(CategoryRecommendation.hit_count.desc()).all()
    return [
        cate.category_id
        for cate in options
    ]


def listen_item_category_update():
    def handler(payload: dict):
        current_app.logger.info(str(payload), channel=holand.channel.CHANNEL_EXPENSE_ITEM_CATEGORY_UPDATE)
        count_word_hit_with_category(payload['subject'], payload['category_id'])

    holand.channel.listen(
        holand.channel.CHANNEL_EXPENSE_ITEM_CATEGORY_UPDATE,
        handler
    )
