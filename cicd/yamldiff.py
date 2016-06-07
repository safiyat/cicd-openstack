import sh
import re
import yaml

# base_vars = read_yaml(
#     'test/cloudprojectcirrus/src/infra/ansible/base_vars.yml')
# base_vars_new = read_yaml(
#     'test/cloudprojectcirrus/src/infra/ansible/base_vars_new.yml')
# unchanged_vars, changed_vars, deleted_vars, new_vars = yaml_diff(
#     base_vars_new, base_vars)
# print_diff(base_vars_new, base_vars, unchanged_vars, changed_vars,
#            deleted_vars, new_vars)


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
