import os
import subprocess


def get_ansible_version():
    output = subprocess.check_output('ansible --version'.split())
    return output.splitlines()[0].split()[1]
