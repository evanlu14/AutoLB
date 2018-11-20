# from ansible import playbook, callbacks
from os import listdir
from os.path import isfile, join
import subprocess

# namespace
def _create_ns(ns_name):
    path = "../ansible/Subnet/create_ns.yml"
    stats = _run_playbook(
        playbook_path=path,
        hosts_path='/SOME/OTHER/PATH/ansible_hosts',
        key_file='/OTHER/PATH/keys/id_rsa.pub')
    return 0

def _remove_ns(ns_name):
    pass

def _get_ns_name(user, proj_name, id):
    if isinstance(id, int):
        id = str(id)
    return user + "_" + proj_name + "_" + id

# vm
def _create_vm(vm_name):
    pass

def _get_vm_name(user, proj_name, id):
    return _get_ns_name(user, proj_name, id)
    # return user + proj_name + id

def _collectd_info(vm_name):
    res = {"if": {}, "memory": [], "cpu": []}

    BASE_PATH = "/var/lib/collectd/csv/"
    path = join(BASE_PATH, vm_name)
    path = join(path, "virt-" + vm_name)
    
    for f in listdir(path):
        fullpath = join(path, f)
        if f.startswith("if_packets"):
            ifname = f.split("-")[1]
            res["if"][ifname] = tail(fullpath, 10)
        elif f.startswith("memory-available"):
            res["memory"] = tail(fullpath, 10)
        elif f.startswith("virt_cpu_total"):
            res["cpu"] = tail(fullpath,10)

    return res

def tail(f, n):
    num = str(n)
    proc = subprocess.Popen(['tail', '-n', num, f], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    lines = [line.decode("utf-8").strip("\n") for line in lines]
    return lines[-n:]

# ansible
def _run_playbook(playbook_path, hosts_path, key_file):
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=0)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=0)
    playbook.PlayBook(
        playbook=playbook_path,
        # host_list=hosts_path,
        stats=stats,
        forks=4,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        # private_key_file=key_file
        ).run()
    return stats

def get_ip(hostname):
    """ get the ip of vm
        ensure vm only have one IP first
        return: ip address
    """
    ret = ""

    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    domainIDs = conn.listDomainsID()
    if domainIDs == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)
    if len(domainIDs) == 0:
        print('No active domains...')

    # For each ID, finding the corresponding MAC address and IP address.
    for domainID in domainIDs:
        dom = conn.lookupByID(domainID)
        if dom == None:
            print('Failed to get the domain object', file=sys.stderr)
        # get domain name
        curName = dom.name()
        if curName == hostname:
            # get all ip addresses 
            ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE, 0)
            for (name, val) in ifaces.iteritems():
                if val['addrs']:
                    for ipaddr in val['addrs']:
                        if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                            ret = ipaddr['addr'] 
                            # print("IPV4: " + ipaddr['addr'] + "/" +str(ipaddr["prefix"]))
                        # elif ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV6:
                        #     print("IPV6: " + ipaddr['addr'])
    conn.close()
    return ret
