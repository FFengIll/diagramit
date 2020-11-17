from diagramit.puml.diagram import Diagram, Context
from diagramit.puml.utils import block_generator, wrap_puml


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
        self.label = ''
        self.type = type

    def __or__(self, other: str):
        self.label = other
        return self

    def to_puml(self):
        text = '{}{}{}'.format(self.start.id, self.type, self.end.id)
        if self.label:
            text += ':{}'.format(self.label)
        return text


class Node():
    def __init__(self, label, alias=None):
        self.label = label.replace('\n', '\\n')
        self.context = Context._cur_context
        self.context.add_node(self)
        self.id = self.context.get_alias(alias or label)

    def to_puml(self):
        return '[{}] as {}'.format(self.label, self.id)

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
