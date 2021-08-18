from .. import framework

import CloudFlare
import dns.name

class cloudflare_dns:
    class zone:
        def __init__(self, cf, z_id, z_name):
            self.cf = cf
            self.z_id = z_id
            self.z_name = z_name

        def fqdn(self, r_name):
            return dns.name \
                    .from_text(
                        text = r_name,
                        origin = dns.name.from_text(
                            text = self.z_name,
                            origin = dns.name.root
                        )
                    )                                       \
                    .relativize(origin = dns.name.root)     \
                    .to_text()

        def get(self, r_name = None, r_type = None, r_content = None):
            try:
                return self.cf.zones.dns_records.get(
                    self.z_id,
                    params = {
                        'name': self.fqdn(r_name),
                        'type': r_type,
                        'content': r_content,
                        'match': 'all'
                    }
                )
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                raise RuntimeError(e)

        def add(self, r_name, r_type, r_content):
            res = []

            rs = self.get(r_name, r_type, r_content)
            if not rs:
                try:
                    res.append(self.cf.zones.dns_records.post(
                        self.z_id,
                        data = {
                            'name': r_name,
                            'type': r_type,
                            'content': r_content
                        }
                    ))
                except CloudFlare.exceptions.CloudFlareAPIError as e:
                    raise RuntimeError(e)
            else:
                for r in rs:
                    r_id = r['id']

                    try:
                        res.append(self.cf.zones.dns_records.put(
                            self.z_id,
                            r_id,
                            data = {
                                'name': r_name,
                                'type': r_type,
                                'content': r_content
                            }
                        ))
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        raise RuntimeError(e)

            return res

        def remove(self, *args, **kwargs):
            res = []

            rs = self.get(*args, **kwargs)
            for r in rs:
                r_id = r['id']
                try:
                    res.append(self.cf.zones.dns_records.delete(
                        self.z_id, r_id
                    ))
                except CloudFlare.exceptions.CloudFlareAPIError as e:
                    raise RuntimeError(e)

            return res

    def __init__(self, *args, **kwargs):
        self.cf = CloudFlare.CloudFlare(*args, **kwargs)

    def zones(self, z_name):
        zs = self.cf.zones.get(params = {
            'name': z_name,
            'match': 'all'
        })

        res = []
        for z in zs:
            z_id, z_name = z['id'], z['name']
            res.append(self.zone(
                self.cf,
                z_id = z_id, z_name = z_name
            ))
        return res


class d_cloudflare(framework.ddns.database_base):
    def __init__(self,
        conf: dict,
        zone: str, name: str
    ):
        self.name = name
        self.zones = cloudflare_dns(**conf) \
                        .zones(z_name = zone)

    def add(self, addr: framework.ddns.address):
        ipaddr = addr.get_ipaddress()

        for zone in self.zones:
            zone.add(
                r_name = self.name,
                r_type = {
                    4: 'A',
                    6: 'AAAA'
                }[ipaddr.version],
                r_content = str(ipaddr)
            )

    def remove(self, addr: framework.ddns.address):
        ipaddr = addr.get_ipaddress()

        for zone in self.zones:
            zone.remove(
                r_name = self.name,
                r_type = {
                    4: 'A',
                    6: 'AAAA'
                }[ipaddr.version],
                r_content = str(ipaddr)
            )

    def purge(self):
        for zone in self.zones:
            zone.remove(r_name = self.name)

framework.modular.register(d_cloudflare, 'cloudflare')
