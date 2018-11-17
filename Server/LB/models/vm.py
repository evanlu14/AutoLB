from django.db import models
from .project import Project
from .subnet import Subnet
from ..util.util_vm import *

MAX_NAME_LENGTH = 50
class VM(models.Model):
    subnet_id = models.ForeignKey('Subnet', on_delete=models.CASCADE)
    traffic = models.CharField(max_length=MAX_NAME_LENGTH)
    backends = models.TextField(null=True) # JSON-serialized, like ['192.168.1.1', '192.168.1.2']
    healthcheck = models.BooleanField(default=False)

    def __init__(self, user, proj_name, subnet, traffic_type, backend, healthcheck):
        project = Project.objects.get(user=user, name=proj_name)
        subnet = Subnet.objects.get(ip=subnet, project=project)
        self.subnet = subnet
        self.traffic = traffic_type
        self.backends = backend
        self.healthcheck = healthcheck

        name = get_vm_name(user, proj_name, id)
        create_vm(name)

    @classmethod
    def create(cls, user, proj_name, subnet, traffic_type, backend, healthcheck):
        """ create a new VM
        """
        vm = VM(user, proj_name, subnet, traffic_type, backend, healthcheck)
        return vm

    def delete(self):
        """ delete it
        """

    def initializa(self):
        """ install packets, collected and configure
        """
    
    def add_backend(self, ip):
        """ add a backend server
        """
    
    def remove_backend(self, ip):
        """ remove a backend server
        """
    
    def update_backend(self, old_ip, new_ip):
        """ update a bacend server
        """
    
    def attach_to_subnet(self):
        """ attack to subnet
        """