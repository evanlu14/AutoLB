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

from random import randint
import logging
import docker
logger = logging.getLogger(__name__)

cur_dir = os.path.abspath('./')
ansible_path = os.path.normpath(os.path.join(cur_dir, 'LB/ansible/'))
hosts_path = os.path.normpath(os.path.join(ansible_path, 'hosts'))

DEBUG = 1
###############################################################################
# namespace
###############################################################################

def _create_ns(ns_name, source):
    if DEBUG:
        print("[DEBUG]create network namespace: {}".format(ns_name))
    playbook_path = os.path.join(ansible_path, 'Project/create_ns.yml')

    source = source.split("/")[0]
    source_list = source.split('.')
    source_list[3] = '2'
    ip_int1 = ".".join(source_list) + "/24"
    source_list[3] = '1'
    # ip_int2 should not have /24
    ip_int2 = ".".join(source_list)
    source = source + "/24"
    extra_vars = {"target_proj":ns_name, "ip_int1": ip_int1, "ip_int2": ip_int2, "source": source}

    # print("ns create: ")
    # print("ns: ", ns_name)
    # print("ns: source ", source)
    # print("ns: ip_int1 ", ip_int1)
    # print("ns: ip_int2 ", ip_int2)
    logger.info("ns_create: {}, ip: {}, int1: {}, int2: {}".format(ns_name, source, ip_int1, ip_int2))

    _run_playbook(playbook_path, hosts_path, extra_vars)

def _remove_ns(ns_name, ip):
    print("remove network namespace: {}".format(ns_name))
    playbook_path = os.path.join(ansible_path, 'Project/delete_ns.yml')
    extra_vars = {"target_proj":ns_name, "ip":ip}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _get_ns_name(user, proj_name, id):
    if isinstance(id, int):
        id = str(id)
    # return hashlib.sha224((user + proj_name + id).encode('ascii')).hexdigest()[:5]
    return user[:3] + proj_name[:3] + id

###############################################################################
# subnet
###############################################################################

def _get_br_name(proj_name, id):
    if isinstance(id, int):
        id = str(id)
    # return hashlib.sha224((user + proj_name + id).encode('ascii')).hexdigest()[:5]
    return proj_name[:3] + "br" + id

def _create_br(br_name, subnet_ip):
    """ subnet_ip example: 1.1.1.1/24
    """
    print("create bridge: {}".format(br_name))
    gateway_ip = _generate_gateway_ip(subnet_ip)
    playbook_path = os.path.join(ansible_path, 'Subnet/create_docker_br.yml')
    extra_vars = {"br_name": br_name, "gateway_ip": gateway_ip,"subnet_ip": subnet_ip}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _attach_to_ns(br_name, ns_name, subnet_ip):
    print("attach bridge to namespace: {} -> {}".format(br_name, ns_name))
    br_id = _get_docker_network_id(br_name)
    real_br_name = "br-" + br_id[:12]

    veth_ip = _generate_gateway_ip(subnet_ip) + "01"

    playbook_path = os.path.join(ansible_path, 'Subnet/attach_docker_br_to_ns.yml')
    extra_vars = {"br_name": br_name, "real_br_name": real_br_name,"ns_name": ns_name, "subnet_ip": subnet_ip, "veth_ip":veth_ip}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _delete_br(br_name):
    print("delete bridge: {}".format(br_name))
    playbook_path = os.path.join(ansible_path, 'Subnet/delete_docker_br.yml')
    extra_vars = {"br_name": br_name}
    _run_playbook(playbook_path, hosts_path, extra_vars)

###############################################################################
# vm
###############################################################################

def _create_vm(vm_name):
    playbook_path = os.path.join(ansible_path, 'VM/create.yml')
    extra_vars = {"target_vm": vm_name}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _create_ins(ins_name, br_name):
    """ create a new docker container
    """
    print("create instance: {}".format(ins_name))
    playbook_path = os.path.join(ansible_path, 'Container/create_ctn.yml')
    extra_vars = {"ctn_name": ins_name, "br_name": br_name}
    _run_playbook(playbook_path, hosts_path, extra_vars)

def _get_vm_name(user, proj_name, id):
    return _get_ns_name(user, proj_name, id)

def _get_ins_name(user, proj_name, id):
    return _get_ns_name(user, proj_name, id)
    
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
    if not target_ip:
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
    if not target_mac_addr:
        return ""
    return target_mac_addr[0]

###############################################################################
# helper
###############################################################################

def _generate_ip():
    octets = []
    source = "102."
    for x in range(2):
        octets.append(str(randint(0,255)))
    source = source + '.'.join(octets)
    source = source + ".0/24"
    return source

def _generate_gateway_ip(subnet_ip):
    ip = subnet_ip.split("/")[0]
    mask = int(subnet_ip.split("/")[1])
    ip_list = ip.split(".")
    if mask == 24:
        ip_list[3] = "1"
    elif mask == 16:
        ip_list[2] = "0"
        ip_list[3] = "1"
    elif mask == 8:
        ip_list[1] = "0"
        ip_list[2] = "0"
        ip_list[3] = "1"
    str_dot = "."
    gateway_ip = str_dot.join(ip_list)
    return gateway_ip

def _get_docker_network_id(br_name):
    client = docker.from_env() 
    try:
        id = client.networks.get(network_id=br_name).id
        return id
    except docker.errors.NotFound:
        logger.debug("util._get_docker_network_id: not found by name")
        return None