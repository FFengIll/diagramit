import inspect
import re
import uuid
from queue import LifoQueue as Stack

import loguru

from diagramit.puml.utils import assert_format, output_puml, desc2alias
from diagramit.puml.utils import direction
from .utils import alias_gen

logger = loguru.logger


class Context():
    _count = 1
    _context = Stack()
    _cur_context = None
    _alias = alias_gen()
    diagram = None

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
        if Context._cur_context is None:
            Context._cur_context = FakePumlDiagram()


class PumlBase():
    def __init__(self, path=None, format='png', show=False, export=True, output=False, **kwargs):
        self.path = path
        self.text = []
        self.ns = []
        self.es = []
        self.format = format
        self.output = output
        assert_format(format)

        self.show = show
        self.export = export

        self.alias_set = set()
        self._alias_gen = self._rand_id()
        self._mix = False

        self.Edge = None
        self.op_map = {
            '>>': '',
            '<<': '',
            '-': '',
            '**': '',
            '.': ''
        }

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    def add_note(self, p):
        self.text.append(p)

    def add_node(self, p):
        self.ns.append(p)
        self.text.append(p)

    def add_link(self, edge) -> 'BaseEdge':
        self.text.append(edge)
        return edge

    def add_text(self, text):
        self.text.append(text)

    def make_edge(self, source, target, type='', **kwargs) -> 'BaseEdge':
        if type:
            type = self.op_map.get(type, None)
            assert type is not None
        return self.add_link(self.Edge(source, target, **kwargs))

    def to_puml(self):
        raise NotImplementedError


class FakePumlDiagram(PumlBase):
    pass


class PumlDiagram(PumlBase):

    @property
    def mix(self):
        return self._mix

    @mix.setter
    def mix(self, value: bool):
        self._mix = value

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
        Context.diagram = self

    def __exit__(self, *args):
        context = Context._context.get_nowait()
        Context._cur_context = context

        text = self.to_puml()
        print(text)

        if self.show:
            print(text)
        else:
            print(text)

            if self.export:
                with open(self.path, 'w') as fd:
                    fd.write(text)

                if self.format and self.output:
                    try:
                        output_puml(self.path, self.format)
                    except Exception as e:
                        logger.exception(e)
                        logger.error('dump {} to {} error', self.path, self.format)


class BaseEdge():
    def __init__(self, a, b, type=''):
        self.source = a
        self.target = b
        self.label = ''
        self.type = [type] if type else []
        self.direction = ''
        self.context: PumlBase = None
        self.diagram: PumlDiagram = None

    def __or__(self, other: str):
        self.label = other
        return self

    def __gt__(self, other):
        if other in direction:
            self.direction = other
        else:
            self.type.append(other)
        return self

    def __lshift__(self, other: 'BaseNode'):
        node = self.target
        return node.context.make_edge(other, node, '<<')

    def __rshift__(self, other: 'BaseNode'):
        node = self.target
        return node.context.make_edge(node, other, '>>')

    def __sub__(self, other: 'BaseNode'):
        node = self.target
        return node.context.make_edge(node, other, '-')

    def __pow__(self, power, modulo=None):
        node = self.target
        return node.context.make_edge(node, power, '**')

    def to_puml(self):
        text = 'Rel({},{},"{}")'.format(self.source.id, self.target.id, self.label)
        return text


class BaseNode():
    def __init__(self, label, *args, alias=None):
        self._label = label.replace('\n', '\\n')
        self.extra = '\\n'.join(args)

        self.context = Context._cur_context
        self.context.add_node(self)
        self.diagram = Context.diagram
        self.id = self.context._rand_id()

        self.desc = args
        self._color = ''

        for line in inspect.getframeinfo(inspect.currentframe().f_back.f_back)[3]:
            line = str(line)
            m = re.search(r'(\w+)\s*=\s*', line)
            if m:
                self._var = m.group(1)
                if not self._label:
                    self._label = self._var
                self.id = self._var

    @property
    def label(self):
        text = self._label
        if self.extra:
            text += '\\n' + self.extra
        return text

    def color(self, color):
        self._color = color
        return self

    def refresh_context(self, context):
        self.context = Context._cur_context
        self.context.add_node(self)

    def to_puml(self) -> str:
        text = 'Node({},"{}")'.format(self.id, self.label)
        return text

    def __getattr__(self, other: 'BaseNode'):
        self.context.make_edge(other, self, '.')
        return other

    def __lshift__(self, other: 'BaseNode'):
        self.context.make_edge(other, self, '>>')
        return other

    def __rshift__(self, other: 'BaseNode'):
        return self.context.make_edge(self, other, '<<')

    def __sub__(self, other: 'BaseNode'):
        return self.context.make_edge(self, other, '-')

    def __pow__(self, power, modulo=None):
        return self.context.make_edge(self, power, '**')
