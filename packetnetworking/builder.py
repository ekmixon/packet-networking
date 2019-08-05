from .metadata import Metadata
from .utils import (
    RecursiveDictAttributes,
    RecursiveAttributes,
    WhereList,
    IPAddressList,
    get_matched_interfaces,
    get_interfaces,
    resolvers,
)
from .distros import get_distro_builder
from collections import namedtuple
import logging
import requests

log = logging.getLogger()

OSInfo = namedtuple("OSInfo", ["name", "version"])


class Builder(object):
    def __init__(self, metadata=None):
        self.metadata = None
        self.initialized = False

        self.network = NetworkData()

        if metadata:
            self.set_metadata(metadata)

    # Any attribute not found will attempt to pull it from metadata
    def __getattr__(self, attr):
        return getattr(self.metadata, attr)

    def load_metadata(self, url, **request_args):
        response = requests.get(url, **request_args)
        response.raise_for_status()
        self.set_metadata(response.json())
        return self

    def set_metadata(self, metadata):
        self.metadata = Metadata(metadata)
        return self.metadata

    def get_builder(self, distro):
        builder = get_distro_builder(distro)
        if not builder:
            raise LookupError("No builders found for distro '{}'".format(distro))
        return builder

    def initialize(self):
        self.initialized = False
        if self.metadata is None:
            raise Exception("Metadata must be loaded before calling initialize")
        self.network.load(self.metadata.network)
        self.initialized = True
        return self

    def run(self, osinfo, rootfs_path):
        if not self.initialized:
            raise Exception("Builder must be initialized before calling run")

        osname, osversion = osinfo.split()
        osinfo = OSInfo(osname.lower(), osversion)
        DistroBuilder = self.get_builder(osinfo.name)
        builder = DistroBuilder(self)
        builder.build(osinfo)
        builder.run(rootfs_path)
        return builder


class NetworkData(object):
    def __init__(self, default_resolvers=None):
        self.nw_metadata = None
        self.bonding = None
        self.interfaces = None
        self.bonds = None
        self.addresses = None
        self.resolvers = default_resolvers

    def load(self, nw_metadata):
        self.nw_metadata = nw_metadata
        self.build_bonding()
        self.build_interfaces()
        self.build_bonds()
        self.build_addresses()
        self.build_resolvers()

    def build_bonding(self):
        self.bonding = self.nw_metadata.bonding

    def build_interfaces(self):
        self.interfaces = WhereList()
        physical_ifaces = get_interfaces()
        matched_ifaces = get_matched_interfaces(
            self.nw_metadata.interfaces, physical_ifaces
        )
        if not matched_ifaces:
            log.debug("Physical Interfaces: {}".format(physical_ifaces))
            log.debug("Metadata Interfaces: {}".format(self.nw_metadata.interfaces))
            raise LookupError("No interfaces matched ones provided from metadata")
        self.interfaces = RecursiveAttributes(matched_ifaces)

    def build_bonds(self):
        self.bonds = RecursiveDictAttributes({})
        for iface in self.nw_metadata.interfaces:
            if iface.bond:
                if iface.bond not in self.bonds:
                    self.bonds[iface.bond] = [iface]
                else:
                    self.bonds[iface.bond].append(iface)

    def build_addresses(self):
        self.addresses = IPAddressList(self.nw_metadata.addresses)

    def build_resolvers(self):
        self.resolvers = resolvers(self.resolvers)
