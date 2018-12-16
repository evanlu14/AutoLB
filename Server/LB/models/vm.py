from django.db import models
import os
from .project import Project
from .subnet import Subnet
from . import util
from random import randint
import time
import subprocess

MAX_NAME_LENGTH = 50
class VM(models.Model):
    subnet = models.ForeignKey('Subnet', on_delete=models.CASCADE)
    backends = models.TextField(null=True) # JSON-serialized, like ['192.168.1.1', '192.168.1.2']
    healthcheck = models.BooleanField(default=False)
    port_num = models.IntegerField(null=True)

    @classmethod
    def create(cls, user, proj_name, subnet_ip, backends, healthcheck):
        """ create a new VM
        """
        subnet = Subnet.create(ip=subnet_ip, user=user, proj_name=proj_name)

        try:
            ins = VM.objects.get(subnet=subnet, backends=backends, healthcheck=healthcheck)
        except VM.DoesNotExist:
            ins = VM(subnet=subnet, backends=backends, healthcheck=healthcheck)
            port_num = ins.get_port_number()
            ins.port_num = port_num
            ins.save()

            ins.create_ins()
            ins.config_lb()

        return ins

    def delete(self, name):
        self.detach_to_ns(name)
        self.delete_vm(name)

    def info(self):
        res = {
                "id": self.pk,
                "backends": self.backends,
                "healthcheck": self.healthcheck,
                "port_num": self.port_num,
                "instance": {
                    "name": self.get_ins_name()
                }
        }
        return res

    def create_ins(self):
        """ create a instance
        """
        ins_name = self.get_ins_name()
        br_name = self.subnet.get_br_name()
        util._create_ins(ins_name, br_name)

    def attach_to_subnet(self):
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
        pass
        # playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'LB/config.yml'))
        # extra_vars = {"s_ip":"192.168.162.1"}
        # util._run_playbook(playbook_path, util.hosts_path, extra_vars)

    def detach_to_ns(self, name):
        """ detach vm to L2, l2 to ns, delete l2
        """
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/dettach.yml'))
        mac_addr = util.get_mac(name)
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

    def get_ins_name(self):
        project = self.subnet.get_project()
        return util._get_ins_name(project.user, project.name, self.pk)

    def get_port_number(self):
        is_occupied = True
        port_num = randint(10000, 20000)
        while VM.objects.filter(port_num=port_num).exists():
            port_num = randint(10000, 20000)
        return port_num