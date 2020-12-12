from textwrap import dedent
import pytest


@pytest.fixture
def debian_7_dhcp_network(generic_debian_dhcp_network):
    def _builder(**kwargs):
        return generic_debian_dhcp_network("debian", "7", **kwargs)

    return _builder


def test_debian_7_dhcp_task_etc_network_interfaces(
    debian_7_dhcp_network
):
    """Validates /etc/network/interfaces for DHCP"""

    builder = debian_7_dhcp_network(public=True)
    tasks = builder.render()
    result = dedent(
        """\
        auto lo
        iface lo inet loopback

        auto enp0
        iface enp0 inet dhcp
    """
    )
    assert tasks["etc/network/interfaces"] == result


def test_debian_7_etc_resolvers_configured(debian_7_dhcp_network, fake):
    """
    Validates /etc/resolv.conf is configured correctly
    """
    builder = debian_7_dhcp_network()
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


def test_debian_7_etc_hostname_configured(debian_7_dhcp_network):
    """
    Validates /etc/hostname is configured correctly
    """
    builder = debian_7_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        {hostname}
    """
    ).format(hostname=builder.metadata.hostname)
    assert tasks["etc/hostname"] == result


def test_debian_7_etc_hosts_configured(debian_7_dhcp_network):
    """
    Validates /etc/hosts is configured correctly
    """
    builder = debian_7_dhcp_network()
    tasks = builder.render()
    result = dedent(
        """\
        127.0.0.1	localhost	{hostname}

        # The following lines are desirable for IPv6 capable hosts
        ::1	localhost ip6-localhost ip6-loopback
        ff02::1	ip6-allnodes
        ff02::2	ip6-allrouters
    """
    ).format(hostname=builder.metadata.hostname)
    assert tasks["etc/hosts"] == result


def test_debian_7_no_persistent_interface_names(debian_7_dhcp_network):
    """
    When using certain operating systems, we want to bypass driver interface name,
    here we make sure the /etc/udev/rules.d/70-persistent-net.rules is generated.
    """
    builder = debian_7_dhcp_network()
    tasks = builder.render()
    assert "etc/udev/rules.d/70-persistent-net.rules" not in tasks
