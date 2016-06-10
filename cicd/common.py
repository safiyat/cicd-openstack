#! /usr/bin/env python

import ConfigParser
import os


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


class ConfigHelper(object):

    def __init__(self, path=None):
        if not path:
            self.path = os.path.join(os.environ['HOME'], '.cicd.conf')
        else:
            self.path = path
        self.path = os.path.abspath(self.path)
        self.conf = ConfigParser.ConfigParser()

    def write_conf(self, ansible_path, ansible_extra):
        self.conf = ConfigParser.ConfigParser()
        self.conf.add_section('ansible')
        self.conf.set('ansible', 'ansible', ansible_path)
        self.conf.set('ansible', 'ansible-extra', ansible_extra)
        with open(self.path, 'w') as configfile:
            self.conf.write(configfile)

    def read_conf(self):
        self.conf.read(self.path)
        ansible_path = self.conf.get('ansible', 'ansible')
        ansible_extra = self.conf.get('ansible', 'ansible-extra')
        return ansible_path, ansible_extra

    def get_conf(self):
        if os.path.isfile(self.path):
            return self.read_conf()
        print 'ERROR: Config file not found!.'
        exit()

    def init_conf(self):
        print 'Storing configuration at path %s' % self.path
        print 'Please enter the CI/CD configuration...'
        print '(For the ansible directories, enter including `ansible/`)'
        ansible_path = raw_input('    Ansible Root Directory: ')
        ansible_extra = raw_input('    Ansible Extras Directory: ')
        self.write_conf(ansible_path=ansible_path, ansible_extra=ansible_extra)


if __name__ == '__main__':
    # Script run for cicd.conf setup.
    print 'Running `.cicd.conf` setup...'
    conf = ConfigHelper()
    conf.init_conf()
