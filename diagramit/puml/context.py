import uuid
from queue import LifoQueue as Stack

from .utils import alias_gen


class Context():
    _count = 1
    _context = Stack()
    _cur_context = None
    _alias = alias_gen()
    top_context = None

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    @staticmethod
    def get_alias():
        return next(Context._alias)
