#!/usr/bin/env python3

import consts
#raise NotImplementedError()


def dispatch(removal: bool, user: bool, unit_name: str):
    global consts

    import os
    import configparser
    class systemd_unit(configparser.ConfigParser):
        class location:
            user = '~/.local/share/systemd/user/'
            system = '/usr/lib/systemd/system/'

        @staticmethod
        def get_path(user: bool, name: str):
            ext = '.service'
            base = systemd_unit.location.user if user   \
                    else systemd_unit.location.system

            base = os.path.expanduser(base)
            if not os.path.exists(base):
                os.makedirs(base)

            return os.path.join(base, name + ext)

        def __init__(self,
            user: bool, unit_name: str,
            *args, **kwargs
        ):
            super().__init__(*args, **kwargs)
            self.optionxform = str

            self._path = self.get_path(user, unit_name)

        def __enter__(self):
            self._fp = open(file = self._path, mode = 'w+')
            self.read(self._fp)
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.write(
                self._fp,
                space_around_delimiters = False
            )
            self._fp.close()

    class system_conf:
        class location:
            user = '~/.config/'
            system = '/etc/'

        @staticmethod
        def get_path(user: bool, name: str):
            base = system_conf.location.user if user   \
                    else system_conf.location.system

            base = os.path.expanduser(base)
            if not os.path.exists(base):
                os.makedirs(base)

            return os.path.join(base, name)

    if removal:
        import os
        os.remove(systemd_unit.get_path(user, unit_name))
    else:
        user = user
        conf_dir = system_conf.get_path(user, 'ddnsc.d')
        import os
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)
        unit_name = unit_name
        description = 'DDNS Client Daemon Service'
        start_after = 'network-online.target'
        daemon_exec = consts.EXECUTABLE
        daemon_args = f"-c '{conf_dir}/*'"

        with systemd_unit(
            user = user,
            unit_name = unit_name
        ) as config:
            config['Unit'] = {
                'Description': description,
                'After': start_after
            }
            config['Service'] = {
                'Type': 'simple',
                'ExecStart': f'/usr/bin/env sh -c "{daemon_exec} {daemon_args}"'
            }
            config['Install'] = {
                'WantedBy': 'multi-user.target'
            }

def main():
    global consts

    import logging
    import argparse
    import glob

    argparser = argparse.ArgumentParser(
        description = f'Systemd service installer for {consts.EXECUTABLE}.'
    )
    argparser.add_argument(
        '--remove',
        required = False,
        action = "store_true",
        default = False,
        dest = 'removal',
        help = 'remove installation'
    )
    argparser.add_argument(
        '--user',
        required = False,
        action = "store_true",
        default = False,
        dest = 'user',
        help = 'install systemd user service'
    )
    argparser.add_argument(
        '-u', '--unit-name',
        required = True,
        nargs = None,
        type = str,
        dest = 'unit_name',
        help = 'specify systemd unit name'
    )

    args = argparser.parse_args()

    dispatch(
        removal = args.removal,
        user = args.user,
        unit_name = args.unit_name
    )

if __name__ == '__main__':
    main()
