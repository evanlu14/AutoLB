from django.db import models
import os
from .project import Project
from .subnet import Subnet
from . import util
from random import randint
import time

MAX_NAME_LENGTH = 50
class VM(models.Model):
    subnet = models.ForeignKey('Subnet', on_delete=models.CASCADE)
    traffic = models.CharField(max_length=MAX_NAME_LENGTH)
    backends = models.TextField(null=True) # JSON-serialized, like ['192.168.1.1', '192.168.1.2']
    healthcheck = models.BooleanField(default=False)

    @classmethod
    def create(cls, user, proj_name, subnet_ip, traffic_type, backend, healthcheck):
        """ create a new VM
        """
        try:
            project = Project.objects.get(user=user, name=proj_name)
        except Project.DoesNotExist:
            project = Project.create(user=user, name=proj_name)

        try:
            subnet = Subnet.objects.get(ip = subnet_ip, project_id = project)
        except Subnet.DoesNotExist:
            subnet = Subnet.create(subnet_ip, user, proj_name)

        vm = VM(subnet=subnet, traffic=traffic_type, backends=backend, healthcheck=healthcheck)

        vm.save()
        # create a VM
        id = project.get_id()
        if isinstance(id, int):
            id = str(id)
        name = util._get_vm_name(user, proj_name, id)
        vm.create_vm(name)

        # get the ip address
        ip_addr = ""
        while not ip_addr:
            time.sleep(10)
            util.mac_addr,ip_addr = util.get_ip(name)

        # rewrite hosts file
        with open(util.hosts_path, 'w') as f:
            f.write("[VMs]\n")
            f.write(ip_addr[:-3] + " ansible_connection=ssh ansible_ssh_user=zecao ansible_ssh_pass=123 ansible_ssh_common_args='-o StrictHostKeyChecking=no' ansible_sudo_pass='123'\n")

        vm.attach_to_ns(name)
        vm.config_lb()

        return vm

    def delete(self, name):
        self.detach_to_ns(name)
        self.delete_vm(name)

    def info(self):
        res = {
                "subnet": subnet,
                "traffic": traffic,
                "backends": backends,
                "healthcheck": healthcheck
        }
        return res

    def create_vm(self, name):
        """ just create
        """
        util._create_vm(name)

    def attach_to_ns(self, name):
        """ create L2, attach vm to L2 and L2 to ns
        """
        net_name = name + 'net'
        br_name = name + 'br'
        template_net = net_name + '.xml'
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'Subnet/create_net.yml'))
        extra_vars = {"net_name":net_name, "br_name": br_name, "template_net":template_net}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)

        # generate vm and ns source ip
        octets = []
        source = "10."
        for x in range(2):
            octets.append(str(randint(0,255)))
        source = source + '.'.join(octets)
        ip_int3 = source + ".1"
        ip_int3_n = ip_int3 + "/24"
        ip_vm = source + ".2/24"

        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/attach.yml'))
        extra_vars = {"vm":name, "bridge_name":br_name, "target":name, "ip_int3":ip_int3_n }
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)

        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/config.yml'))
        extra_vars = {"ip1":ip_vm, "ip2":ip_int3 }
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)


    def config_lb(self):
        """ config lb on vm
        """
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'LB/config.yml'))
        extra_vars = {"s_ip":"192.168.162.1"}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)

    def detach_to_ns(self, name):
        """ detach vm to L2, l2 to ns, delete l2
        """
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/dettach.yml'))
        mac_addr = util.mac_addr
        extra_vars = {"target":name, "vm":name, "mac_addr": mac_addr}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)

        net_name = name + 'net'
        br_name = name + 'br'
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'Subnet/delete_net.yml'))
        extra_vars = {"net_name":net_name, "br_name": br_name}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)


    def delete_vm(self, vm_name):
        """ delete the vm
        """
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/delete.yml'))
        extra_vars = {"target_vm": vm_name}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)
