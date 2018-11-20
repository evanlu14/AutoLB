from django.db import models
from . import util
import logging
from random import randint

logger = logging.getLogger(__name__)
MAX_NAME_LENGTH = 50
class Project(models.Model):
    user = models.CharField(max_length=MAX_NAME_LENGTH)
    # project name
    name = models.CharField(max_length=MAX_NAME_LENGTH)

    @classmethod
    def create(cls, user, name):
        try:
            project = Project.objects.get(user=user, name=name)
        except Project.DoesNotExist:
            project = Project(user=user, name=name)
            # save to db
            project.save()
            
            # create project ns
            project.create_ns()

        return project

    def delete(self, user, name):
        try:
            project = Project.objects.get(user=user, name=name)
        except Project.DoesNotExist:
            print("project doesn't exist...")
            return 

        for subnet in project.subnet_set.all():
            for vm in subnet.vm_set.all():
                vm.delete()
        project.delete_ns()

    def info(self):
        res = {
                "user": self.user,
                "name": self.name,
                "vms": []
        }
        for subnet in self.subnet_set.all():
            for vm in subnet.vm_set.all():
                vm_info = vm.info()
                res["vms"].append(vm_info)
        return res

    def __str__(self):
        return "id: " + str(self.pk) + ", user: " + self.user + ", name: " + self.name 

    def create_ns(self):
        ns_name = self.get_ns_name()
        # generate ns source ip
        octets = []
        for x in range(3):
            octets.append(str(randint(0,255)))
        source = '.'.join(octets)
        source = source + ".0"

        util._create_ns(ns_name, source)

    def delete_ns(self):
        ns_name = self.get_ns_name()
        util._remove_ns(ns_name)

    def get_ns_name(self):
        return util._get_ns_name(self.user, self.name, self.pk)

    @classmethod
    def listall(cls): 
        res =[str(item) for item in Project.objects.all()]
        # logger.info(res)
        return res

    def get_id(self):
        return self.pk
