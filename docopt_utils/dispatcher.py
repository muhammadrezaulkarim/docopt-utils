import functools
import logging
import os
import re
import sys
from inspect import getdoc

from docopt import docopt
from docopt import DocoptExit


log = logging.getLogger(__name__)


def dispatch(command_classes, before_f=None, args=None, env=None):
    if not args:
        args = sys.argv[1:]
    try:
        handler, options = parse(command_classes, docopt_opts={'options_first': True},
                                 args=args, env=None)
    except NoSuchCommand as e:
        commands = '\n'.join(parse_section('commands:', getdoc(e.container)))
        log.error(f'No such command: {e.command}\n{commands}')
        sys.exit(1)

    if before_f:
        before_f(handler, options)
    handler(options)


def parse(command_classes, command='__root__', command_opts=None, docopt_opts={},
          args=None, env=None):
    command_class = command_classes.get(command)
    if not command_class:
        raise Exception()
    command_help = getdoc(command_class)
    if not command_opts:
        command_opts = {}
    command_opts.update(_docopt(command_help, args, **docopt_opts))
    command = command_opts['COMMAND']

    if command in command_classes:
        return parse(command_classes, command=command, command_opts=command_opts,
                     docopt_opts=docopt_opts, args=[command] + command_opts['ARGS'])

    if not command or command in ('-h', '--help'):
        raise SystemExit(command_help)

    command_handler = get_handler(command_class, command)
    command_help = getdoc(command_handler)
    if command_help is None:
        raise NoSuchCommand(command, command_class)

    command_opts.update(_docopt(command_help, command_opts['ARGS'], options_first=True))
    if env:
        prefix = f'{env}_'
        env_option_keys = ((k, prefix + k.lstrip('-').replace('-', '_').upper())
                           for k in command_opts.keys())
        env_options = {opt_key: os.environ[env_key]
                       for opt_key, env_key in env_option_keys
                       if env_key in os.environ}
        command_opts = {**env_options, **command_opts}

    return command_handler, command_opts


def _docopt(docstring, *args, **kwargs):
    try:
        return docopt(docstring, *args, **kwargs)
    except DocoptExit:
        raise SystemExit(docstring)


def get_handler(command_class, command):
    command_name = command.replace('-', '_')
    if not hasattr(command_class, command_name):
        raise NoSuchCommand(command, command_class)
    instance = command_class()
    return getattr(instance, command)


# From docopt@master
def parse_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


class NoSuchCommand(Exception):
    def __init__(self, command, container):
        super().__init__(f'No such command: {command}')
        self.command = command
        self.container = container
