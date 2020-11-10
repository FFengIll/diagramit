from contextlib import contextmanager

import loguru
import sh

logger = loguru.logger
_format = ['png', 'svg', 'txt', 'pdf', None]

direction = ['up', 'down', 'left', 'right']


def alias_gen():
    count = 0
    while 1:
        yield '{}'.format(count)
        count += 1


def desc2alias(desc: str):
    res = ''
    for ch in desc:
        if ch.isalpha():
            res += ch

    return res


def wrap_puml(content):
    text = '@startuml\n{}\n@enduml'.format('\n'.join(content))
    return text


def output_puml(path, format):
    logger.info('export {} file: {}', format, path)
    plantuml = sh.Command('plantuml')
    plantuml(path, '-t{}'.format(format))
    # os.system('plantuml {} -t{}'.format(path, format))


def assert_format(format):
    assert format in _format


def block_generator(entry, exit):
    from .context import Context

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
    from .context import Context

    def inner(desc=''):
        context = Context._cur_context
        context.add_text(entry.format(desc))
        context.add_text(exit.format(desc))

    return inner
