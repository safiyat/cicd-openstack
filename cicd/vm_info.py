import sys
import json
import time
from common import Color
sys.path.insert(0, 'utils.zip')
import keystoneutils
import novautils


def get(list_of_dict, key, value):
    """
    Retrieve dictionaries matching the key-value pair from a list of
    dictionaries.
    """
    o = filter(lambda dictionary: dictionary[key] == value,
               list_of_dict)
    return o


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

    return json.loads(vm_list_json)


def filter_vms(vm_list, **kwargs):
    """
    Filter the vm list for vms based on specified parameters.

    :param list vm_list: A list of dictionaries containing information about
                         the VMs.

    kwargs:
        :param string name:       The name of the VMs to be filtered.
        :param string ip_addr:    The IP address of the VMs to be filtered.
        :param string flavor_id:     The flavor ID of the VMs to be filtered.
        :param string uuid:       The uuid of the VMs to be filtered.
        :param string tenant_id:  The tenant ID of the VMs to be filtered.
        :param string user_id:    The user ID of the VMs to be filtered.
        :param string status:     Status of the VMs to be filtered.
        :param string hypervisor: The hypervisor of the VMs to be filtered.
    """
    filter_list = ['name', 'ip_addr', 'flavor_id', 'uuid', 'tenant_id',
                   'user_id', 'status', 'hypervisor']

    # filters = {}
    for (key, value) in kwargs.items():
        if key not in filter_list:
            raise(Exception('Invalid keyword argument: %s' % key))
        # filters[key] = value

    filtered = vm_list
    if 'name' in kwargs:
        filtered = filter(lambda d: d['name'] == kwargs['name'], filtered)
    if 'ip_addr' in kwargs:
        filtered = filter(lambda d: d['addresses'].values()[0][0]['addr'] ==
                          kwargs['ip_addr'], filtered)
    if 'flavor_id' in kwargs:
        filtered = filter(lambda d: d['flavor']['id'] == kwargs['flavor_id'],
                          filtered)
    if 'uuid' in kwargs:
        filtered = filter(lambda d: d['id'] == kwargs['uuid'], filtered)
    if 'tenant_id' in kwargs:
        filtered = filter(lambda d: d['tenant_id'] == kwargs['tenant_id'],
                          filtered)
    if 'user_id' in kwargs:
        filtered = filter(lambda d: d['user_id'] == kwargs['user_id'],
                          filtered)
    if 'status' in kwargs:
        filtered = filter(lambda d: d['status'] == kwargs['status'], filtered)
    if 'hypervisor' in kwargs:
        filtered = filter(lambda d: d['OS-EXT-SRV-ATTR:host'] ==
                          kwargs['hypervisor'], filtered)

    return filtered


def get_vm_state_count(vm_list):
    vm_state_list = {'ACTIVE': {'color':Color.GREEN, 'count':0},
                     'ERROR': {'color':Color.RED, 'count':0},
                     'SHUTOFF': {'color':Color.ON_BLACK, 'count':0}}
    for vm in vm_list:
        if vm['status'] == 'ACTIVE':
            vm_state_list['ACTIVE']['count'] += 1
        elif vm['status'] == 'ERROR':
            vm_state_list['ERROR']['count'] += 1
        elif vm['status'] == 'SHUTOFF':
            vm_state_list['SHUTOFF']['count'] += 1
        else:
            state = vm['status']
            if state not in vm_state_list:
                vm_state_list[state] = {'color': Color.NORMAL, 'count': 0}
            vm_state_list[state]['count'] += 1

    return vm_state_list


def get_vm_state_diff(old, new):
    vm_state_diff = []
    for vm in old:
        vm_new = get(new, 'id', vm['id'])
        if not vm_new:
            vm['new_status'] = 'DELETED'
        elif vm_new[0]['status'] != vm['status']:
            vm['new_status'] = vm_new[0]['status']
        else:
            continue
        vm_state_diff.append(vm)

    return vm_state_diff


def print_vm_info(vm_list):
    if type(vm_list) is not list:
        vm_list = [vm_list]
    if 'new_status' in vm_list[0]:
        headers = ['ID', 'Name', 'Host', 'User', 'Tenant', 'Status',
                   'New Status']
        column_width = [36, 4, 4, 4, 32, 13, 13]
    else:
        headers = ['ID', 'Name', 'Host', 'User', 'Tenant', 'Status']
        column_width = [36, 4, 4, 4, 32, 13]
    output_list = []
    for vm in vm_list:
        info = {'id': vm['id']}
        info['name'] = vm['name']
        info['hypervisor'] = vm['OS-EXT-SRV-ATTR:host']
        info['user'] = vm['user_id']
        info['tenant'] = vm['tenant_id']
        info['status'] = vm['status']
        if 'new_status' in vm:
            info['new_status'] = vm['new_status']
        output_list.append(info)

        if column_width[1] < len(info['name']):
            column_width[1] = len(info['name'])
        if column_width[2] < len(info['hypervisor']):
            column_width[2] = len(info['hypervisor'])
        if column_width[3] < len(info['user']):
            column_width[3] = len(info['user'])

    header_line = '+%s+' % ('+'.join(['-' * (x + 2) for x in column_width]))
    for i in range(len(headers)):
        headers[i] = headers[i].center(column_width[i] + 2)

    print header_line
    print '|%s|' % ('|'.join(headers))
    print header_line
    for info in output_list:
        if 'new_status' in info:
            print '| %s | %s | %s | %s | %s | %s | %s |' % (
                info['id'].ljust(column_width[0]),
                info['name'].ljust(column_width[1]),
                info['hypervisor'].ljust(column_width[2]),
                info['user'].ljust(column_width[3]),
                info['tenant'].ljust(column_width[4]),
                info['status'].ljust(column_width[5]),
                info['new_status'].ljust(column_width[6]))
        else:
            print '| %s | %s | %s | %s | %s | %s |' % (
                info['id'].ljust(column_width[0]),
                info['name'].ljust(column_width[1]),
                info['hypervisor'].ljust(column_width[2]),
                info['user'].ljust(column_width[3]),
                info['tenant'].ljust(column_width[4]),
                info['status'].ljust(column_width[5]))
    print header_line
