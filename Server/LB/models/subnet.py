from django.db import models
from .project import Project

MAX_NAME_LENGTH = 50
class Subnet(models.Model):
    ip = models.CharField(max_length=MAX_NAME_LENGTH)
    project_id = models.ForeignKey('Project', on_delete = models.CASCADE)

    def __init__(self, ip, user, proj_name):
        project = Project.objects.get(user=user, name=proj_name)
        self.project = project
        self.ip = ip


    @classmethod
    def create(cls, ip, proj_name):
        """ create a new VM
        """
        vm = Subnet(ip, user, proj_name)
        return vm

    def initializa(self):
        """ create a new network namespace
        """

    def add_vm(self, vm):
        """ create a new L2 bridge and attach to the namespace
        """

    def remove_vm(self, vm):
        """ detach and destroy corresponding bridge
        """