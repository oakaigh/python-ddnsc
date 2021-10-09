import logging

import enum
import typing
import ipaddress

class ddns:
    ip_address = ipaddress._BaseAddress

    class interface:
        links = dict()

        @staticmethod
        def register(idx: int, ifname: str):
            ddns.interface.links[idx] = ifname

        @staticmethod
        def unregister(idx: int):
            try:
                ddns.interface.links.pop(idx)
            except KeyError:
                pass

        def __init__(self, idx: int):
            self.idx = idx

        def __eq__(self, other):
            if isinstance(other, type(self)):
                return self.idx == other.idx
            if isinstance(other, int):
                return self.idx == other
            if isinstance(other, str):
                return self.get_name() == other

            return False

        def __hash__(self):
            return self.idx.__hash__()

        def __repr__(self):
            return f'{self.get_name()!r}'

        def get_name(self):
            return self.links.get(self.idx, None)

    class address:
        def __init__(self,
            intf: 'ddns.interface',
            ipaddr: 'ddns.ip_address'
        ):
            self.intf = intf
            self.ipaddr = ipaddr

        def __eq__(self, other):
            return self.intf == other.intf  \
                    and self.ipaddr == other.ipaddr

        def __hash__(self):
            return (self.intf, self.ipaddr).__hash__()

        def __repr__(self):
            return f'{(self.intf, self.ipaddr)!r}'

        def get_interface(self): return self.intf
        def get_ipaddress(self): return self.ipaddr


    class op(enum.Enum):
        ADD, REMOVE = 0, 1

    class generator_base:
        def get(self,
            callback: typing.Callable[['ddns.op', 'ddns.address'], typing.Any]
        ):
            raise NotImplementedError()

    class filter_base:
        def check(self,
            op: 'ddns.op',
            address: 'ddns.address'
        ) -> bool:
            raise NotImplementedError()

    class database_base:
        def add(self, addr: 'ddns.address'):
            raise NotImplementedError()

        def remove(self, addr: 'ddns.address'):
            raise NotImplementedError()

        def purge(self):
            raise NotImplementedError()

    def __init__(self,
        _gen: 'ddns.generator_base',
        _filter: 'ddns.filter_base',
        _db: 'ddns.database_base'
    ):
        self._gen = _gen
        self._filter = _filter
        self._db = _db

    def dispatch(self, volatile: bool = False):
        def cleanup():
            nonlocal volatile
            if volatile:
                self._db.purge()

        def callback(op: self.op, addr: self.address):
            try:
                if not self._filter.check(op, addr):
                    return

                logging.info(f'UPDATE {addr!r}')
                return {
                    self.op.ADD: self._db.add,
                    self.op.REMOVE: self._db.remove
                }[op](addr)
            except Exception as e:
                logging.critical(e, exc_info = True)
                return

        cleanup()
        self._gen.get(callback = callback)

class modular:
    default = None

    class type:
        GENERATOR, FILTER, DATABASE = 0, 1, 2

    modules = {
        type.GENERATOR: dict(),
        type.FILTER: dict(),
        type.DATABASE: dict()
    }

    @staticmethod
    def register(mod, mod_name):
        def get_type(mod):
            if issubclass(mod, ddns.generator_base):
                return modular.type.GENERATOR
            if issubclass(mod, ddns.filter_base):
                return modular.type.FILTER
            if issubclass(mod, ddns.database_base):
                return modular.type.DATABASE

            raise TypeError()

        modular.modules[get_type(mod)][mod_name] = mod

    @staticmethod
    def get(mod_type, mod_name = default):
        return modular.modules[mod_type][mod_name]

    @staticmethod
    def init(mod_type, mod_name, mod_conf = {}):
        return modular.get(
            mod_type = mod_type,
            mod_name = mod_name
        )(**mod_conf)
