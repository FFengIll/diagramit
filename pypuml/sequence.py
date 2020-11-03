import os
from contextlib import contextmanager
from enum import Enum
from queue import LifoQueue as Stack


def alias_gen():
    while 1:
        yield 'p{}'.format(Context._count)
        Context._count += 1


_alias = alias_gen()


class Context():
    _count = 1

    _context = Stack()
    _cur_context = None


class Sequence():
    _format = ['png', 'svg', 'txt', 'pdf', None]

    def __init__(self, path=None, format='png', ):
        self.path = path
        self.text = []
        self.ns = []
        self.es = []
        self.format = format
        assert format in self._format

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
            os.system('plantuml {} -t{}'.format(self.path, self.format))

    def to_puml(self):
        content = []
        for i in self.text:
            if isinstance(i, str):
                content.append(i)
            else:
                content.append(i.to_puml())
        text = '@startuml\n{}\n@enduml'.format('\n'.join(content))
        return text

    def add_note(self, p):
        self.text.append(p)

    def add_node(self, p):
        self.ns.append(p)
        self.text.append(p)

    def add_link(self, a: 'Node', b: 'Node', type=None):
        res = Edge(a, b, type)
        self.text.append(res)
        return res

    def add_text(self, text):
        self.text.append(text)


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
        self.alias = alias or next(_alias)
        self.context = Context._cur_context
        self.context.add_node(self)

    def to_puml(self):
        return 'participant "{}" as {}'.format(self.desc, self.alias)

    def __lshift__(self, other: 'Node'):
        return self.context.add_link(other, self, '->')

    def __rshift__(self, other: 'Node'):
        return self.context.add_link(self, other, '->')

    def __sub__(self, other: 'Node'):
        return self.context.add_link(self, other, '-->')


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


def block_generator(entry, exit):
    @contextmanager
    def inner(desc=''):
        context = Context._cur_context
        context.add_text(entry.format(desc))
        try:
            yield None
        finally:
            context.add_text(exit.format(desc))

    return inner


def line_generator(entry, exit):
    def inner(desc=''):
        context = Context._cur_context
        context.add_text(entry.format(desc))
        context.add_text(exit.format(desc))

    return inner


Group = block_generator('group {}', 'end')
Loop = block_generator('loop {}', 'end')
Split = line_generator('== {} ==', '')


def Active(node: Node):
    inner = block_generator('activate {}'.format(node.alias), 'deactivate {}'.format(node.alias))
    return inner('')
