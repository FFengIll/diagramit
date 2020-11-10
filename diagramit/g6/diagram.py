from diagramit.puml.context import Context, alias_gen
from diagramit.puml.utils import assert_format, output_puml, desc2alias


class Diagram():
    def __init__(self, path=None, format='png', show=False, **kwargs):
        self.path = path
        self.text = []
        self.ns = []
        self.es = []
        self.format = format
        assert_format(format)

        self.show = show

        self.alias_set = set()
        self._alias_gen = alias_gen()

    def get_alias(self, alias=None):
        if alias:
            alias = desc2alias(alias)

            if alias:
                if alias in self.alias_set:
                    alias = alias + next(self._alias_gen)
                    self.alias_set.add(alias)
                else:
                    self.alias_set.add(alias)
                return alias

        return next(self._alias_gen)

    def __enter__(self):
        Context._context.put_nowait(Context._cur_context)
        Context._cur_context = self

    def __exit__(self, *args):
        context = Context._context.get_nowait()
        Context._cur_context = context

        text = self.to_puml()
        # print(text)

        if self.show:
            print(text)
        elif self.path:
            with open(self.path, 'w') as fd:
                fd.write(text)

            if self.format:
                output_puml(self.path, self.format)

        return text

    def add_note(self, p):
        self.text.append(p)

    def add_node(self, p):
        self.ns.append(p)
        self.text.append(p)

    def add_link(self, edge):
        self.text.append(edge)
        return edge

    def add_text(self, text):
        self.text.append(text)

    def to_puml(self):
        raise NotImplementedError
