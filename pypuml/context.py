from queue import LifoQueue as Stack


def alias_gen():
    while 1:
        yield 'p{}'.format(Context._count)
        Context._count += 1


class Context():
    _count = 1
    _context = Stack()
    _cur_context = None
    _alias = alias_gen()

    @staticmethod
    def get_alias():
        return next(Context._alias)
