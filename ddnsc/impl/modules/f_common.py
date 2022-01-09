from .. import framework

import logging

import typing

class f_common(framework.ddns.filter_base):
    def __init__(self,
        interfaces: typing.Iterable[str] = None,
        private_address: bool = False,
        caching: bool = False
    ):
        self.interfaces = interfaces
        self.private_address = private_address
        self.cache = set() if caching else None

    def check(self, op: framework.ddns.op, address: framework.ddns.address):
        def check_cache():
            nonlocal self, op, address

            logging.debug(f'CHECK {address!r} cache {self.cache!r}')

            if self.cache is None:
                return True

            if op is framework.ddns.op.ADD:
                if address in self.cache:
                    return False
                self.cache.add(address)

            if op is framework.ddns.op.REMOVE:
                if address not in self.cache:
                    return False
                self.cache.remove(address)

            return True

        def check_interfaces():
            nonlocal self, address

            logging.debug(f'CHECK {address!r} interfaces {self.interfaces!r}')

            if self.interfaces is None:
                return True
            return address.get_interface().get_name() in self.interfaces

        def check_private_address():
            nonlocal self, address

            logging.debug(f'CHECK {address!r} private address')

            if not self.private_address:
                return address.get_ipaddress().is_global
            return True

        return check_cache()            \
            and check_interfaces()      \
            and check_private_address()


framework.modular.register(f_common, framework.modular.default)
