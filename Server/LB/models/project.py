from django.db import models
from .util import _create_ns, _get_ns_name

MAX_NAME_LENGTH = 50
class Project(models.Model):
    user = models.CharField(max_length=MAX_NAME_LENGTH)
    # project name
    name = models.CharField(max_length=MAX_NAME_LENGTH)

    @classmethod
    def create(cls, user, name):
        project = Project(user=user, name=name)

        # save to db
        project.save()

        # create project ns
        project.create_ns()

        return project

    def __str__(self):
        return "id: " + str(self.pk) + ", user: " + self.user + ", name: " + self.name 

    def create_ns(self):
        ns_name = self.get_ns_name()
        _create_ns(ns_name)

    def get_ns_name(self):
        return _get_ns_name(self.user, self.name, self.pk)

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

    def info(self):
        pass
