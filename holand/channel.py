import os
import sqlalchemy as sa
import json
import psycopg2
import asyncio


CHANNEL_EXPENSE_ITEM_CATEGORY_UPDATE = "expense_item_category_update"


c_engine = sa.create_engine(os.getenv('PG_CHANNEL_URL'))
c_raw = c_engine.raw_connection()
c_raw.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)


def notify(channel, payload):
    c_raw.cursor().execute("NOTIFY {channel}, '{payload}';".format(channel=channel, payload=json.dumps(payload)))


def listen(channel: str, callback):
    curs = c_raw.cursor()
    curs.execute("LISTEN {channel};".format(channel=channel))

    def handle():
        c_raw.poll()
        for mess in c_raw.notifies:
            try:
                args = json.loads(mess.payload)
                callback(args)
            except (ValueError, Exception) as e:
                print(e)
                loop = asyncio.get_running_loop()
                loop.stop()
                break
        c_raw.notifies.clear()

    loop = asyncio.get_event_loop()
    loop.add_reader(c_raw, handle)
    loop.run_forever()
