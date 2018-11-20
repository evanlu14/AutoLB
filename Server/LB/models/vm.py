from django.db import models
from .project import Project
from .subnet import Subnet
from .util import *

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

        vm.create_vm(user, proj_name, project)
        vm.attach_to_ns()
        vm.config_lb()

        return vm

    def delete(self):
        self.delete_vm()
        self.detach_to_ns()

    def info(self):
        res = {
                "subnet": subnet,
                "traffic": traffic,
                "backends": backends,
                "healthcheck": healthcheck
        }
        return res

    def create_vm(self, user, proj_name, id):
        """ just create
        """
        name = _get_vm_name(user, proj_name, id)
        _create_vm(name)

    def attach_to_ns(self):
        """ create L2, attach vm to L2 and L2 to ns
        """
        pass

    def config_lb(self):
        """ config lb on vm
        """
        pass

    def detach_to_ns(self):
        """ detach vm to L2, l2 to ns, delete l2
        """
        pass

    def delete_vm(self, vm_name):
        """ delete the vm
        """
        cur_dir = os.path.abspath('./')
        playbook_path = os.path.join(cur_dir, '../ansible/VM/delete.yml')
        hosts_path = os.path.join(cur_dir, '../ansible/hosts')
        extra_vars = {"target_vm": vm_name}
        _run_playbook(playbook_path, hosts_path, extra_vars)
