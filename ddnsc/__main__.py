from .impl import framework
from .impl.modules import *


def dispatch(conf):
    import collections
    def deep_update(dst, src):
        ret = dst
        for key, value in src.items():
            if isinstance(value, collections.abc.Mapping) and value:
                ret[key] = deep_update(
                    dst = dst.setdefault(key, {}),
                    src = value
                )
            else:
                ret[key] = value
        return ret

    conf = deep_update(
        dst = {
            'volatile': False,
            'generator': {
                'name': framework.modular.default,
                'conf': {}
            },
            'filter': {
                'name': framework.modular.default,
                'conf': {}
            },
            'database': {
                'name': framework.modular.default,
                'conf': {}
            }
        },
        src = conf
    )

    g_conf = conf['generator']
    _gen = framework.modular.init(
        mod_type = framework.modular.type.GENERATOR,
        mod_name = g_conf['name'],
        mod_conf = g_conf['conf']
    )

    f_conf = conf['filter']
    _filter = framework.modular.init(
        mod_type = framework.modular.type.FILTER,
        mod_name = f_conf['name'],
        mod_conf = f_conf['conf']
    )

    d_conf = conf['database']
    _db = framework.modular.init(
        mod_type = framework.modular.type.DATABASE,
        mod_name = d_conf['name'],
        mod_conf = d_conf['conf']
    )

    framework.ddns(
        _gen = _gen,
        _filter = _filter,
        _db = _db
    ).dispatch(volatile = conf['volatile'])

def dispatch_conf_files(conf_files):
    import multiprocessing
    import json

    jobs = []

    for conf_file in conf_files:
        with open(conf_file) as f:
            conf = json.load(f)

            p = multiprocessing.Process(
                target = dispatch,
                kwargs = {'conf': conf}
            )
            p.start()
            jobs.append(p)

    for p in jobs:
        p.join()


def main():
    import logging
    import argparse
    import glob

    argparser = argparse.ArgumentParser(
        description = 'DDNS client daemon.'
    )
    argparser.add_argument(
        '-l', '--log-level',
        required = False,
        nargs = None,
        type = str,
        default = 'NOTSET',
        choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        dest = 'log_level',
        help = 'set logging level'
    )
    argparser.add_argument(
        '-c', '--conf-file',
        required = True,
        nargs = '+',
        type = str,
        dest = 'conf_args',
        help = 'read one or multiple configuration files (glob pattern matching supported)'
    )

    args = argparser.parse_args()

    logging.basicConfig(level = args.log_level)

    conf_files = []
    for conf_arg in args.conf_args:
        conf_files += glob.glob(conf_arg, recursive = True)

    dispatch_conf_files(conf_files)

if __name__ == '__main__':
    main()
