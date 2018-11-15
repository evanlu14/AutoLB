from django.db import models

MAX_NAME_LENGTH = 50
class Project(models.Model):
    user = models.CharField(max_length=MAX_NAME_LENGTH)
    # project name
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    subnets = models.ForeignKey('Subnet', on_delete = models.CASCADE)

    def __init__(self, user, name):
        self.user = user
        self.name = name

    @classmethod
    def create(cls, user, name):
        project = Project(user, name)
        return project

    # def init_subnet(self):
    #     """ create and initializa a network namespace
    #     """
    #     self.subnet.initialize()
    
    # def add_vm(self, vm):
    #     """ attach a new VM in the current project
    #     """
    #     self.subnet.add_vm(vm)
    #     self.vms.append(vm)

    # def remove_vm(self, vm):
    #     """ remove a VM from the current project
    #     """
    #     self.subnet.remove_vm(vm)
    #     self.vms.remove(vm)