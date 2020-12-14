from diagramit.puml.diagram import PumlDiagram, BaseNode, BaseEdge
from diagramit.puml.note import NoteLeft, NoteRight
from diagramit.puml.utils import block_generator, wrap_puml, direction

__all__ = [
    'NoteLeft', 'NoteRight',
    'StateDiagram',
    'CompState', 'Empty',
    'StartNode', 'Node', 'NoteNode', 'TerminateNode'
]


class StateDiagram(PumlDiagram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simple = kwargs.get('simple', True)
        self.Edge = Edge

        self.op_map = {
            '>>': '',
            '<<': '',
            '-': 'dashed',
            '**': 'dotted',
            '.': 'dotted'

        }

    def to_puml(self):
        content = []
        if self.mix:
            content.append('allowmixing')
        if self.simple:
            content.append('hide empty description')

        for i in self.text:
            if isinstance(i, str):
                content.append(i)
            else:
                content.append(i.to_puml())
        text = wrap_puml(content)
        return text


class Edge(BaseEdge):
    def __init__(self, a, b, type=''):
        super(Edge, self).__init__(a, b, type=type)

        self.label = ''
        self.type = [type] if type else []
        self.direction = ''

    def __or__(self, other: str):
        self.label = other
        return self

    def __gt__(self, other):
        if other in direction:
            self.direction = other
        else:
            self.type.append(other)
        return self

    def to_puml(self):
        if self.type:
            modifier = '-{}[{}]->'.format(self.direction, ','.join(self.type))
        else:
            modifier = '-->'
        text = '{}{}{}'.format(self.source.id, modifier, self.target.id)
        if self.label:
            text += ' : {}'.format(self.label)
        return text


class Node(BaseNode):
    def __init__(self, label='', *args, fields=[], alias=None):
        super(Node, self).__init__(label, *args)
        self.fields = fields

    def to_puml(self):
        base = 'state "{}" as {}'.format(self.label, self.id)
        if self._color:
            base = '{} {}'.format(base, self._color)
        fields = ['{} : {}'.format(self.id, i) for i in self.fields]
        res = '{}\n{}'.format(base, '\n'.join(fields))
        return res


class _EndNode(Node):
    def __init__(self):
        super().__init__('', alias='[*]')

    def to_puml(self):
        return ''

    def __call__(self, *args, **kwargs):
        return self


StartNode = _EndNode
TerminateNode = _EndNode


class NoteNode(Node):
    def to_puml(self):
        text = 'note "{}" as {}'.format(self.label, self.id)
        return text


Empty = block_generator('', '')


def Package(label):
    from ..diagram import Context
    Context.diagram.mix = True
    return block_generator('package "{}" {{', '}}')(label)


def Box(label):
    from ..diagram import Context
    Context.diagram.mix = True
    return block_generator('rectangle "{}" {{', '}}')(label)


def CompState(label: str):
    label = label.replace(' ', '_')
    inner = block_generator('state {} {{', '}}')
    return inner(label)
