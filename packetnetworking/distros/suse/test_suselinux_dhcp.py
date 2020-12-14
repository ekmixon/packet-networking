from textwrap import dedent
import pytest
from jinja2.exceptions import UndefinedError


@pytest.fixture
def suselinux_dhcp_network(generic_suse_dhcp_network):
    def _builder(**kwargs):
        return generic_suse_dhcp_network("suselinux", "7", **kwargs)

    return _builder


def test_suselinux_dhcp_task_etc_sysconfig_network_ifcfg_enp0(
    suselinux_dhcp_network
):
    """Validates /etc/sysconfig/network/ifcfg-enp0 file"""
    builder = suselinux_dhcp_network(public=True)
    tasks = builder.render()
    result = dedent(
        """\
        STARTMODE='hotplug'
        BOOTPROTO='dhcp'
    """
    )
    assert tasks["etc/sysconfig/network/ifcfg-enp0"] == result


def test_suselinux_public_task_etc_sysconfig_network_ifcfg_enp1(
    suselinux_dhcp_network
):
    """
    For each interface, we should see the corresponding ifcfg file
    located at /etc/sysconfig/network/ifcfg-*
    """
    builder = suselinux_dhcp_network(public=True)
    tasks = builder.render()
    result = dedent(
        """\
        STARTMODE='hotplug'
        BOOTPROTO='none'
    """
    )
    assert tasks["etc/sysconfig/network/ifcfg-enp1"] == result


def test_suselinux_etc_resolvers_configured(suselinux_dhcp_network, fake):
    """
    Validates /etc/resolv.conf is configured correctly
    """
    builder = suselinux_dhcp_network()
    resolver1 = fake.ipv4()
    resolver2 = fake.ipv4()
    builder.network.resolvers = (resolver1, resolver2)
    tasks = builder.render()
    result = dedent(
        """\
        nameserver {resolver1}
        nameserver {resolver2}
    """
    ).format(resolver1=resolver1, resolver2=resolver2)
    assert tasks["etc/resolv.conf"] == result


def test_suselinux_etc_hostname_configured(suselinux_dhcp_network):
    """
    Validates /etc/hostname is configured correctly
    """
    builder = suselinux_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        {hostname}
    """
    ).format(hostname=builder.metadata.hostname)
    assert tasks["etc/hostname"] == result


def test_suselinux_etc_hosts_configured(suselinux_dhcp_network):
    """
    Validates /etc/hosts is configured correctly
    """
    builder = suselinux_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
        ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
    """
    )
    assert tasks["etc/hosts"] == result
