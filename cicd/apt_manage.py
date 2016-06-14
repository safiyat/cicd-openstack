#! /usr/bin/env python

import apt
import os
import paramiko
import time
import yaml
from common import Color


def check_packages(filename, print_diff=True):
    with open(filename, 'r') as stream:
        yml = yaml.load(stream)

    cache_local = apt.cache.Cache()
    cache_local.open()
    cache_repo = apt.cache.Cache()
    cache_repo.update()
    cache_repo.open()

    missing = ['non-existent-package']

    max_package_name = 0
    max_version_yaml = 0
    max_version_installed = 0
    max_version_repo = 0
    package_details = []

    for component in yml.keys():
        for package in yml[component]:
            if package['name'] in missing:
                continue

            p = {'name': package['name'], 'recommended': package['version']}

            if p['name'] in cache_local:
                l = cache_local[p['name']]
                if l.is_installed:
                    p['installed'] = l.installed.version
                else:
                    p['installed'] = '-'
            else:
                p['installed'] = '-'

            if p['name'] in cache_repo:
                r = cache_repo[p['name']]
                p['available'] = r.candidate.version
            else:
                p['available'] = '-'

            package_details.append(p)

            if max_package_name < len(p['name']):
                max_package_name = len(p['name'])
            if max_version_yaml < len(p['recommended']):
                max_version_yaml = len(p['recommended'])
            if max_version_installed < len(p['installed']):
                max_version_installed = len(p['installed'])
            if max_version_repo < len(p['available']):
                max_version_repo = len(p['available'])

    total_length = 2 + max_package_name + 3 + max_version_yaml + 3 + \
        max_version_installed + 3 + max_version_repo
    border = ' %s ' % ('-' * total_length)
    print ' ' + border
    print Color.BOLD,
    print '| %s | %s | %s | %s |' % ('Package'.center(max_package_name),
                                     'Installed'.center(max_version_installed),
                                     'Recommended'.center(max_version_yaml),
                                     'Available'.center(max_version_repo))
    print Color.NORMAL,
    print border
    for package in package_details:
        # All good.
        if package['installed'] == package['recommended'] == \
           package['available']:
            color = Color.NORMAL
        # Not installed. Not available. Recommended.
        elif package['installed'] == package['available'] == '-':
            color = Color.ON_RED
        # Will be installed.
        elif package['installed'] == '-':
            color = Color.ON_GREEN
        # Installed. Will be updated.
        elif package['installed'] != package['available'] \
                and package['available'] != '-':
            color = Color.GREEN
        else:
            color = Color.NORMAL
        if color == Color.NORMAL and print_diff:
            continue
        print color,
        print '| %s | %s | %s | %s |' % (
            package['name'].ljust(max_package_name),
            package['installed'].ljust(max_version_installed),
            package['recommended'].ljust(max_version_yaml),
            package['available'].ljust(max_version_repo)),
        print Color.NORMAL

    print border


def get_apt_list(hostname, username, ansible_path):
    package_versions = os.path.join(ansible_path, 'package_versions.yml')
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
    print '%s%s%s:' % (Color.BOLD, hostname, Color.NORMAL)
    print output
    open(os.path.join(ansible_path, 'cicd/pre/package_versions_%s' % hostname),
         'w').write(output)
    os._exit(0)


def parallel_get_apt_list(hostnames, username, ansible_path):
    start = time.time()
    children = []
    for hostname in hostnames:
        pid = os.fork()
        if pid:
           children.append(pid)
        else:
            get_apt_list(hostname, username, ansible_path)
            os._exit(0)

    for i, child in enumerate(children):
        os.waitpid(child, 0)
    # print children
    print 'Gathered package info from %s hosts in %.2f seconds.' % (
        len(hostnames), time.time() - start)

if __name__ == '__main__':
    check_packages('/tmp/package_versions.yml')
