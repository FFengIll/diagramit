from diagramit.puml.diagram import PumlDiagram, BaseNode, BaseEdge
from diagramit.puml.note import NoteLink, NoteLeft, NoteRight, NoteOver
from diagramit.puml.utils import block_generator, line_generator, wrap_puml

__all__ = [
    'SequenceDiagram',
    'NoteLeft', 'NoteRight', 'NoteLink', 'NoteOver',
    'Actor', 'Participant', 'DB', 'Collection',
    'Active', 'Split', 'Loop', 'Group', 'Box'
]


class SequenceDiagram(PumlDiagram):

    def __init__(self, path=None, format='png', **kwargs):
        super().__init__(path, format, **kwargs)
        self.Edge = Edge

        self.op_map = {
            '>>': '->',
            '<<': '->',
            '-': '',
            '**': '',
        }

    def to_puml(self):
        content = []
        for i in self.text:
            if isinstance(i, str):
                content.append(i)
            else:
                content.append(i.to_puml())
        text = wrap_puml(content)
        return text


class Edge(BaseEdge):
    def __init__(self, a, b, type='->'):
        super(Edge, self).__init__(a, b, type=type)

        self.label = []
        self.type = type

    def __or__(self, other: str):
        self.label.append(other.replace('\n', '\\n'))
        return self

    def to_puml(self):
        text = '{}{}{}'.format(self.source.id, self.type, self.target.id)
        label = '\\n'.join(self.label)
        if label:
            text += ':{}'.format(label)
        return text


class Node(BaseNode):
    def __init__(self, label, *args, type='participant'):
        super(Node, self).__init__(label, *args)
        self.type = type

    def to_puml(self):
        return '{} "{}" as {}'.format(self.type, self.label, self.id)

    def __sub__(self, other: 'Node'):
        # FIXME: here is a trick
        self.diagram.add_link(self.diagram.Edge(self, other, '->'))
        return self.diagram.add_link(self.diagram.Edge(other, self, '-->'))


def NodeHelper(type):
    def inner(*args, **kwargs):
        return Node(*args, **kwargs, type=type)

    return inner


# participant, e.g. a module
Participant = NodeHelper('participant')
# Actor, e.g. a user
Actor = NodeHelper('actor')
DB = NodeHelper('database')
Collection = NodeHelper('collections')

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
