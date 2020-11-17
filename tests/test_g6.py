from pprint import pprint

from colour import Color

from diagramit.g6 import Helper, Template


def test_template():
    pass


def test_arch1():
    from diagramit.g6.arch import Arch, Layer
    with Arch() as a:
        with Layer('combo1') as g:
            g('1', '2', '3', '4')
        with Layer('combo2') as g:
            g('1', '2', '3', '4')
        with Layer() as r:
            r('1', '2', '3', '4')

    data = a.to_puml()
    pprint(data)
    h = Helper()
    h.output(Template.arch, 'dump.svg', data=data)


def test_arch2():
    from diagramit.g6.arch import Arch, Layer
    with Arch() as a:
        with Layer('combo1') as g:
            g('1', '2', '3', '4')
        with Layer('combo2') as g:
            g('1', '2', '3', '4')
        with Layer('combo3') as g:
            g('col1')
            g('col2')

    data = a.to_puml()
    pprint(data)
    h = Helper()
    h.output(Template.arch, 'dump.svg', data=data)


def test_arch3():
    from diagramit.g6.arch import Arch, Layer, Node
    grey = Color('grey').get_hex()
    purple = Color('Purple').get_hex()

    with Arch() as a:
        with Layer('combo1') as g:
            g(Node('color', fill=purple), )
            g('binary', 'apk', 'cpp', 'java')
        with Layer('combo2') as g:
            g('androguard', 'ida', 'tree-sitter', 'binary ninja')
            with Layer('inner') as inner:
                inner('test')
        with Layer('combo3') as g:
            g(*['cfg'] * 5)
            g(*['dfg'] * 5)
            g(*['code'] * 6)

    data = a.to_puml()
    # pprint(data)
    h = Helper()
    h.output(Template.arch, 'dump.svg', data=data)


def test_g6_helper():
    data = {
        'nodes': [
            {
                'id': "node1",
                'x': 250,
                'y': 150,
                'comboId': "combo",
            },
            {
                'id': "node2",
                'x': 350,
                'y': 150,
                'comboId': "combo",
            },
        ],
        'combos': [
            {
                'id': "combo",
                'label': "Combo",
            },
        ],
    }
    h = Helper()

    h.output(Template.arch, 'dump.svg', data=data)
