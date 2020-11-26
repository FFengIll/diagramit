from diagramit.puml.diagram import PumlDiagram, BaseNode, BaseEdge
from diagramit.puml.utils import block_generator, wrap_puml


class ComponentDiagram(PumlDiagram):

    def __init__(self, path=None, format='png', **kwargs):
        super().__init__(path, format, **kwargs)
        self.Edge = Edge

        self.op_map = {
            '>>': '->',
            '<<': '<-',
            '-': '--',
            # '**': '',
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

        self.label = ''
        self.type = type

    def __or__(self, other: str):
        self.label = other
        return self

    def to_puml(self):
        text = '{}{}{}'.format(self.source.id, self.type, self.target.id)
        if self.label:
            text += ':{}'.format(self.label)
        return text


class Node(BaseNode):
    def __init__(self, label, *args):
        super(Node, self).__init__(label, *args)

    def to_puml(self):
        return '[{}] as {}'.format(self.label, self.id)


Package = block_generator('package "{}" {{', '}}')
Cloud = block_generator('cloud {{', '}}')
DB = block_generator('database "{}" {{', '}}')
