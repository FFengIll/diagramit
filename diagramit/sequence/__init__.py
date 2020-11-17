from diagramit.puml.diagram import Context
from diagramit.puml.diagram import Diagram
from diagramit.puml.note import NoteLink, NoteLeft, NoteRight, NoteOver
from diagramit.puml.utils import block_generator, line_generator, wrap_puml

__all__ = [
    'Sequence',
    'NoteLeft', 'NoteRight', 'NoteLink', 'NoteOver',
    'Actor', 'Participant', 'DB', 'Collection',
    'Active', 'Split', 'Loop', 'Group', 'Box'
]


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
        self.label = []
        self.type = type

    def __or__(self, other: str):
        self.label.append(other.replace('\n', '\\n'))
        return self

    def to_puml(self):
        text = '{}{}{}'.format(self.start.id, self.type, self.end.id)
        label = '\\n'.join(self.label)
        if label:
            text += ':{}'.format(label)
        return text


class Node():
    def __init__(self, label, *args, alias=None, type='participant'):
        self.label = label.replace('\n', '\\n')
        extra = '\\n'.join(args)
        if extra:
            self.label += '\\n' + extra
        self.context = Context._cur_context
        self.context.add_node(self)
        self.id = self.context._rand_id()
        self.type = type

    def to_puml(self):
        return '{} "{}" as {}'.format(self.type, self.label, self.id)

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(Edge(other, self, '->'))

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '->'))

    def __sub__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '-->'))


def NodeGen(type):
    def inner(*args, **kwargs):
        return Node(*args, **kwargs, type=type)

    return inner


# participant, e.g. a module
Participant = NodeGen('participant')
# Actor, e.g. a user
Actor = NodeGen('actor')
DB = NodeGen('database')
Collection = NodeGen('collections')

# group of some procedure
Group = block_generator('group {}', 'end')
# a loop box
Loop = block_generator('loop {}', 'end')
# box include some node, e.g. a box of some roles
Box = block_generator('box "{}"', 'end box')
# a split line
Split = line_generator('== {} ==', '')


# active some seq bar and deactive it after some process
def Active(node: Node):
    inner = block_generator('activate {}'.format(node.id), 'deactivate {}'.format(node.id))
    return inner('')
