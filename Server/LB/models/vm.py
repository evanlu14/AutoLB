from django.db import models
import os
from .project import Project
from .subnet import Subnet
from . import util

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
        id = project.get_id()
        if isinstance(id, int):
            id = str(id)

        name = util._get_vm_name(user, proj_name, id)
        vm.create_vm(name)
        vm.attach_to_ns(name)
        vm.config_lb()

        return vm

    def delete(self, name):
        self.delete_vm(name)
        self.detach_to_ns(name)

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

        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/attach.yml'))
        extra_vars = {"vm":name, "bridge_name":br_name, "target":name, "ip_int3":"1.1.4.1/24" }
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
        extra_vars = {"target":name, "vm":name, "mac_addr": "xxx"}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)

    def delete_vm(self, vm_name):
        """ delete the vm
        """
        playbook_path = os.path.normpath(os.path.join(util.ansible_path, 'VM/delete.yml'))
        extra_vars = {"target_vm": vm_name}
        util._run_playbook(playbook_path, util.hosts_path, extra_vars)
