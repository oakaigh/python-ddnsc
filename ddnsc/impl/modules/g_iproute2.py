from .. import framework


class g_iproute2(framework.ddns.generator_base):
    def get(self, callback):
        import logging

        import socket
        import ipaddress
        import pyroute2

        import itertools

        def handle_ipr_info(ipr_info):
            for ipr_entry in ipr_info:
                def handle_intf():
                    nonlocal ipr_entry

                    ev = ipr_entry['event']

                    if ev is 'RTM_NEWLINK':
                        framework.ddns.interface.register(
                            idx = int(ipr_entry['index']),
                            ifname = dict(ipr_entry['attrs'])['IFLA_IFNAME']
                        )
                    if ev is 'RTM_DELLINK':
                        framework.ddns.interface.unregister(
                            idx = int(ipr_entry['index'])
                        )

                def handle_addr():
                    nonlocal ipr_entry, callback

                    ev = ipr_entry['event']

                    op = {
                        'RTM_NEWADDR': framework.ddns.op.ADD,
                        'RTM_DELADDR': framework.ddns.op.REMOVE
                    }.get(ev)
                    if op is None:
                        return

                    callback(
                        op,
                        framework.ddns.address(
                            intf = framework.ddns.interface(
                                idx = int(ipr_entry['index'])
                            ),
                            ipaddr = ipaddress.ip_address(
                                address = dict(ipr_entry['attrs'])[
                                    'IFA_ADDRESS'
                                ]
                            )
                        )
                    )

                handle_intf()
                handle_addr()

        with pyroute2.IPRoute() as ipr:
            handle_ipr_info(
                itertools.chain(
                    ipr.get_links(),
                    ipr.get_addr()
                )
            )

            ipr.bind()
            while True:
                handle_ipr_info(ipr.get())

framework.modular.register(g_iproute2, framework.modular.default)
