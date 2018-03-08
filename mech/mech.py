# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from __future__ import print_function

import os
import sys
import time
import utils
import shutil
import fnmatch
import logging
import tempfile
import textwrap
import subprocess

from clint.textui import colored, puts_err

from vmrun import VMrun
from command import Command

logger = logging.getLogger(__name__)

DEFAULT_USER = 'vagrant'
DEFAULT_PASSWORD = 'vagrant'
INSECURE_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzI
w+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoP
kcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2
hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NO
Td0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcW
yLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQIBIwKCAQEA4iqWPJXtzZA68mKd
ELs4jJsdyky+ewdZeNds5tjcnHU5zUYE25K+ffJED9qUWICcLZDc81TGWjHyAqD1
Bw7XpgUwFgeUJwUlzQurAv+/ySnxiwuaGJfhFM1CaQHzfXphgVml+fZUvnJUTvzf
TK2Lg6EdbUE9TarUlBf/xPfuEhMSlIE5keb/Zz3/LUlRg8yDqz5w+QWVJ4utnKnK
iqwZN0mwpwU7YSyJhlT4YV1F3n4YjLswM5wJs2oqm0jssQu/BT0tyEXNDYBLEF4A
sClaWuSJ2kjq7KhrrYXzagqhnSei9ODYFShJu8UWVec3Ihb5ZXlzO6vdNQ1J9Xsf
4m+2ywKBgQD6qFxx/Rv9CNN96l/4rb14HKirC2o/orApiHmHDsURs5rUKDx0f9iP
cXN7S1uePXuJRK/5hsubaOCx3Owd2u9gD6Oq0CsMkE4CUSiJcYrMANtx54cGH7Rk
EjFZxK8xAv1ldELEyxrFqkbE4BKd8QOt414qjvTGyAK+OLD3M2QdCQKBgQDtx8pN
CAxR7yhHbIWT1AH66+XWN8bXq7l3RO/ukeaci98JfkbkxURZhtxV/HHuvUhnPLdX
3TwygPBYZFNo4pzVEhzWoTtnEtrFueKxyc3+LjZpuo+mBlQ6ORtfgkr9gBVphXZG
YEzkCD3lVdl8L4cw9BVpKrJCs1c5taGjDgdInQKBgHm/fVvv96bJxc9x1tffXAcj
3OVdUN0UgXNCSaf/3A/phbeBQe9xS+3mpc4r6qvx+iy69mNBeNZ0xOitIjpjBo2+
dBEjSBwLk5q5tJqHmy/jKMJL4n9ROlx93XS+njxgibTvU6Fp9w+NOFD/HvxB3Tcz
6+jJF85D5BNAG3DBMKBjAoGBAOAxZvgsKN+JuENXsST7F89Tck2iTcQIT8g5rwWC
P9Vt74yboe2kDT531w8+egz7nAmRBKNM751U/95P9t88EDacDI/Z2OwnuFQHCPDF
llYOUI+SpLJ6/vURRbHSnnn8a/XG+nzedGH5JGqEJNQsz+xT2axM0/W/CRknmGaJ
kda/AoGANWrLCz708y7VYgAtW2Uf1DPOIYMdvo6fxIB5i9ZfISgcJ/bbCUkFrhoH
+vq/5CIWxCPp0f85R4qxxQ5ihxJ0YDQT9Jpx4TMss4PSavPaBH3RXow5Ohe+bYoQ
NE5OgEXk2wVfZczCZpigBKbKZHNYcelXtTt/nP3rsCuGcM4h53s=
-----END RSA PRIVATE KEY-----
"""

HOME = os.path.expanduser("~/.mech")


class MechCommand(Command):
    def get(self, name, default=None):
        if not hasattr(self, 'mechfile'):
            self.mechfile = utils.load_mechfile()
        return self.mechfile.get(name, default)

    @property
    def vmx(self):
        self.get("")  # Check if there's a mechfile
        return utils.get_vmx()

    @property
    def box_name(self):
        box_name = self.get('box')
        if not box_name:
            puts_err(colored.red(textwrap.fill("Cannot find a box configured in the mechfile")))
            sys.exit(1)
        return box_name

    @property
    def box_version(self):
        return self.get('version')

    @property
    def user(self):
        return self.get('user', DEFAULT_USER)

    @property
    def password(self):
        return self.get('password', DEFAULT_PASSWORD)

    @property
    def config_ssh(self):
        vm = VMrun(self.vmx)

        ip = vm.getGuestIPAddress(wait=False) if vm.installedTools() else None
        if not ip:
            puts_err(colored.red(textwrap.fill(
                "This mech machine is reporting that it is not yet ready for SSH. "
                "Make sure your machine is created and running and try again. "
                "Additionally, check the output of `mech status` to verify "
                "that the machine is in the state that you expect."
            )))
            sys.exit(1)

        insecure_private_key = os.path.abspath(os.path.join(HOME, "insecure_private_key"))
        if not os.path.exists(insecure_private_key):
            with open(insecure_private_key, 'w') as f:
                f.write(INSECURE_PRIVATE_KEY)
        config = {
            "User": self.user,
            "Port": "22",
            "UserKnownHostsFile": "/dev/null",
            "StrictHostKeyChecking": "no",
            "PasswordAuthentication": "no",
            "IdentityFile": insecure_private_key,
            "IdentitiesOnly": "yes",
            "LogLevel": "FATAL",
        }
        config.update(self.get('config', {}).get('ssh', {}))
        config.update({
            "HostName": ip,
        })
        return config


class MechBox(MechCommand):
    """
    Usage: mech box <subcommand> [<args>...]

    Available subcommands:
        add               add a box to the catalog of available boxes
        list              list available boxes in the catalog
        outdated          checks for outdated boxes
        prune             removes old versions of installed boxes
        remove            removes a box that matches the given name
        repackage
        update

    For help on any individual subcommand run `mech box <subcommand> -h`
    """

    def add(self, arguments):
        """
        Add a box to the catalog of available boxes.

        Usage: mech box add [options] <name|url|path>

        Notes:
            The box descriptor can be the name of a box on HashiCorp's Vagrant Cloud,
            or a URL, a local .box or .tar file, or a local .json file containing
            the catalog metadata.

        Options:
            -f, --force                      Overwrite an existing box if it exists
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        url = arguments['<name | url | path>']
        name = arguments['--name']
        version = arguments['--box-version']
        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)
        utils.add_box(url, name=name, version=version, force=force, requests_kwargs=requests_kwargs)

    def list(self, arguments):
        """
        List all available boxes in the catalog.

        Usage: mech box list [options]

        Options:
            -i, --box-info                   Displays additional information about the boxes
            -h, --help                       Print this help
        """

        path = os.path.abspath(os.path.join(HOME, 'boxes'))
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.box'):
                dir = os.path.dirname(os.path.join(root, filename))[len(path) + 1:]
                print(dir)
    ls = list

    def outdated(self, arguments):
        """
        Checks if there is a new version available for the box.

        Usage: mech box outdated [options]

        Options:
                --global                     Check all boxes installed
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def prune(self, arguments):
        """
        Remove old versions of installed boxes.

        Usage: mech box prune [options]

        Notes:
            If the box is currently in use mech will ask for confirmation.

        Options:
            -n, --dry-run                    Only print the boxes that would be removed.
                --name NAME                  The specific box name to check for outdated versions.
            -f, --force                      Destroy without confirmation even when box is in use.
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def remove(self, arguments):
        """
        Remove a box from mech that matches the given name.

        Usage: mech box remove [options] <name>

        Options:
            -f, --force                      Remove without confirmation.
                --box-version VERSION        The specific version of the box to remove
                --all                        Remove all available versions of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def repackage(self, arguments):
        """
        Repackage the box that is in use in the current mech environment.

        Usage: mech box repackage [options] <name> <version>

        Notes:
            Puts it in the current directory so you can redistribute it.
            The name and version of the box can be retrieved using mech box list.

        Options:
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def update(self, arguments):
        """
        Update the box that is in use in the current mech environment.

        Usage: mech box update [options]

        Notes:
            Only if there any updates available. This does not destroy/recreate
            the machine, so you'll have to do that to see changes.

        Options:
            -f, --force                      Overwrite an existing box if it exists
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))


class MechSnapshot(MechCommand):
    """
    Usage: mech snapshot <subcommand> [<args>...]

    Available subcommands:
        delete            delete a snapshot taken previously with snapshot save
        list              list all snapshots taken for a machine
        pop               restore state that was pushed with `mech snapshot push`
        push              push a snapshot of the current state of the machine
        restore           restore a snapshot taken previously with snapshot save
        save              take a snapshot of the current state of the machine

    For help on any individual subcommand run `mech snapshot <subcommand> -h`
    """

    def delete(self, arguments):
        """
        Delete a snapshot taken previously with snapshot save.

        Usage: mech snapshot delete [options] <name>

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        vm = VMrun(self.vmx)
        if vm.deleteSnapshot(name) is None:
            puts_err(colored.red("Cannot delete snapshot"))
        else:
            puts_err(colored.green("Snapshot {} deleted".format(name)))

    def list(self, arguments):
        """
        List all snapshots taken for a machine.

        Usage: mech snapshot list [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        vm = VMrun(self.vmx)
        print(vm.listSnapshots())

    def pop(self, arguments):
        """
        Restore state that was pushed with `mech snapshot push`.

        Usage: mech snapshot pop [options]

        Options:
                --provision                  Enable provisioning
                --no-delete                  Don't delete the snapshot after the restore
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def push(self, arguments):
        """
        Push a snapshot of the current state of the machine.

        Usage: mech snapshot push [options]

        Notes:
            Take a snapshot of the current state of the machine and 'push'
            it onto the stack of states. You can use `mech snapshot pop`
            to restore back to this state at any time.

            If you use `mech snapshot save` or restore at any point after
            a push, pop will still bring you back to this pushed state.

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def restore(self, arguments):
        """
        Restore a snapshot taken previously with snapshot save.

        Usage: mech snapshot restore [options] <name>

        Options:
                --provision                  Enable provisioning
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def save(self, arguments):
        """
        Take a snapshot of the current state of the machine.

        Usage: mech snapshot save [options] <name>

        Notes:
            Take a snapshot of the current state of the machine. The snapshot
            can be restored via `mech snapshot restore` at any point in the
            future to get back to this exact machine state.

            Snapshots are useful for experimenting in a machine and being able
            to rollback quickly.

        Options:
            -f  --force                      Replace snapshot without confirmation
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        vm = VMrun(self.vmx)
        if vm.snapshot(name) is None:
            puts_err(colored.red("Cannot take snapshot"))
        else:
            puts_err(colored.green("Snapshot {} taken".format(name)))


class Mech(MechCommand):
    """
    Usage: mech [options] <command> [<args>...]

    Options:
        -v, --version                    Print the version and exit.
        -h, --help                       Print this help.
        --debug                          Show debug messages.

    Common commands:
        init              initializes a new mech environment by creating a mechfile
        destroy           stops and deletes all traces of the mech machine
        (up|start)        starts and provisions the mech environment
        (down|stop|halt)  stops the mech machine
        suspend           suspends the machine
        pause             pauses the mech machine
        ssh               connects to machine via SSH
        ssh-cconfig       outputs OpenSSH valid configuration to connect to the machine
        scp               copies files to and from the machine via SCP
        ip                outputs ip of the mech machine
        box               manages boxes: installation, removal, etc.
        (status|ps)       outputs status mech environments for this user
        provision         provisions the mech machine
        reload            restarts mech machine, loads new mechfile configuration
        resume            resume a paused/suspended mech machine
        snapshot          manages snapshots: saving, restoring, etc.
        port              displays information about guest port mappings
        push              deploys code in this environment to a configured destination

    For help on any individual command run `mech <command> -h`

    Example:

        Initializing and using a machine from HashiCorp's Vagrant Cloud:

            mech init bento/ubuntu-14.04
            mech up
            mech ssh
    """

    subcommand_name = '<command>'

    def __init__(self, arguments):
        super(Mech, self).__init__(arguments)

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if arguments['--debug']:
            logger.setLevel(logging.DEBUG)

    box = MechBox
    snapshot = MechSnapshot

    def init(self, arguments):
        """
        Initializes a new mech environment by creating a mechfile.

        Usage: mech init [options] [<name|url|path>]

        Notes:
            The box descriptor can be the name of a box on HashiCorp's Vagrant Cloud,
            or a URL, a local .box or .tar file, or a local .json file containing
            the catalog metadata.

        Options:
            -f, --force                      Overwrite existing mechfile
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        url = arguments['<name | url | path>']
        name = arguments['--name']
        version = arguments['--box-version']
        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        if os.path.exists('mechfile') and not force:
            puts_err(colored.red(textwrap.fill(
                "`mechfile` already exists in this directory. Remove it "
                "before running `mech init`."
            )))
            return

        puts_err(colored.green("Initializing mech"))
        if utils.init_mechfile(url, name=name, version=version, requests_kwargs=requests_kwargs):
            puts_err(colored.green(textwrap.fill(
                "A `mechfile` has been initialized and placed in this directory. "
                "You are now ready to `mech up` your first virtual environment!"
            )))
        else:
            puts_err(colored.red("Couldn't initialize mech"))

    def up(self, arguments):
        """
        Starts and provisions the mech environment.

        Usage: mech up [options]

        Options:
                --gui                        Start GUI
                --provision                  Enable provisioning
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        gui = arguments['--gui']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        vmx = utils.init_box(self.box_name, self.box_version, requests_kwargs=requests_kwargs)
        vm = VMrun(vmx)
        puts_err(colored.blue("Bringing machine up..."))
        started = vm.start(gui=gui)
        if started is None:
            puts_err(colored.red("VM not started"))
        else:
            time.sleep(3)
            puts_err(colored.blue("Getting IP address..."))
            ip = vm.getGuestIPAddress()
            puts_err(colored.blue("Sharing current folder..."))
            vm.addSharedFolder('mech', os.getcwd(), quiet=True)
            if ip:
                if started:
                    puts_err(colored.green("VM started on {}".format(ip)))
                else:
                    puts_err(colored.yellow("VM already was started on {}".format(ip)))
            else:
                if started:
                    puts_err(colored.green("VM started on an unknown IP address"))
                else:
                    puts_err(colored.yellow("VM already was started on an unknown IP address"))
    start = up

    def global_status(self, arguments):
        """
        Outputs mech environments status for this user.

        Usage: mech global-status [options]

        Options:
                --prune                      Prune invalid entries
            -h, --help                       Print this help
        """
        vm = VMrun()
        print(vm.list())
    ps = global_status

    def status(self, arguments):
        """
        Outputs status of the vagrant machine.

        Usage: mech status [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        vm = VMrun(self.vmx)
        box_name = self.box_name
        ip = vm.getGuestIPAddress()
        state = vm.checkToolsState()

        print("Current machine states:\n")
        print("%20s %16s %15s" % (box_name, ip, state))
        # default                   poweroff (virtualbox)

        # print("\nThe VM is powered off. To restart the VM, simply run `vagrant up`")

    def destroy(self, arguments):
        """
        Stops and deletes all traces of the mech machine.

        Usage: mech destroy [options]

        Options:
            -f, --force                      Destroy without confirmation.
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        force = arguments['--force']

        vmx = self.vmx
        directory = os.path.dirname(vmx)
        name = os.path.basename(directory)
        if force or utils.confirm("Are you sure you want to delete {name} at {directory}".format(name=name, directory=directory), default='n'):
            puts_err(colored.green("Deleting..."))
            vm = VMrun(vmx)
            vm.stop(mode='hard', quiet=True)
            time.sleep(3)
            shutil.rmtree(directory)
        else:
            puts_err(colored.red("Deletion aborted"))

    def down(self, arguments):
        """
        Stops the mech machine.

        Usage: mech down [options]

        Options:
                --force                      Force a hard stop
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        force = arguments['--force']

        vm = VMrun(self.vmx)
        if not force and vm.installedTools():
            stopped = vm.stop()
        else:
            stopped = vm.stop(mode='hard')
        if stopped is None:
            puts_err(colored.red("Not stopped", vm))
        else:
            puts_err(colored.green("Stopped", vm))
    stop = down
    halt = down

    def pause(self, arguments):
        """
        Pauses the mech machine.

        Usage: mech pause [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        vm = VMrun(self.vmx)
        if vm.pause() is None:
            puts_err(colored.red("Not paused", vm))
        else:
            puts_err(colored.yellow("Paused", vm))

    def resume(self, arguments):
        """
        Resume a paused/suspended mech machine.

        Usage: mech resume [options]

        Options:
                --provision                  Enable provisioning
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        vm = VMrun(self.vmx)

        # Try to unpause
        if vm.unpause(quiet=True) is not None:
            time.sleep(1)
            puts_err(colored.blue("Getting IP address..."))
            ip = vm.getGuestIPAddress()
            if ip:
                puts_err(colored.green("VM resumed on {}".format(ip)))
            else:
                puts_err(colored.green("VM resumed on an unknown IP address"))

        # Otherwise try starting
        else:
            started = vm.start()
            if started is None:
                puts_err(colored.red("VM not started"))
            else:
                time.sleep(3)
                puts_err(colored.blue("Getting IP address..."))
                ip = vm.getGuestIPAddress()
                puts_err(colored.blue("Sharing current folder..."))
                vm.enableSharedFolders()
                vm.addSharedFolder('mech', os.getcwd(), quiet=True)
                if ip:
                    if started:
                        puts_err(colored.green("VM started on {}".format(ip)))
                    else:
                        puts_err(colored.yellow("VM already was started on {}".format(ip)))
                else:
                    if started:
                        puts_err(colored.green("VM started on an unknown IP address"))
                    else:
                        puts_err(colored.yellow("VM already was started on an unknown IP address"))

    def suspend(self, arguments):
        """
        Suspends the machine.

        Usage: mech suspend [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        vm = VMrun(self.vmx)
        if vm.suspend() is None:
            puts_err(colored.red("Not suspended", vm))
        else:
            puts_err(colored.green("Suspended", vm))

    def ssh(self, arguments):
        """
        Connects to machine via SSH.

        Usage: mech ssh [options] [-- <extra ssh args>...]

        Options:
            -c, --command COMMAND            Execute an SSH command directly
            -p, --plain                      Plain mode, leaves authentication up to user
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        plain = arguments['--plain']
        extra = arguments['<extra ssh args>']
        command = arguments['--command']

        config_ssh = self.config_ssh
        if not config_ssh:
            puts_err(colored.red(""))
            sys.exit(1)

        with tempfile.NamedTemporaryFile() as fp:
            fp.write(utils.config_ssh_string(config_ssh))
            fp.flush()

            cmds = ['ssh']
            if not plain:
                cmds.extend(('-F', fp.name))
            if extra:
                cmds.extend(extra)
            if not plain:
                cmds.append('default')
            if command:
                cmds.extend(('--', command))

            logger.debug(" ".join("'{}'".format(c.replace("'", "\\'")) if ' ' in c else c for c in cmds))
            return subprocess.call(cmds)

    def ssh_config(self, arguments):
        """
        Output OpenSSH valid configuration to connect to the machine.

        Usage: mech ssh-config [options]

        Options:
            -h, --help                       Print this help
        """
        print(utils.config_ssh_string(self.config_ssh))

    def scp(self, arguments):
        """
        Copies files to and from the machine via SCP.

        Usage: mech scp [options] <src> <dst> [-- <extra scp args>...]

        Options:
                --user USERNAME
            -p, --plain                      Plain mode, leaves authentication up to user
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        if arguments['--plain']:
            authentication = ''
        else:
            user = arguments['--user']
            if user is None:
                user = self.user
            authentication = '{}@'.format(user)
        extra = arguments['<extra scp args>']
        src = arguments['<src>']
        dst = arguments['<dst>']

        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            src_is_host = src.startswith(":")
            dst_is_host = dst.startswith(":")

            if src_is_host and dst_is_host:
                puts_err(colored.red("Both src and host are host destinations"))
                sys.exit(1)

            if dst_is_host:
                dst = dst[1:]
                puts_err(colored.blue("Sending {src} to {authentication}{ip}:{dst}".format(
                    authentication=colored.green(authentication),
                    ip=colored.green(ip),
                    src=src,
                    dst=dst,
                )))
                cmd = 'scp {} {}{}:{}'.format(src, authentication, ip, dst)
            else:
                src = src[1:]
                puts_err(colored.blue("Getting {authentication}{ip}:{src} and saving in {dst}".format(
                    authentication=colored.green(authentication),
                    ip=colored.green(ip),
                    src=src,
                    dst=dst,
                )))
                cmd = 'scp {}{}:{} {}'.format(authentication, ip, src, dst)
            if extra:
                cmd += ' ' + ' '.join(extra)
            os.system(cmd)
        else:
            puts_err(colored.red("Unkown IP address"))

    def ip(self, arguments):
        """
        Outputs ip of the mech machine.

        Usage: mech ip [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """

        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            puts_err(colored.green(ip))
        else:
            puts_err(colored.red("Unkown IP address"))

    def provision(self, arguments):
        """
        Provisions the mech machine.

        Usage: mech provision [options]

        Options:
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        vm = VMrun(self.vmx, self.user, self.password)

        if not vm.installedTools():
            puts_err(colored.red("Tools not installed"))
            return

        provisioned = 0
        for i, provision in enumerate(self.get('provision', [])):

            if provision.get('type') == 'file':
                source = provision.get('source')
                destination = provision.get('destination')
                if utils.provision_file(vm, source, destination) is None:
                    puts_err(colored.red("Not Provisioned"))
                    return
                provisioned += 1

            elif provision.get('type') == 'shell':
                inline = provision.get('inline')
                path = provision.get('path')
                args = provision.get('args')
                if not isinstance(args, list):
                    args = [args]
                if utils.provision_shell(vm, inline, path, args) is None:
                    puts_err(colored.red("Not Provisioned"))
                    return
                provisioned += 1

            else:
                puts_err(colored.red("Not Provisioned ({}".format(i)))
                return
        else:
            puts_err(colored.green("Provisioned {} entries".format(provisioned)))
            return

        puts_err(colored.red("Not Provisioned ({}".format(i)))

    def reload(self, arguments):
        """
        Restarts mech machine, loads new mechfile configuration.

        Usage: mech reload [options]

        Options:
                --provision                  Enable provisioning
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def port(self, arguments):
        """
        Displays information about guest port mappings.

        Usage: mech port [options]

        Options:
                --guest PORT                 Output the host port that maps to the given guest port
                --machine-readable           Display machine-readable output
                --name BOX                   Name of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def push(self, arguments):
        """
        Deploys code in this environment to a configured destination.

        Usage: mech push [options] [<strategy>]

        Options:
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))
