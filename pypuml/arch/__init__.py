from ..g6.diagram import Diagram, Context
from math import ceil
from typing import *

import loguru
from functools import cached_property

from ..g6.diagram import Diagram, Context

logger = loguru.logger
"""
需要根据上下文进行组装。
每次生成一个group，并将其中的每个node创建填入。
最终根据算法评估要如何布局每个group，从而设置node position。
"""

y_padding_step = 10
padding = 10

node_width = 100
node_height = 30

node_space = padding * 2
combo_space = padding * 4
layer_space = padding * 2

ystep = (node_height + padding * 2) + padding + (padding * 2)
xstep = node_width + node_space
inner_ystep = node_height + padding


class Arch(Diagram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layers: List[Layer] = []
        self.player = -1

        self.x = 100
        self.y = 100
        self.x_padding = 20
        self.y_padding = 5

    @property
    def raw(self):
        return len(self.layers)

    @property
    def current_layer(self):
        return self.layers[self.player]

    def get_layer_x(self, idx):
        return self.x

    def get_layer_y(self, idx):
        # 针对y，需要计算layer的space/padding，计算combo的space/padding，计算inner combo padding
        if idx - 1 >= 0:
            layer = self.layers[idx - 1]
            base = layer.y
            raw = layer.raw
            pad = layer_space + padding * 2 + \
                  raw * node_height + (raw - 1) * node_space + \
                  (padding * 2 if len(layer.combos) <= 1 else padding * 3)
            res = base + pad
            logger.info(res)
        else:
            base = self.y
            res = base
            logger.info(res)

        return res

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
        arch.process()
        res = arch.generate()
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
        return self.x

    def preprocess(self):

        """
        - 统计各层次的数据
        - 对于每一层，首先平均，并尽可能维持算子
            - 2 * raw <= col <= 3 * raw
            - 即 4行图，纵向列数目在 8~12，由此维持一个美观度（长方形）
        - 其次，不能让整体宽度超过 6
        - 对于内部，尽可能按比例拆分
            - 首先尝试 raw 数目，随后进行拆分
        - 最终重新扩展每一层，保证尽可能填充完毕
        :return:
        """
        max_col = 0
        max_raw = self.context.raw
        for l in self.context.layers:
            max_col = max(max_col, l.col)

        if max_col <= 6:
            # 已经足够均衡了，可以直接开始后续步骤
            return
        else:
            # 宽度过分大，需要拆分combo
            for layer in self.context.layers:
                if layer.col > 6:
                    # 对于比较不均衡的部分，直接拆分
                    for combo in layer.combos:
                        combo.raw += 1

            self.preprocess()

    def process(self):

        # 首先处理层级，显然，每一层有一个combo，对应需要设置pos y
        # 其次需要处理content，横向扩展，所以需要设置pos x
        # 其下可能有node，所以需要设置pos x
        # 其下可能有combo，所以需要再另行设置pos

        self.preprocess()

        for idx, layer in enumerate(self.context.layers):
            logger.info(layer)
            layer.x = self.context.get_layer_x(idx)
            layer.y = self.context.get_layer_y(idx)
            self.layout_layer(layer)
            # idx += layer.raw

        self.postprocess()

        return self

    def postprocess(self):
        """
        后处理每一层，这一次主要目的是`展开每一层，补全空隙，生成方正的结构`
        :return:
        """

        max_width = 0
        max_col = 0
        for _, layer in enumerate(self.context.layers):
            max_width = max(max_width, layer.width)
            max_col = max(max_col, layer.col)

        for _, layer in enumerate(self.context.layers):
            col = layer.col
            logger.info('layer "{}" width={}', layer, layer.width)

            delta = max_width - layer.width
            if delta:
                layer.extend_space(delta)

            # if col > 1:
            #     pad = (max_width - layer.width) / (col)
            #     for combo in layer.combos:
            #         for idx, n in enumerate(combo.nodes[1:]):
            #             n.x += pad * (idx + 1)
            # else:
            #     pass

    def layout_combo(self, combo: 'Combo', parent=None):
        for idx, n in enumerate(combo.nodes):
            n.x = combo.get_node_x(idx) + node_space
            n.y = combo.get_node_y(idx)

        res = dict(
            id=combo.alias,
            label=combo.desc,
            y=combo.y,
        )
        if combo.x:
            res['x'] = combo.x
        return res

    def layout_layer(self, layer: 'Layer'):

        if len(layer.combos) <= 1:
            # 注意：对于单层单combo，直接用combo作为这个层级即可
            for idx, combo in enumerate(layer.combos):
                combo.x, combo.y = layer.get_combo_x(idx), layer.get_combo_y(None)
                combo.desc = layer.desc
                res = self.layout_combo(combo, )

                self.cs.append(res)
        else:
            # 注意：对于单层多combo，需要额外附加一个parent（或许以后可以去除）
            res = dict(
                id=layer.alias,
                label=layer.desc,
            )
            self.cs.append(res)

            # process inner combo
            # 由于可能拆分成多个层级，所以需要妥善构造增量
            # 对于y轴，（内外）记录并构造每一层的y
            # 对于x轴，需要内部记录并构造每一层x

            xidx = 0
            for _, combo in enumerate(layer.combos):
                combo.x = layer.get_combo_x(xidx) + node_space
                combo.y = layer.get_combo_y(None) + layer_space
                xidx += combo.col

                res = self.layout_combo(combo)

                if combo.parent:
                    res['parentId'] = combo.parent.alias
                self.cs.append(res)

    def generate_node(self, node: 'Node', parent=None):
        res = dict(
            id=node.alias,
            comboId=parent.alias,
            label=node.desc,
            x=node.x,
            y=node.y
        )
        self.ns.append(res)

        return res

    def generate_combo(self, combo: 'Combo', parent=None):
        for idx, n in enumerate(combo.nodes):
            self.generate_node(n, combo)

        res = dict(
            id=combo.alias,
            label=combo.desc,
            y=combo.y,
        )
        if combo.x:
            res['x'] = combo.x
        return res

    def generate_layer(self, layer: 'Layer'):

        if len(layer.combos) <= 1:
            # 注意：对于单层单combo，直接用combo作为这个层级即可
            for idx, combo in enumerate(layer.combos):
                res = self.generate_combo(combo, )
                self.cs.append(res)
        else:
            # 注意：对于单层多combo，需要额外附加一个parent（或许以后可以去除）
            res = dict(
                id=layer.alias,
                label=layer.desc,
            )
            self.cs.append(res)

            # process inner combo
            # 由于可能拆分成多个层级，所以需要妥善构造增量
            # 对于y轴，（内外）记录并构造每一层的y
            # 对于x轴，需要内部记录并构造每一层x

            xidx = 0

            for cidx, combo in enumerate(layer.combos):
                xidx += combo.col
                res = self.generate_combo(combo)

                if combo.parent:
                    res['parentId'] = combo.parent.alias
                self.cs.append(res)

    def generate(self):
        """
        后处理每一层，这一次主要目的是`展开每一层，补全空隙，生成方正的结构`
        :return:
        """
        self.ns.clear()
        self.cs.clear()

        res = dict(nodes=self.ns, combos=self.cs)
        for _, layer in enumerate(self.context.layers):
            self.generate_layer(layer)
        return res


class Layer():
    def __init__(self, desc='', *args, alias=None):
        self.context: Arch = Context._cur_context
        self.context.add_layer(self)
        self.desc = desc
        self.alias = 'layer_' + self.context.get_alias(alias or desc)
        self.combos: List[Combo] = []
        self.x = None
        self.y = None

    def extend_space(self, delta):
        count = 0
        for c in self.combos:
            count += c.col - 1
        space = delta / count

        idx = 1
        for c in self.combos:
            for n in c.nodes[1:]:
                n.x += space * idx
                idx += 1

    @cached_property
    def width_legacy(self):
        col = self.col
        cs = len(self.combos)

        # 计算边缘，计算combo间space，计算node，计算node间space
        pad = combo_space * (cs - 1) + col * node_width
        for c in self.combos:
            pad += (len(c.nodes) - 1) * node_space

        return pad

    @cached_property
    def width(self):
        """
        简化算法，直接通过首尾的节点去计算整个layer的宽度
        :return:
        """
        # 最左点与最右点之间
        first, last = self.combos[0], self.combos[-1]
        left = first.nodes[0].x
        right = last.nodes[min(last.col - 1, len(last.nodes))].x + node_width

        cs = len(self.combos)
        # layer 两端
        padding1 = padding * 2
        # layer combo 两端
        space1 = 0 if cs <= 1 else padding * 2
        # layer combo 之间
        space2 = 0 if cs <= 1 else (combo_space - padding * 2) * (cs - 1)

        return right - left + padding1 + space1 + space2

    def get_combo_y(self, idx):
        return self.y

    def get_combo_x(self, idx):
        if idx > 0:
            return self.x + xstep * idx + combo_space
        else:
            return self.x + xstep * idx

    @property
    def col(self):
        res = 0
        for c in self.combos:
            tmp = c.col
            res += tmp
        return res

    @property
    def raw(self):
        if self.combos:
            return self.combos[0].raw
        return 0

    def __str__(self):
        return self.alias

    def __repr__(self):
        return str(self)

    def __call__(self, *args, desc=''):
        c = Combo(parent=self, desc=desc)
        for i in args:
            n = Node(i, c)
            c.nodes.append(n)
        self.combos.append(c)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Combo():
    def __init__(self, parent=None, alias=None, desc=''):
        self.desc = desc
        self.parent = parent
        self.alias = 'combo_' + Context._cur_context.get_alias(alias or desc)
        self.nodes = []
        self.x = None
        self.y = None
        self.raw = 1

    @property
    def col(self):
        return ceil(len(self) / self.raw)

    def __len__(self):
        return len(self.nodes)

    def get_node_y(self, idx):
        # 如果有n层，那么每层对应一个ystep
        # e.g. 8元素分两层，0~3取0，4~7取1
        count = idx // self.col
        if count > 0:
            return self.y + inner_ystep * count
        else:
            return self.y

    def get_node_x(self, idx):
        # 取模数
        count = idx % self.col
        return self.x + xstep * count


class Node():
    def __init__(self, desc, parent: 'Combo' = None, alias=None):
        self.parent = parent

        self.desc = desc
        self.alias = 'node' + Context._cur_context.get_alias(alias or desc)
        self.x = None
        self.y = None
