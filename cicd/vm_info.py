import sys
import json
import time
sys.path.insert(0, 'utils.zip')
import keystoneutils
import novautils


def get_vm_list(output='file', **kwargs):
    """
    Get a detailed list of all VMs.


    """
    if 'args' in kwargs:
        nc = novautils.get_client(keystoneutils.get_session(kwargs['args']))
    elif 'session' in kwargs:
        nc = novautils.get_client(kwargs['session'])
    elif 'kc' in kwargs:
        nc = novautils.get_client(kwargs['kc'].session)
    elif 'nc' in kwargs:
        nc = kwargs['nc']
    else:
        raise(Exception('No session object passed.'))

    instances = nc.servers.list(search_opts={'all_tenants': 1})

    vm_list_json = '['
    for instance in instances:
        j = instance.to_dict()
        vm_list_json += json.dumps(j, indent=2)
        if instance is not instances[-1]:
            vm_list_json += ','
    vm_list_json += ']'

    if output == 'file':
        if 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = 'vm-list-%d.json' % int(time.time())
        f = open(filename, 'w')
        f.write(vm_list_json)
        f.close
    else:
        print vm_list_json

    return vm_list_json
