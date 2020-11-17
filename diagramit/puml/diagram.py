import uuid
from queue import LifoQueue as Stack

import loguru

from diagramit.puml.utils import assert_format, output_puml, desc2alias
from .utils import alias_gen

logger = loguru.logger


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
    def _rand_node_id():
        return 'N_' + uuid.uuid4().hex

    @staticmethod
    def get_alias():
        return next(Context._alias)

    @staticmethod
    def make_negative():
        from .diagram import FakeDiagram
        if Context._cur_context is None:
            Context._cur_context = FakeDiagram()


class Base():
    def __init__(self, path=None, format='png', show=False, **kwargs):
        self.path = path
        self.text = []
        self.ns = []
        self.es = []
        self.format = format
        assert_format(format)

        self.show = show

        self.alias_set = set()
        self._alias_gen = self._rand_id()

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    def add_note(self, p):
        self.text.append(p)

    def add_node(self, p):
        self.ns.append(p)
        self.text.append(p)

    def add_link(self, edge):
        self.text.append(edge)
        return edge

    def add_text(self, text):
        self.text.append(text)

    def to_puml(self):
        raise NotImplementedError


class FakeDiagram(Base):
    pass


class Diagram(Base):

    def get_alias(self, alias=None):
        if alias:
            alias = desc2alias(alias)

            if alias:
                if alias in self.alias_set:
                    alias = alias + next(self._alias_gen)
                    self.alias_set.add(alias)
                else:
                    self.alias_set.add(alias)
                return alias

        return 'n' + next(self._alias_gen)

    def __enter__(self):
        Context._context.put_nowait(Context._cur_context)
        Context._cur_context = self

    def __exit__(self, *args):
        context = Context._context.get_nowait()
        Context._cur_context = context

        text = self.to_puml()
        print(text)

        if self.show:
            print(text)
        else:
            with open(self.path, 'w') as fd:
                fd.write(text)

            if self.format:
                try:
                    output_puml(self.path, self.format)
                except Exception as e:
                    logger.exception(e)
                    logger.error('dump {} to {} error', self.path, self.format)
