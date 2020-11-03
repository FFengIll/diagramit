import os
from contextlib import contextmanager

from .context import Context

_format = ['png', 'svg', 'txt', 'pdf', None]


def wrap_puml(content):
    text = '@startuml\n{}\n@enduml'.format('\n'.join(content))
    return text


def output_puml(path, format):
    os.system('plantuml {} -t{}'.format(path, format))


def assert_format(format):
    assert format in _format


def block_generator(entry, exit):
    @contextmanager
    def inner(desc=''):
        context = Context._cur_context
        context.add_text(entry.format(desc))
        try:
            yield None
        finally:
            context.add_text(exit.format(desc))

    return inner


def line_generator(entry, exit):
    def inner(desc=''):
        context = Context._cur_context
        context.add_text(entry.format(desc))
        context.add_text(exit.format(desc))

    return inner
