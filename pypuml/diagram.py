from .utils import assert_format


class Diagram():
    def __init__(self, path=None, format='png', ):
        self.path = path
        self.text = []
        self.ns = []
        self.es = []
        self.format = format
        assert_format(format)

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
