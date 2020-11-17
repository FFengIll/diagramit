import uuid

from diagramit.puml.diagram import Context
from diagramit.puml.diagram import Diagram
from diagramit.puml.utils import block_generator, wrap_puml, direction


def reuse(*args):
    for i in args:
        i: 'Node'
        i.refresh_context(Context._cur_context)


Context.make_negative()


class C4Diagram(Diagram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _rand_id():
        return 'N_' + uuid.uuid4().hex

    def to_puml(self):
        headers = [
            '!include https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/release/1-0/C4_Component.puml',
            '!include https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/release/1-0/C4_Context.puml',
            '!include https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/release/1-0/C4_Container.puml',

            'LAYOUT_WITH_LEGEND()'

        ]
        tails = [

        ]
        content = []

        for i in headers:
            content.append(i)

        for i in self.text:
            if isinstance(i, str):
                content.append(i)
            else:
                content.append(i.to_puml())
        text = wrap_puml(content)
        return text


class Edge():
    def __init__(self, a, b, type=''):
        self.source = a
        self.target = b
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
        text = 'Rel({},{},"{}")'.format(self.source.id, self.target.id, self.label)
        return text


class Node():
    def __init__(self, label, *args, alias=None):
        self.label = label
        self.desc = args
        self.context = Context._cur_context
        self.context.add_node(self)
        self.id = C4Diagram._rand_id()

    def refresh_context(self, context):
        self.context = Context._cur_context
        self.context.add_node(self)

    def to_puml(self):
        base = 'state "{}" as {}'.format(self.label, self.id)
        fields = ['{} : {}'.format(self.id, i) for i in self.desc]
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
State = Node


class C4Node(Node):
    desc_limit = 2
    node_type = 'UNKNOWN'

    def to_puml(self):
        labels = []
        for i in self.desc:
            labels.append('"{}"'.format(i))

        text = '{}({}, {}, {})'.format(self.node_type, self.id, self.label, ','.join(labels[:self.desc_limit]))
        return text


class Container(C4Node):
    desc_limit = 2
    node_type = 'Container'


class ContainerDB(C4Node):
    desc_limit = 2
    node_type = 'ContainerDb'


class Person(C4Node):
    desc_limit = 2
    node_type = 'Person'


class System(C4Node):
    desc_limit = 2
    node_type = 'System'


class System_Ext(C4Node):
    desc_limit = 2
    node_type = 'System_Ext'


class Component(C4Node):
    desc_limit = 2
    node_type = 'Component'


def Container_Boundary(label):
    inner = block_generator('Container_Boundary({}, "{}") {{', '}}')
    return inner(C4Diagram._rand_id(), label)


def System_Boundary(label):
    inner = block_generator('System_Boundary({}, "{}") {{', '}}')
    return inner(C4Diagram._rand_id(), label)


def Boundary(label):
    inner = block_generator('Container_Boundary({}, "{}") {{', '}}')
    return inner(C4Diagram._rand_id(), label)
