from enum import Enum

from .context import Context


class NoteWhere(Enum):
    left = 'note left of'
    right = 'note right of'
    over = 'note over'
    link = 'note on link'


class _Note():
    def __init__(self, *args, site='', no_node=False):
        nodes = set()
        desc = []
        for i in args:
            if isinstance(i, str):
                desc.append(i)
            else:
                nodes.add(i)

        if not no_node and len(nodes) <= 0:
            raise Exception('must given node for note')

        self.desc = '\n'.join(desc)
        self.nodes = nodes
        self.site = site
        self.context = Context._cur_context
        self.context.add_note(self)

    def to_puml(self):
        if self.site == NoteWhere.over:
            n = ', '.join([n.alias for n in self.nodes])
        if self.site == NoteWhere.link:
            n = ''
        else:
            n = self.nodes.pop().alias

        text = '{} {}\n{}\nend note'.format(self.site.value, n, self.desc)
        return text


class NoteRight(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.right)


class NoteLeft(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.left)


class NoteOver(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.over)


class NoteLink(_Note):
    def __init__(self, *args):
        super().__init__(*args, site=NoteWhere.link, no_node=True)
