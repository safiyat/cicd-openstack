import ConfigParser
import os


class ConfigHelper(object):

    def __init__(self, path=None):
        if not path:
            self.path = os.environ['HOME'] + '/cicd.cfg'
        else:
            self.path = path
        self.conf = ConfigParser.ConfigParser()

    def write_conf(self, ansible_path, ansible_extra=None):
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

    def init_config(self):
        print 'Storing configuration at path %s' % self.path
        print 'Please enter the CI/CD configuration...'
        print '(For the ansible directories, enter including `ansible/`)'
        ansible_path = raw_input('    Ansible Root Directory:')
        ansible_extra = raw_input('    Ansible Extras Directory:')
        self.write_conf(ansible_path=ansible_path, ansible_extra=ansible_extra)
