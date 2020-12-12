from textwrap import dedent
import pytest
from jinja2.exceptions import UndefinedError


@pytest.fixture
def suse_dhcp_network(generic_suse_dhcp_network):
    def _builder(**kwargs):
        return generic_suse_dhcp_network("suse", "7", **kwargs)

    return _builder


def test_suse_private_only_throws_error(suse_dhcp_network):
    """
    Verifies a jinja2 UndefinedError is thrown when providing only
    private ip information
    """
    builder = suse_dhcp_network(public=False)
    with pytest.raises(UndefinedError):
        builder.render()


def test_suse_public_task_etc_sysconfig_network_ifcfg_enp1(suse_dhcp_network):
    """
    For each interface, we should see the corresponding ifcfg file
    located at /etc/sysconfig/network/ifcfg-*
    """
    builder = suse_dhcp_network(public=True)
    tasks = builder.render()
    result = dedent(
        """\
        STARTMODE='hotplug'
        BOOTPROTO='none'
    """
    )
    assert tasks["etc/sysconfig/network/ifcfg-enp1"] == result


def test_suse_etc_resolvers_configured(suse_dhcp_network, fake):
    """
    Validates /etc/resolv.conf is configured correctly
    """
    builder = suse_dhcp_network()
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


def test_suse_etc_hostname_configured(suse_dhcp_network):
    """
    Validates /etc/hostname is configured correctly
    """
    builder = suse_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        {hostname}
    """
    ).format(hostname=builder.metadata.hostname)
    assert tasks["etc/hostname"] == result


def test_suse_etc_hosts_configured(suse_dhcp_network):
    """
    Validates /etc/hosts is configured correctly
    """
    builder = suse_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
        ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
    """
    )
    assert tasks["etc/hosts"] == result
