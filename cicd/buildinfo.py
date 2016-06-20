import os
import paramiko
import time


def copy_buildinfo(hostname, destination):
    # print '[%s] Copying from %s' % (time.time(), hostname)
    username = 'ubuntu'
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=hostname, username=username)
    sftp = client.open_sftp()
    sftp.get('/etc/sdcloud/.buildinfo', os.path.join(destination, 'buildinfo_%s' % hostname))
    sftp.close()
    # print '[%s] Copied from %s' % (time.time(), hostname)
    os._exit(0)


def parallel_sftp(hosts, destination):
    start = time.time()
    children = []
    for host in hosts:
        pid = os.fork()
        if pid:
           children.append(pid)
        else:
            copy_buildinfo(host, destination)
            os._exit(0)

    for i, child in enumerate(children):
        os.waitpid(child, 0)
    # print children
    print 'Copied %s buildinfo files in %.2f seconds.' % (len(hosts), time.time() - start)
