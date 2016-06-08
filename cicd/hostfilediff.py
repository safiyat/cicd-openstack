import sh
import re
import os
from common import Color


def get_files_changed():
    # To remove colors and return carriages
    ansi_escape = re.compile('(\x1b(=|>|(\[[^mKhl]*[mKhl])))|\r')
    git = sh.git.bake()
    # Get last two commits
    commit = ansi_escape.sub('', git('log', '-n 2',
                                     '--pretty=format:%H').stdout).splitlines()
    # Get the differing files between the last two commits.
    file_list = ansi_escape.sub('', git('diff', '--name-only', commit[0],
                                        commit[1]).stdout).splitlines()
    return file_list


def read_hostfile(filename):
    def expand_range(ranged_ip):
        prefix = ranged_ip[:ranged_ip.find('[')]
        start, end = [int(x) for x in ranged_ip[
            ranged_ip.find('[') + 1:ranged_ip.find(']')].split(':')]
        hosts = []
        for i in range(start, end + 1):
            hosts.append(prefix + str(i))
        return hosts

    def get_parent(child, text):
        place_of_birth = text.find('\n%s\n' % child)
        if place_of_birth == -1:
            return None
        return text[text.rfind('\n[', 0, place_of_birth) +
                    2:].splitlines()[0][:-10]

    text = open(filename, 'r').read()

    # Remove comments and blank lines
    comments = re.compile('^\s*#.*$', re.MULTILINE)
    text = comments.sub('', text)
    text = os.linesep.join([s for s in text.splitlines() if s])

    # Find ranged IPs
    ranged_ip = re.compile('^\d+\.\d+.\d+.\[\d+:\d+\]', re.MULTILINE)

    # Retrieve host groups
    leaf_group = re.compile('^\[[^:\]\s]*\]', re.MULTILINE)
    leaves = [x.strip('[]') for x in leaf_group.findall(text)]

    leaf_hosts = {}
    for leaf in leaves:
        start = text.find('[%s]' % leaf)
        end = text.find('\n[', start)
        if end == -1:  # EOF reached. No '['
            end = len(text)
        hosts = text[start:end].splitlines()[1:]
        leaf_hosts[leaf] = []
        for host in hosts:
            if ranged_ip.match(host):
                leaf_hosts[leaf] += expand_range(host)
            else:
                leaf_hosts[leaf].append(host)

    host_tree = {}
    while leaf_hosts:
        for leaf in leaf_hosts.keys():
            parent = get_parent(leaf, text)
            if not parent:
                if leaf in host_tree:
                    host_tree[leaf].update(leaf_hosts[leaf].items())
                    leaf_hosts.pop(leaf)
                else:
                    host_tree[leaf] = leaf_hosts.pop(leaf)
            else:
                if parent not in leaf_hosts:
                    leaf_hosts[parent] = {}
                leaf_hosts[parent][leaf] = leaf_hosts.pop(leaf)

    return host_tree


# def hostfile_diff(new, old, unchanged_hosts={}, deleted_hosts={},
#                   new_hosts={}):
#     print type(new), type(old)
#     if type(new) is list and type(old) is list:
#         unchanged_hosts = []
#         deleted_hosts = []
#         new_hosts = []
#         new_hosts.append(list(set(new) - set(old)))
#         deleted_hosts.append(list(set(old) - set(new)))
#         unchanged_hosts.append(list(set(new).intersection(set(old))))
#     elif type(new) is list and type(old) is dict:
#         new_hosts = new
#         deleted_hosts = old
#     elif type(new) is dict and type(old) is list:
#         new_hosts = new
#         deleted_hosts = old
#     else:
#         new_keys = set(new.keys()) - set(old.keys())
#         deleted_keys = set(old.keys()) - set(new.keys())
#         for key in new_keys:
#             new_hosts[key] = new[key]
#         for key in deleted_keys:
#             deleted_hosts[key] = old[key]
#         for key in list(set(old.keys()).intersection(set(new.keys()))):
#             u_hosts, d_hosts, n_hosts = hostfile_diff(new[key], old[key])
#             unchanged_hosts[key] = u_hosts
#             deleted_hosts[key] = d_hosts
#             new_hosts[key] = n_hosts
#     return unchanged_hosts, deleted_hosts, new_hosts


def hostfile_diff(new, old):
    unchanged_hosts = {}
    deleted_hosts = {}
    new_hosts = {}
    if new == old:
        unchanged_hosts = old
    elif type(new) is list and type(old) is list:
        unchanged_hosts = list(set(new).intersection(set(old)))
        new_hosts = list(set(new) - set(old))
        deleted_hosts = list(set(old) - set(new))
    elif type(new) is list or type(old) is list:
        new_hosts = new
        deleted_hosts = old
    # Both are dictionaries
    else:
        new_keys = set(new.keys()) - set(old.keys())
        deleted_keys = set(old.keys()) - set(new.keys())
        for key in new_keys:
            new_hosts[key] = new[key]
        for key in deleted_keys:
            deleted_hosts[key] = old[key]
        for key in (set(new.keys()) - new_keys):
            u_h, d_h, n_h = hostfile_diff(new[key], old[key])
            if not d_h and not n_h:
                unchanged_hosts[key] = u_h
            else:
                unchanged_hosts[key] = u_h
                deleted_hosts[key] = d_h
                new_hosts[key] = n_h
    return unchanged_hosts, deleted_hosts, new_hosts


def print_diff(unchanged_hosts, deleted_hosts, new_hosts,
               print_unchanged=False):
    def print_subtree(tree):
        if type(tree) is dict:
            for key in tree.keys():
                print '[%s]' % key
                print_subtree(tree[key])
        else:
            for ip in tree:
                print ip

    print Color.RED,
    deleted = set(deleted_hosts.keys()) - set(unchanged_hosts.keys())
    for key in deleted:
        print '[%s]' % key
        print_subtree(deleted_hosts[key])

    print Color.NORMAL,
    print

    unchanged = set(unchanged_hosts.keys()).intersection(
        set(deleted_hosts.keys()).intersection(set(new_hosts.keys())))
    for key in unchanged:
        print '[%s]' % key
        print Color.RED,
        print_subtree(deleted_hosts[key])
        if print_unchanged:
            print Color.NORMAL,
            print_subtree(unchanged_hosts[key])
        print Color.GREEN,
        print_subtree(new_hosts[key])
        print Color.NORMAL,

    print Color.GREEN,
    print

    new = set(new_hosts.keys()) - set(unchanged_hosts.keys())
    for key in new:
        print '[%s]' % key
        print_subtree(new_hosts[key])
    # if print_unchanged:
    #     for key in unchanged_vars:
    #         print Color.BOLD + key + ': ' + Color.NORMAL + str(old[key])

    # print Color.RED
    # for key in deleted_vars:
    #     print Color.BOLD + key + ': ' + Color.NORMAL + Color.RED + \
    #         str(old[key])

    # print Color.NORMAL
    # for key in changed_vars:
    #     print Color.BOLD + key + Color.NORMAL + ': ' + Color.RED + \
    #         str(old[key]) + ' ' + Color.GREEN + str(new[key]) + Color.NORMAL

    # print Color.GREEN
    # for key in new_vars:
    #     print Color.BOLD + key + ': ' + Color.NORMAL + Color.GREEN + \
    #         str(new[key])
    print Color.NORMAL
