def test_comp():
    from pypuml.component import Component, Group, Node, Cloud, DB

    with Component('output/test_component.puml', format='svg', show=False) as comp:
        with Group('Test'):
            Node('a')
            Node('b')

        with Cloud():
            Node('cloud')

        with DB():
            Node('db')


def test_state():
    from pypuml.puml.note import NoteLink, NoteLeft
    from pypuml.state import State, Node, StartNode, CompState, EndNode, NoteNode

    with State('output/test_state.puml', format='svg', show=False) as seq:
        a = Node('A')
        b = Node('B')
        field = Node('Field', 'f1', 'f2')
        NoteLeft(a, 'test note left')

        StartNode() >> a

        a >> a | 'self' > '#red' > 'up'
        a >> b | 'line' > 'dotted'
        b - a | 'dash' > 'dotted'
        b ** a | 'dot'
        NoteLink('test note on link')

        with CompState('test comp state'):
            a >> EndNode() | 'end'

            # with Active(b):
            #     b >> a | 'line'
            #
            NoteNode('test note')


def test_sequence():
    from pypuml.puml.note import NoteOver, NoteRight, NoteLeft
    from pypuml.sequence import Node, Split, Sequence, Active, Group
    with Sequence('output/test_seq.puml', format='svg', show=True) as seq:
        a = Node('A')
        b = Node('B')

        a >> a | 'self'

        a >> b | 'line'
        b >> a | 'line'
        b - a | 'dot line'

        Split('split')

        with Active(a):
            NoteRight(a, 'note right')

            a >> b | 'line'
            with Active(b):
                b >> a | 'line'

            NoteLeft(a, 'note left')
            NoteOver(a, b, 'note over')

        with Group('group'):
            a >> b
