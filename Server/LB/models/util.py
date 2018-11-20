# from ansible import playbook, callbacks
from os import listdir
from os.path import isfile, join
import subprocess
import libvirt
from xml.dom import minidom
import os
import sys
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
import hashlib

cur_dir = os.path.abspath('./')
ansible_path = os.path.normpath(os.path.join(cur_dir, 'LB/ansible/'))
hosts_path = os.path.normpath(os.path.join(ansible_path, 'hosts'))

# namespace
def _create_ns(ns_name, source):
    playbook_path = os.path.join(ansible_path, 'Subnet/create_ns.yml')

    source_list = source.split('.')
    source_list[3] = '2'
    ip_int1 = ".".join(source_list) + "/24"
    source_list[3] = '1'
    # ip_int2 should not have /24
    ip_int2 = ".".join(source_list)
    source = source + "/24"
    extra_vars = {"target_proj":ns_name, "ip_int1": ip_int1, "ip_int2": ip_int2, "source": source}

    print("ns create: ")
    print("ns: ", ns_name)
    print("ns: source ", source)
    print("ns: ip_int1 ", ip_int1)
    print("ns: ip_int2 ", ip_int2)

    _run_playbook(playbook_path, hosts_path, extra_vars)

def _remove_ns(ns_name):
    playbook_path = os.path.join(ansible_path, 'Subnet/delete_ns.yml')
    extra_vars = {"target_proj":ns_name}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _get_ns_name(user, proj_name, id):
    if isinstance(id, int):
        id = str(id)
    return hashlib.sha224((user + proj_name + id).encode('ascii')).hexdigest()[:5]

# vm
def _create_vm(vm_name):
    playbook_path = os.path.join(ansible_path, 'VM/create.yml')
    extra_vars = {"target_vm": vm_name}
    _run_playbook(playbook_path, hosts_path, extra_vars)

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
def _run_playbook(playbook_path, hosts_path, extra_vars):
    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=hosts_path)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    if not os.path.exists(playbook_path):
        print('[INFO] The playbook does not exist')
        sys.exit()

    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check','diff'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user='zecao', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False, diff=False)

    variable_manager.extra_vars = extra_vars # This can accomodate various other command line arguments.`

    passwords = dict()

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, options=options, passwords=passwords)

    results = pbex.run()

def get_ip(hostname):
    input_name = hostname

    target_ip = []

    # Connect to the local hypervisor and get all active domains' ID.
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
        print("=========VM %s =========" % (curName))
        # get all ip addresses 
        ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE, 0)
        #count = 1
        for (name, val) in ifaces.items():
            #print("%d->" % count)
            #count = count + 1
            if val['addrs']:
                for ipaddr in val['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        print("IPV4: " + ipaddr['addr'] + "/" +str(ipaddr["prefix"]))
                        if curName == input_name:
                            target_ip.append(ipaddr['addr'] + "/" +str(ipaddr["prefix"]))

    conn.close()
    if(target_ip == [])
        return ""
    return target_ip[0]

def get_mac(hostname):
    input_name = hostname

    target_mac_addr = []

    # Connect to the local hypervisor and get all active domains' ID.
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
        print("=========VM %s =========" % (curName))

        # get all mac addresses
        vm_xml = minidom.parseString(dom.XMLDesc(0))
        macs = vm_xml.getElementsByTagName('mac')
        for i in macs:
            val = i.attributes['address'].value
            print("MAC: " + val)
            if curName == input_name:
                target_mac_addr.append(val)

        # get all ip addresses 
        ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE, 0)
        #count = 1
        for (name, val) in ifaces.items():
            #print("%d->" % count)
            #count = count + 1
            if val['hwaddr']:
                print("MAC: %s" % (val['hwaddr']))
                if curName == input_name:
                    target_mac_addr.remove(val['hwaddr'])

    conn.close()
    if(target_mac_addr == [])
        return ""
    return target_mac_addr[0]
