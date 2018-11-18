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

        vm.create_vm()

        return vm

    def create_vm(self):
        pass

    def delete(self):
        """ delete it
        """
        pass

    def initializa(self):
        """ install packets, collected and configure
        """
        pass
    
    def add_backend(self, ip):
        """ add a backend server
        """
        pass
    
    def remove_backend(self, ip):
        """ remove a backend server
        """
        pass
    
    def update_backend(self, old_ip, new_ip):
        """ update a bacend server
        """
        pass
    
    def attach_to_subnet(self):
        """ attack to subnet
        """
        pass