# Copyright (C) 2015 Red Hat, Inc., Lee Yarwood <lyarwood@redhat.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin


class OpenStackIronic(Plugin):
    """OpenStack Ironic
    """
    plugin_name = "openstack_ironic"
    profiles = ('openstack', 'openstack_undercloud')

    def setup(self):
        self.conf_list = ['/etc/ironic/*']
        self.add_copy_spec('/etc/ironic/')
        self.add_copy_spec('/var/log/ironic/')

        self.add_cmd_output('ls -laRt /var/lib/ironic/')

    def postproc(self):
        protect_keys = [
            "dns_passkey", "memcache_secret_key", "rabbit_password",
            "password", "qpid_password", "connection", "sql_connection",
            "admin_password", "ssl_key_password", "os_password"
        ]
        regexp = r"((?m)^\s*#*(%s)\s*=\s*)(.*)" % "|".join(protect_keys)

        for conf in self.conf_list:
            self.do_path_regex_sub(conf, regexp, r"\1*********")


class DebianOpenStackIronic(OpenStackIronic, DebianPlugin, UbuntuPlugin):

    packages = [
        'ironic-api',
        'ironic-common',
        'ironic-conductor',
    ]

    def setup(self):
        super(DebianOpenStackIronic, self).setup()


class RedHatOpenStackIronic(OpenStackIronic, RedHatPlugin):

    packages = [
        'openstack-ironic-api',
        'openstack-ironic-common',
        'openstack-ironic-conductor',
    ]

    discoverd_packages = [
        'openstack-ironic-discoverd',
        'openstack-ironic-discoverd-ramdisk'
    ]

    def setup(self):
        super(RedHatOpenStackIronic, self).setup()

        # is the optional ironic-discoverd service installed?
        if any([self.is_installed(p) for p in self.discoverd_packages]):
            self.conf_list.append('/etc/ironic-discoverd/*')
            self.add_copy_spec('/etc/ironic-discoverd/')
            self.add_copy_spec('/var/lib/ironic-discoverd/')
            self.add_copy_spec('/var/log/ironic-discoverd/')

            self.add_cmd_output('journalctl -u openstack-ironic-discoverd')
            self.add_cmd_output('journalctl '
                                '-u openstack-ironic-discoverd-dnsmasq')

# vim: set et ts=4 sw=4 :
