from .. import NetworkBuilder


# pylama:ignore=E501
class SuseDhcpNetwork(NetworkBuilder):
    def build(self):
        if self.network.bonding.link_aggregation == "dhcp":
            self.build_tasks()

    def build_tasks(self):
        self.tasks = {}

        iface0 = self.network.interfaces[0]

        self.task_template(
            "etc/sysconfig/network/ifcfg-" + iface0.name,
            "dhcp/etc_sysconfig_network_ifcfg-iface0.j2",
        )

        for i, iface in enumerate(self.network.interfaces):
            if iface == iface0:
                # skip interface since it is already configured above
                continue
            self.task_template(
                "etc/sysconfig/network/ifcfg-" + iface.name,
                "dhcp/etc_sysconfig_network_ifcfg-template.j2",
                fmt={"iface": iface.name, "i": i},
            )

        return self.tasks