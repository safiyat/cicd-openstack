#! /usr/bin/env python

import apt
import yaml
from distutils.version import LooseVersion


class Color:
    PURPLE = '\033[95m'
    DARKCYAN = '\033[36m'

    BLACK = '\x1b[30m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    BLUE = '\x1b[34m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'
    WHITE = '\x1b[37m'
    BOLD = '\x1b[1m'
    UNDERLINE = '\x1b[4m'
    NORMAL = '\x1b(B\x1b[m'

    ON_BLACK = '\x1b[40m'
    ON_RED = '\x1b[41m'
    ON_GREEN = '\x1b[42m'
    ON_YELLOW = '\x1b[43m'
    ON_BLUE = '\x1b[44m'
    ON_MAGENTA = '\x1b[45m'
    ON_CYAN = '\x1b[46m'
    ON_WHITE = '\x1b[47m'

    REVERSE = '\x1b[7m'
    NO_UNDERLINE = '\x1b[24m'
    BLINK = '\x1b[5m'


filename = 'package_versions.yml'
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
        # if package['name'] not in cache_repo:
        #     print '%s%s: Package not in repo. %s' % \
        #         (Color.RED, package['name'], Color.NORMAL)
        #     continue
        # versions = cache_repo[package['name']].versions.keys()
        # if package['version'] == sorted(versions, reverse=True)[0]:
        #     # print '%s: All good.' % package['name']
        #     pass
        # elif package['version'] in versions:
        #     print '%s%s: Package will get updated from %s to %s. %s' % \
        #         (Color.GREEN, package['name'], package['version'],
        #          sorted(versions, reverse=True)[0], Color.NORMAL)
        # else:
        #     print '%s%s: Package version %s not in the repo. %s' % \
        #         (Color.BLUE, package['name'], package['version'],
        # Color.NORMAL)
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
    if package['installed'] == package['recommended'] == package['available']:
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
    print '| %s | %s | %s | %s |' % (package['name'].ljust(max_package_name),
                                     package['installed'].ljust(
                                         max_version_installed),
                                     package['recommended'].ljust(
                                         max_version_yaml),
                                     package['available'].ljust(
                                         max_version_repo)),
    print Color.NORMAL

print border
