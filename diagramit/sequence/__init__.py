from diagramit.puml.context import Context
from diagramit.puml.diagram import Diagram
from diagramit.puml.utils import block_generator, line_generator, wrap_puml


class Sequence(Diagram):

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
        self.label = other.replace('\n', '\\n')
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
        self.id = self.context._rand_id()

    def to_puml(self):
        return 'participant "{}" as {}'.format(self.label, self.id)

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(Edge(other, self, '->'))

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '->'))

    def __sub__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '-->'))


Participant = Node
Role = Node

Group = block_generator('group {}', 'end')
Loop = block_generator('loop {}', 'end')
Box = block_generator('box "{}"', 'end box')
Split = line_generator('== {} ==', '')


def Active(node: Node):
    inner = block_generator('activate {}'.format(node.id), 'deactivate {}'.format(node.id))
    return inner('')
