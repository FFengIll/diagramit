from urllib.parse import unquote

import loguru
from jinja2 import Environment, FileSystemLoader
from path import Path
from requests_file import FileAdapter
from requests_html import HTMLSession, Element

logger = loguru.logger
session = HTMLSession()
session.mount('file://', FileAdapter())

# 使用包加载器，限定包结构
folder = Path(__package__).dirname()
env = Environment(loader=FileSystemLoader(str(folder), 'templates'))  # 创建一个包加载器对象


class Template:
    arch = 'arch.template.html'
    linkarch = 'link.arch.template.html'


svg_attr_pad = dict(
    xmlns="http://www.w3.org/2000/svg",
    contentScriptType="application/ecmascript",
    contentStyleType="text/css"
)
svg_attr_pad['xmlns:xlink'] = "http://www.w3.org/1999/xlink"


class Helper():
    def render(self, template, **kwargs):
        template = env.get_template(template)  # 获取一个模板文件
        content = template.render(**kwargs)  # 渲染
        return content

    def output(self, template, output, **kwargs):
        # render with g6
        content = self.render(template, **kwargs)

        # make a temp file
        # fd, path = tempfile.mkstemp(suffix='.html')
        path = './tmp.html'
        with open(path, 'w') as f:
            f.write(content)

        # headless load html file
        url = 'file://{}'.format(Path(path).abspath())
        logger.info(url)
        res = session.get(url)

        # render and draw the diagram
        html = res.html
        html.render()

        # get the data url and save to file
        data_url = html.render(script='graph.toDataURL()')
        # must do an unquote
        data_plain = unquote(data_url)
        # result like `data:image/svg+xml;charset=utf8,<!DOCTYPE......`
        payload = data_plain[data_plain.find('<!DOCTYPE'):]
        logger.debug('output payload (len={})', len(payload))
        with open(output, 'w') as fd:
            fd.write(payload)
        return output

        # extract svg data & output file
        svg: Element = html.find('svg', first=True)
        svg.element.attrib.update(svg_attr_pad)
        with open(output, 'w') as fd:
            fd.write(svg.html)
