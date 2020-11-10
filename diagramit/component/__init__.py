from enum import Enum

from ..puml.context import Context
from ..puml.diagram import Diagram
from ..puml.utils import block_generator, line_generator, wrap_puml, output_puml


class Component(Diagram):

    def __init__(self, path=None, format='png', **kwargs):
        super().__init__(path, format, **kwargs)

    def to_puml(self):
        content = []
        for i in self.text:
            if isinstance(i, str):
                content.append(i)
            else:
                content.append(i.to_puml())
        text = wrap_puml(content)
        return text


class Edge():
    def __init__(self, a, b, type='->'):
        self.start = a
        self.end = b
        self.desc = ''
        self.type = type

    def __or__(self, other: str):
        self.desc = other
        return self

    def to_puml(self):
        text = '{}{}{}'.format(self.start.alias, self.type, self.end.alias)
        if self.desc:
            text += ':{}'.format(self.desc)
        return text


class Node():
    def __init__(self, desc, alias=None):
        self.desc = desc.replace('\n', '\\n')
        self.context = Context._cur_context
        self.context.add_node(self)
        self.alias = self.context.get_alias(alias or desc)

    def to_puml(self):
        return '[{}] as {}'.format(self.desc, self.alias)

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(Edge(other, self, '->'))

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '->'))

    def __sub__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '-->'))


Group = block_generator('package "{}" {{', '}}')
Package = Group
Cloud = block_generator('cloud {{', '}}')
DB = block_generator('database "{}" {{', '}}')
