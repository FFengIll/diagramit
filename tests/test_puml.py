def test_c4():
    from diagramit.puml.c4 import Container, System_Ext, Container_Boundary, Boundary, C4Diagram, Component, ContainerDB
    with C4Diagram('output/test_c4.puml', format='svg', show=False) as seq:
        cli = Container("Command Line Interface ", "python", "Provides alchemy functionality via a CLI.")
        neo4j = ContainerDB("Neo4j Database", "Graph Database Schema", "Stores graph data which comes from the analysis result.")

        celery = System_Ext("Celery System", "Manage tasks via a distributed queue system.")
        cli = System_Ext("CLI", "Manage tasks via a distributed queue system.")
        bn = System_Ext("Binary Ninja", "")
        ida = System_Ext("IDA CLI", "")
        ag = System_Ext("Androguard", "")

        with Container_Boundary("Alchemy Analysis") as ana:
            with Boundary("label") as cpp_ext:
                cpp = Component("C/CPP Source Code Analysis", "python", "analyse cpp code via ANTLR and PCPP")
                graph_cpp = Component("Graph DAO", "python", "Define Graph object including Node / Label / Link for each target")
                cypher_cpp = Component("Neo4j Cypher", "Pythhon", "Define cypher statements for each object in Graph")

            with Boundary("label") as bin_ext:
                bin = Component("Binary Analysis", "python", "analyse binary file via Binary Ninja")
                graph_bin = Component("Graph DAO", "python", "Define Graph object including Node / Label / Link for each target")
                cypher_bin = Component("Neo4j Cypher", "Pythhon", "Define cypher statements for each object in Graph")

            with  Boundary("label") as apk_ext:
                apk = Component("Apk Analysis", "python", "analyse apk / dex file via androguard")
                graph_apk = Component("Graph DAO", "python", "Define Graph object including Node / Label / Link for each target")
                cypher_apk = Component("Neo4j Cypher", "Pythhon", "Define cypher statements for each object in Graph")

        apk >> ag | "1a"
        apk >> apk | "1b"
        apk >> graph_apk | "2a"
        graph_apk >> cypher_apk | "2b"
        graph_apk >> neo4j | "3"

        cpp >> graph_cpp | "1"
        cpp >> cypher_cpp | "2"
        cpp >> neo4j | "3"

        bin >> graph_bin | "1"
        bin >> cypher_bin | "2"
        bin >> neo4j | "3"


def test_comp():
    from diagramit.puml.component import Component, Group, Node, Cloud, DB
    with Component('output/test_component.puml', format='svg', show=False) as comp:
        with Group('Test'):
            Node('a')
            Node('b')

        with Cloud():
            Node('cloud')

        with DB():
            Node('db')


def test_state():
    from diagramit.puml.note import NoteLink, NoteLeft
    from diagramit.puml.state import State, Node, StartNode, CompState, TerminateNode, NoteNode

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
            a >> TerminateNode() | 'end'
            NoteNode('test note')


def test_sequence():
    from diagramit.puml.note import NoteOver, NoteRight, NoteLeft
    from diagramit.puml.sequence import Node, Split, Sequence, Active, Group
    with Sequence('output/test_seq.puml', format='svg', show=False) as seq:
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
