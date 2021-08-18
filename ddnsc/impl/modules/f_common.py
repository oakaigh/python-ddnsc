from .. import framework

import typing

class f_common(framework.ddns.filter_base):
    def __init__(self,
        interfaces: typing.Iterable[str] = None,
        private_address: bool = False
    ):
        self.interfaces = interfaces
        self.private_address = private_address

    def check(self, op: framework.ddns.op, address: framework.ddns.address):
        res = True

        if self.interfaces is not None:
            res &= address.get_interface().get_name() in self.interfaces

        if not self.private_address:
            res &= address.get_ipaddress().is_global

        return res


framework.modular.register(f_common, framework.modular.default)
