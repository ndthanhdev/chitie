import re
import telegram

from abc import abstractmethod
from urllib.parse import parse_qs, urlencode


class Message(telegram.Message):

    def command(self) -> str:
        if self.entities is None or len(self.entities) == 0:
            return ''
        for entity in self.entities:
            if entity.type == telegram.MessageEntity.BOT_COMMAND:
                return self.text[entity.offset:entity.length + entity.offset].lstrip('/')
        return ''

    def is_command(self) -> bool:
        if self.entities is None or len(self.entities) == 0:
            return False
        for entity in self.entities:
            if entity.type == telegram.MessageEntity.BOT_COMMAND:
                return True
        return False


class CallbackQuery(telegram.CallbackQuery):

    def function(self) -> str:
        data_chunks = self.data.split('|')
        return data_chunks[0]

    def arguments(self) -> dict:
        data_chunks = self.data.split('|')
        rawdict = parse_qs(data_chunks[1])
        result = {}
        for key in rawdict.keys():
            value = rawdict[key]
            if len(value) == 1:
                result[key] = value[0]
                continue
            result[key] = value
        return result


class Handler:

    @abstractmethod
    def exec(self, event: telegram.TelegramObject):
        pass

    @classmethod
    def str_alias(cls) -> str:
        if hasattr(cls, '__stralias__'):
            return cls.__stralias__

        class_name = cls.__name__
        if class_name.endswith('Command'):
            alias = class_name.removesuffix('Command')
        if class_name.endswith('Callback'):
            alias = class_name.removesuffix('Callback')

        return re.sub(r'(?<!^)(?=[A-Z])', '_', alias).lower()


class CallbackHandler(Handler):

    @classmethod
    def build_callback_data(cls, **kwargs):
        args = urlencode(kwargs)
        data = '{}|{}'.format(cls.str_alias(), args)
        return data
