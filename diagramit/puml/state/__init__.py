from diagramit.puml.diagram import Context
from diagramit.puml.diagram import Diagram
from diagramit.puml.utils import block_generator, wrap_puml, direction


class State(Diagram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def __init__(self, a, b, type=''):
        self.start = a
        self.end = b
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
        text = '{}{}{}'.format(self.start.id, modifier, self.end.id)
        if self.label:
            text += ' : {}'.format(self.label)
        return text


class Node():
    def __init__(self, label, *args, alias=None):
        self.label = label
        self.fields = args
        self.context = Context._cur_context
        self.context.add_node(self)
        self.id = self.context._rand_id()

    def to_puml(self):
        base = 'state "{}" as {}'.format(self.label, self.id)
        fields = ['{} : {}'.format(self.id, i) for i in self.fields]
        res = '{}\n{}'.format(base, '\n'.join(fields))
        return res

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(Edge(other, self, ''))

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, ''))

    def __sub__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, 'dashed'))

    def __pow__(self, power, modulo=None):
        return self.context.add_link(Edge(self, power, 'dotted'))


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


def CompState(label: str):
    label = label.replace(' ', '_')
    inner = block_generator('state {} {{', '}}')
    return inner(label)
