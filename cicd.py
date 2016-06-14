#! /usr/bin/env python

import os
import sys
import paramiko
from cicd.common import ConfigHelper, Color
from cicd.fstab import parallel_sftp
from cicd.hostfilediff import read_hostfile, hostfile_diff, get_all
from cicd.hostfilediff import print_diff as print_diff_hostfile
from cicd.vm_info import get_vm_list, filter_vms
from cicd.yamldiff import read_yaml, yaml_diff
from cicd.yamldiff import print_diff as print_diff_yaml
sys.path.insert(0, 'utils.zip')
from utils import get_parser
import keystoneutils
import novautils


def main():
    p = get_parser()
    args = p.parse_args()
    session = keystoneutils.get_session(args)

    conf = ConfigHelper(path=os.path.join(os.environ['HOME'], '.cicd.conf'))
    config = conf.get_conf()
    ansible_path = config['ansible']['ansible_path']
    ansible_extra_path = config['ansible']['ansible_extra']

    if not os.path.isdir(os.path.join(ansible_path, 'cicd')):
        os.mkdir(os.path.join(ansible_path, 'cicd'))
    if not os.path.isdir(os.path.join(ansible_path, 'cicd/pre')):
        os.mkdir(os.path.join(ansible_path, 'cicd/pre'))
    if not os.path.isdir(os.path.join(ansible_path, 'cicd/pre/fstab')):
        os.mkdir(os.path.join(ansible_path, 'cicd/pre/fstab'))

    package_versions = os.path.join(ansible_path, 'package_versions.yml')
    hostname = 'controller'
    username = 'ubuntu'
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=hostname, username=username)
    sftp = client.open_sftp()
    sftp.put('cicd/apt_manage.py', '/tmp/apt_manage.py')
    sftp.put('cicd/common.py', '/tmp/common.py')
    sftp.put(package_versions, '/tmp/package_versions.yml')
    sftp.close()
    stdin, stdout, stderr = client.exec_command(
        'sudo python /tmp/apt_manage.py')
    output = stdout.read()
    print output

    # MySQL Backup
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname='10.41.3.201', username='root',
                   password='sdcloud#mysql#123')
    client.exec_command(
        'sudo su dba; /home/dba/admin/scripts/db_bkp_xtrabkp.sh -cq')

    # Hostfile Diff
    print '\n\n'
    old_hostfile = read_hostfile(os.path.join(ansible_extra_path, 'hostfile'))
    new_hostfile = read_hostfile(os.path.join(ansible_path, 'hostfile'))
    unchanged_hosts, deleted_hosts, new_hosts = hostfile_diff(new_hostfile,
                                                              old_hostfile)
    print_diff_hostfile(unchanged_hosts, deleted_hosts, new_hosts)

    # fstab
    parallel_sftp(get_all(new_hostfile['connet']),
                  os.path.join(ansible_path, 'cicd/pre/fstab'))
    parallel_sftp(get_all(new_hostfile['compute']),
                  os.path.join(ansible_path, 'cicd/pre/fstab'))

    # Collect detailed information about all the VMs in SDCloud
    nc = novautils.get_client(session)
    vms = get_vm_list(nc=nc, filename=os.path.join(ansible_path,
                                                   'cicd/pre/vm_info.json'))
    print '%s%s%s\n' % (Color.BOLD, 'VM States', Color.NORMAL)
    print '%sACTIVE: %s%s' % (Color.GREEN, len(filter_vms(vms,
                                                          status='ACTIVE')),
                              Color.NORMAL)
    print '%sERROR: %s%s' % (Color.RED, len(filter_vms(vms, status='ERROR')),
                             Color.NORMAL)
    print 'SHUTOFF: %s' % len(filter_vms(vms, status='SHUTOFF'))
    print 'Total VMs: %s' % len(vms)

    # YAML Diff
    print '\n'
    # base_vars.yml
    print '\n'
    old_basevars = read_yaml(os.path.join(ansible_extra_path, 'base_vars.yml'))
    new_basevars = read_yaml(os.path.join(ansible_path, 'base_vars.yml'))
    print '%s%s%sbase_vars.yml%s' % (Color.WHITE, Color.ON_BLACK, Color.BOLD,
                                     Color.NORMAL)
    unchanged_vars, changed_vars, deleted_vars, new_vars = yaml_diff(
        new_basevars, old_basevars)
    print_diff_yaml(new_basevars, old_basevars, unchanged_vars, changed_vars,
                    deleted_vars, new_vars)
    # my_vars.yml
    print '\n'
    old_myvars = read_yaml(os.path.join(ansible_extra_path, 'my_vars.yml'))
    new_myvars = read_yaml(os.path.join(ansible_path, 'my_vars.yml'))
    print '%s%s%smy_vars.yml%s' % (Color.WHITE, Color.ON_BLACK, Color.BOLD,
                                   Color.NORMAL)
    unchanged_vars, changed_vars, deleted_vars, new_vars = yaml_diff(
        new_myvars, old_myvars)
    print_diff_yaml(new_myvars, old_myvars, unchanged_vars, changed_vars,
                    deleted_vars, new_vars)
    # cinder_vars.yml
    print '\n'
    old_myvars = read_yaml(os.path.join(ansible_extra_path, 'cinder_vars.yml'))
    new_myvars = read_yaml(os.path.join(ansible_path, 'cinder_vars.yml'))
    print '%s%s%scinder_vars.yml%s' % (Color.WHITE, Color.ON_BLACK, Color.BOLD,
                                       Color.NORMAL)
    unchanged_vars, changed_vars, deleted_vars, new_vars = yaml_diff(
        new_myvars, old_myvars)
    print_diff_yaml(new_myvars, old_myvars, unchanged_vars, changed_vars,
                    deleted_vars, new_vars)


if __name__ == '__main__':
    main()
