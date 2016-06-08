import sh
import re
from common import Color
import yaml

# base_vars = read_yaml(
#     'test/cloudprojectcirrus/src/infra/ansible/base_vars.yml')
# base_vars_new = read_yaml(
#     'test/cloudprojectcirrus/src/infra/ansible/base_vars_new.yml')
# unchanged_vars, changed_vars, deleted_vars, new_vars = yaml_diff(
#     base_vars_new, base_vars)
# print_diff(base_vars_new, base_vars, unchanged_vars, changed_vars,
#            deleted_vars, new_vars)


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


def read_yaml(filename):
    with open(filename, 'r') as stream:
            yml = yaml.load(stream)
    return yml


def yaml_diff(new, old):
    unchanged_vars = []
    changed_vars = []
    deleted_vars = []
    new_vars = list(set(new.keys()) - set(old.keys()))

    for key in old.keys():
        if key not in new:
            deleted_vars.append(key)
        elif old[key] == new[key]:
            unchanged_vars.append(key)
        else:
            changed_vars.append(key)

    return unchanged_vars, changed_vars, deleted_vars, new_vars


def print_diff(new, old, unchanged_vars, changed_vars, deleted_vars, new_vars,
               print_unchanged=False):
    if print_unchanged:
        for key in unchanged_vars:
            print Color.BOLD + key + ': ' + Color.NORMAL + str(old[key])

    print Color.RED
    for key in deleted_vars:
        print Color.BOLD + key + ': ' + Color.NORMAL + Color.RED + \
            str(old[key])

    print Color.NORMAL
    for key in changed_vars:
        print Color.BOLD + key + Color.NORMAL + ': ' + Color.RED + \
            str(old[key]) + ' ' + Color.GREEN + str(new[key]) + Color.NORMAL

    print Color.GREEN
    for key in new_vars:
        print Color.BOLD + key + ': ' + Color.NORMAL + Color.GREEN + \
            str(new[key])
    print Color.NORMAL
