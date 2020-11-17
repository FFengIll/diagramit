from functools import cached_property
from math import ceil
from typing import *

import loguru

from diagramit.g6.diagram import Diagram, Context

logger = loguru.logger
"""
需要根据上下文进行组装。
每次生成一个group，并将其中的每个node创建填入。
最终根据算法评估要如何布局每个group，从而设置node position。
"""

padding = 10
limit = 8
"#E5F5FD", "#EBF3E7", "#ECE8F6", "#FDF7E3"


class Space():
    def __init__(self, x, y):
        self.x, self.y = x, y


class Pad():
    def __init__(self, space, padding):
        self.top, self.right, self.bottom, self.left = padding
        self.space: Space = space
        self.width = 100
        self.height = 30

    @property
    def padding(self):
        return [self.top, self.right, self.bottom, self.left]


class CSS():
    node = Pad(Space(padding, padding), [25, 10, 10, 10])
    combo = Pad(Space(padding * 4, 0), [10, 10, 10, 10])
    label_combo = Pad(Space(padding * 4, 0), [25, 10, 10, 10])
    layer = Pad(Space(padding * 4, padding), [25, 10, 10, 10])


ystep = (CSS.node.height + padding + CSS.combo.top) + padding + (padding * 2)
xstep = CSS.node.width + CSS.node.space.x
inner_ystep = CSS.node.height + padding


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
            pad = 0
            pad += CSS.layer.space.y
            pad += raw * CSS.node.height + (raw - 1) * CSS.node.space.x
            if len(layer.combos) > 1:
                pad += CSS.combo.top + CSS.layer.top
                pad += CSS.combo.bottom + CSS.layer.bottom
            else:
                pad += CSS.combo.top + CSS.layer.top
                pad += CSS.combo.bottom + CSS.layer.bottom

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
        res = super(Arch, self).__exit__(exc_type, exc_val, exc_tb)

    def add_combo(self, c):
        self.layers.append(c)

    def to_puml(self):
        arch = ArchLayout(self)
        arch.layout()
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

        if max_col <= limit:
            # 已经足够均衡了，可以直接开始后续步骤
            return
        else:
            # 宽度过分大，需要拆分combo
            for layer in self.context.layers:
                if layer.col > limit:
                    # 对于比较不均衡的部分，直接拆分
                    for combo in layer.combos:
                        combo.raw += 1

            self.preprocess()

    def layout(self):

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
            if delta > 0:
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
            n.x = combo.get_node_x(idx) + CSS.node.space.x
            n.y = combo.get_node_y(idx)

    def layout_layer(self, layer: 'Layer'):
        if len(layer.combos) == 0:
            return

        # if len(layer.combos) == 1:
        #     # 注意：对于单层单combo，直接用combo作为这个层级即可
        #     combo = layer.combos[0]
        #     if combo.label and layer.label:
        #         pass
        #     else:
        #         combo.x, combo.y = layer.get_combo_x(0), layer.get_combo_y(None)
        #         combo.parent=None
        #         self.layout_combo(combo, )
        #         return

        # layout inner combo
        # 由于可能拆分成多个层级，所以需要妥善构造增量
        # 对于y轴，（内外）记录并构造每一层的y
        # 对于x轴，需要内部记录并构造每一层x

        xbase = layer.x
        ybase = layer.y
        for _, combo in enumerate(layer.combos):
            combo.x = xbase
            combo.y = ybase + CSS.combo.top + CSS.combo.bottom
            logger.info('{} {} x={}', layer, combo, combo.x)

            xbase += CSS.node.width * combo.col + CSS.node.space.x * (combo.col - 1) + CSS.combo.space.x
            self.layout_combo(combo)

    def generate_node(self, node: 'Node', parent=None):
        res = dict(
            id=node.alias,
            comboId=parent.id,
            label=node.label,
            x=node.x,
            y=node.y,
            style=node.style,
        )
        res['style'].update(node._attrs)

        self.ns.append(res)

        return res

    def generate_combo(self, combo: 'Combo', parent=None):
        for idx, n in enumerate(combo.nodes):
            self.generate_node(n, combo)

        res = dict(
            id=combo.id,
            label=combo.label,
            y=combo.y,
            padding=combo.padding,
            style=combo.style,
        )
        if combo.x:
            res['x'] = combo.x
        if combo.parent:
            res['parentId'] = combo.parent.id

        res['style'].update(combo._attrs)

        return res

    def generate_layer(self, layer: 'Layer'):
        if len(layer.combos) <= 0:
            return

        # if len(layer.combos) == 1:
        #     # 注意：对于单层单combo，直接用combo作为这个层级即可
        #     combo = layer.combos[0]
        #     if combo.label and layer.label:
        #         pass
        #     else:
        #         combo.label = layer.label
        #         res = self.generate_combo(combo, )
        #         self.cs.append(res)
        #         return

        # 注意：对于单层多combo，需要额外附加一个parent（或许以后可以去除）
        res = dict(
            id=layer.id,
            label=layer.label,
            style=layer.style,
        )
        res['style'].update(layer._attrs)

        self.cs.append(res)

        # layout inner combo
        # 由于可能拆分成多个层级，所以需要妥善构造增量
        # 对于y轴，（内外）记录并构造每一层的y
        # 对于x轴，需要内部记录并构造每一层x

        xidx = 0

        for cidx, combo in enumerate(layer.combos):
            xidx += combo.col
            res = self.generate_combo(combo)

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
    @property
    def style(self):
        return dict(
            fill='#E5F5FD'
        )

    def __init__(self, label='', alias=None, **kwargs):
        self.context: Arch = Context._cur_context
        self.context.add_layer(self)
        self.label = label
        self.id = 'layer_' + self.context.get_alias(alias or label)
        self.combos: List[Combo] = []
        self.x = None
        self.y = None

        self._attrs = kwargs

    def extend_space(self, delta):
        """
        扩展空隙，有两种方案
        1. 左右panding combo
        2. 在node间扩大space
        目前使用方案2
        :param delta:
        :return:
        """
        count = 0
        inner_count = []
        for c in self.combos:
            t = c.col
            count += t
            inner_count.append(t)

        # 理论上不存在
        if count <= 0:
            return

        space = delta / count
        base = 0
        for combo, count in zip(self.combos, inner_count):
            # 平移每个node
            combo.extend_space(space)
            # 对combo加一个right padding
            combo.padding[1] = space + padding

            for n in combo.nodes:
                n.x += base

            base += count * space

    @cached_property
    def width_legacy(self):
        col = self.col
        cs = len(self.combos)

        # 计算边缘，计算combo间space，计算node，计算node间space
        pad = CSS.combo.space.x * (cs - 1) + col * CSS.node.width
        for c in self.combos:
            pad += (len(c.nodes) - 1) * CSS.node.space.x

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
        right = last.nodes[min(last.col - 1, len(last.nodes))].x + CSS.node.width

        cs = len(self.combos)
        # layer 两端
        extra1 = CSS.layer.left + CSS.layer.right
        # layer combo 两端
        extra2 = CSS.combo.left + CSS.combo.right
        # extra2 = CSS.combo.left + CSS.combo.right if cs>1 else 0

        return right - left + extra1 + extra2

    def get_combo_y(self, idx):
        return self.y

    def get_combo_x(self, idx):
        if idx > 0:
            return self.x + CSS.node.width * idx + CSS.node.space.x * (idx - 1) + CSS.combo.space.x
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
        return self.id

    def __repr__(self):
        return str(self)

    def __call__(self, *args, label=''):
        c = Combo(label, parent=self, )
        for i in args:
            if isinstance(i, Node):
                n = i
                n.parent = c
            else:
                n = Node(i, c)
            c.nodes.append(n)
        self.combos.append(c)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Combo():

    @property
    def style(self):
        return dict(
            fill='#EBF3E7'
        )

    def __init__(self, label, parent=None, **kwargs):
        self.label = label
        self.parent = parent
        self.id = 'combo_' + Context._rand_id()
        self.nodes = []
        self.x = None
        self.y = None
        self.raw = 1

        if label:
            self.padding = CSS.label_combo.padding
        else:
            self.padding = CSS.combo.padding

        self._attrs = kwargs

    def extend_space(self, space):
        col = self.col
        for idx, n in enumerate(self.nodes):
            m = idx % col
            n.x += m * space

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
    @property
    def style(self):
        return dict(
            fill='#C6E5FF'
        )

    def __init__(self, label, parent: 'Combo' = None, **kwargs):
        self.parent = parent

        self.label = label
        self.alias = 'node_' + Context._rand_id()
        self.x = None
        self.y = None

        self._attrs = kwargs
