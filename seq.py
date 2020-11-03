from pypuml import *

with Sequence('./test_seq.puml', format='svg') as seq:
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
