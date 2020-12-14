from .. import DistroBuilder
from .bonded import DebianBondedNetwork
from .individual import DebianIndividualNetwork
from .dhcp import DebianDhcpNetwork


class DebianBuilder(DistroBuilder):
    distros = ["debian", "ubuntu"]
    network_builders = [DebianBondedNetwork, DebianIndividualNetwork, DebianDhcpNetwork]

    def build_tasks(self):
        self.tasks = {}

        self.task_template("etc/hostname", "etc_hostname.j2")
        self.task_template("etc/resolv.conf", "etc_resolv.conf.j2")
        self.task_template("etc/hosts", "etc_hosts.j2")

        return self.tasks
