from enum import Enum

from .context import Context
from .diagram import Diagram
from .utils import block_generator, line_generator, wrap_puml, output_puml


class Sequence(Diagram):

    def __init__(self, path=None, format='png', ):
        super().__init__(path, format)

    def __enter__(self):
        Context._context.put_nowait(Context._cur_context)
        Context._cur_context = self

    def __exit__(self, *args):
        context = Context._context.get_nowait()
        Context._cur_context = context

        text = self.to_puml()
        print(text)

        with open(self.path, 'w') as fd:
            fd.write(text)

        if self.format:
            output_puml(self.path, self.format)

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
        self.desc = desc
        self.alias = alias or Context.get_alias()
        self.context = Context._cur_context
        self.context.add_node(self)

    def to_puml(self):
        return 'participant "{}" as {}'.format(self.desc, self.alias)

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(Edge(other, self, '->'))

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '->'))

    def __sub__(self, other: 'Node'):
        return self.context.add_link(Edge(self, other, '-->'))


class NoteWhere(Enum):
    left = 'note left of'
    right = 'note right of'
    over = 'note over'


class _Note():
    def __init__(self, *args, site=''):
        nodes = set()
        desc = []
        for i in args:
            if isinstance(i, Node):
                nodes.add(i)
            else:
                desc.append(i)

        if len(nodes) < 1:
            raise Exception('must given node for note')

        self.desc = '\n'.join(desc)
        self.nodes = nodes
        self.site = site
        self.context = Context._cur_context
        self.context.add_note(self)

    def to_puml(self):
        if self.site == NoteWhere.over:
            n = ', '.join([n.alias for n in self.nodes])
        else:
            n = self.nodes.pop().alias

        text = '{} {}\n{}\nend note'.format(self.site, n, self.desc)
        return text


class NoteRight(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.right.value)


class NoteLeft(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.left.value)


class NoteOver(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.over.value)


Group = block_generator('group {}', 'end')
Loop = block_generator('loop {}', 'end')
Split = line_generator('== {} ==', '')


def Active(node: Node):
    inner = block_generator('activate {}'.format(node.alias), 'deactivate {}'.format(node.alias))
    return inner('')
