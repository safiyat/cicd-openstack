#! /usr/bin/env python

import apt
import yaml
from distutils.version import LooseVersion
from common import Color


def check_packages(filename):
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
                versions = r.versions.keys()
                versions.sort(key=LooseVersion)
                p['available'] = versions[-1]
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
        print color,
        print '| %s | %s | %s | %s |' % (
            package['name'].ljust(max_package_name),
            package['installed'].ljust(max_version_installed),
            package['recommended'].ljust(max_version_yaml),
            package['available'].ljust(max_version_repo)),
        print Color.NORMAL

    print border


# if __name__ == '__name__':
#     from common import ConfigHelper
#     conf = ConfigHelper(path='test/cicd.conf')
#     ansible_path, ansible_extra_path = conf.get_conf()
