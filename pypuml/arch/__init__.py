from ..g6 import Helper
from ..g6.diagram import Diagram, Context
from typing import *
from copy import deepcopy
from math import floor, ceil

"""
需要根据上下文进行组装。
每次生成一个group，并将其中的每个node创建填入。
最终根据算法评估要如何布局每个group，从而设置node position。
"""

ystep = 100
xstep = 150
y_padding_step = 10
padding = 10


class Arch(Diagram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layers: List[Layer] = []
        self.player = -1

    @property
    def raw(self):
        return len(self.layers)

    @property
    def current_layer(self):
        return self.layers[self.player]

    def add_layer(self, l):
        self.layers.append(l)
        self.player += 1

    def back_layer(self):
        self.player -= 1

    def __enter__(self):
        super(Arch, self).__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        res = super(Arch, self).__exit__()

    def add_combo(self, c):
        self.layers.append(c)

    def to_puml(self):
        arch = ArchLayout(self)
        arch.preprocess()
        res = arch.process()
        return res


class ArchLayout():
    def __init__(self, context):
        self.y = 100
        self.y_padding = 5
        self.x_padding = 20
        self.x = 100
        self.ns = []
        self.cs = []
        self.context: Arch = context

    def get_y_padding(self):
        self.y_padding += y_padding_step
        return self.y_padding

    def get_y(self, idx):
        return self.y + ystep * idx + self.y_padding

    def get_x(self, idx):
        return self.x + xstep * idx

    def preprocess(self):

        """
        - 统计各层次的数据
        - 对于每一层，首先平均，并尽可能维持算子
            - 2 * raw <= col <= 3 * raw
            - 即 4行图，纵向列数目在 8~12，由此维持一个美观度（长方形）
        - 对于内部，尽可能按比例拆分
            - 首先尝试 raw 数目，随后进行拆分
        - 最终重新扩展每一层，保证尽可能填充完毕
        :return:
        """
        max_col = 0
        for l in self.context.layers:
            max_col = max(max_col, l.col)

        if max_col < 3 * self.context.raw:
            return
        else:
            pass

            if 2 * self.context.raw < max_col:
                return

    def process(self):
        res = dict(nodes=self.ns, combos=self.cs)

        # 首先处理层级，显然，每一层有一个combo，对应需要设置pos y
        # 其次需要处理content，横向扩展，所以需要设置pos x
        # 其下可能有node，所以需要设置pos x
        # 其下可能有combo，所以需要再另行设置pos

        for idx, layer in enumerate(self.context.layers):
            layer.y = self.get_y(idx)
            tmp = self.translate_layer(layer)

        res = deepcopy(res)
        self.ns.clear()
        self.cs.clear()
        return res

    def translate_node(self, i: 'Node', parent=None):
        res = dict(
            id=i.alias,
            comboId=parent.alias,
            label=i.desc,
            x=i.x,
            y=i.y
        )
        self.ns.append(res)

        return res

    def translate_combo(self, combo: 'Combo', parent=None):
        for idx, n in enumerate(combo.nodes):
            n.x, n.y = combo.get_x(idx), combo.y
            tmp = self.translate_node(n, parent=parent)

        res = dict(
            id=combo.alias,
            label=combo.desc,
            y=combo.y,
        )
        if combo.x:
            res['x'] = combo.x
        return res

    def translate_layer(self, layer: 'Layer'):

        if len(layer.combos) <= 1:
            for idx, combo in enumerate(layer.combos):
                combo.x, combo.y = self.get_x(idx), layer.y
                combo.desc = layer.desc
                res = self.translate_combo(combo, parent=combo)

                self.cs.append(res)
        else:
            res = dict(
                id=layer.alias,
                label=layer.desc,
            )
            self.cs.append(res)

            y_padding = self.get_y_padding()

            # for each inner combo, need to consider left pad * 2
            x_padding = padding * 2

            # process inner combo
            for idx, combo in enumerate(layer.combos):
                combo.x, combo.y = self.get_x(idx) + x_padding, layer.y + y_padding
                res = self.translate_combo(combo, parent=combo)

                if combo.parent:
                    res['parentId'] = combo.parent.alias
                self.cs.append(res)


class Node():
    def __init__(self, desc, parent: 'Layer' = None, alias=None):
        self.parent = parent

        self.desc = desc
        self.alias = 'node' + Context._cur_context.get_alias(alias or desc)
        self.x = None
        self.y = None


class PosObj():
    def get_y(self, idx):
        return self.y + ystep * idx

    def get_x(self, idx):
        return self.x + xstep * idx


class Layer(PosObj):
    def __init__(self, desc='', *args, alias=None):
        self.context: Arch = Context._cur_context
        self.context.add_layer(self)
        self.desc = desc
        self.alias = 'layer_' + self.context.get_alias(alias or desc)
        self.combos: List[Combo] = []
        self.x = None
        self.y = None

    @property
    def col(self):
        res = 0
        for c in self.combos:
            tmp = c.col
            res += tmp
        return res

    def __call__(self, *args, desc=''):
        nodes = []
        for i in args:
            n = Node(i, self)
            nodes.append(n)
        c = Combo(*nodes, parent=self, desc=desc)
        self.combos.append(c)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Combo(PosObj):
    def __init__(self, *args, parent=None, alias=None, desc=''):
        self.desc = desc
        self.parent = parent
        self.alias = 'combo_' + Context._cur_context.get_alias(alias or desc)
        self.nodes = args
        self.x = None
        self.y = None
        self.raw = 1

    @property
    def col(self):
        return ceil(len(self) / self.raw)

    def __len__(self):
        return len(self.nodes)
