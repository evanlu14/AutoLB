from django.db import models
from .project import Project
import logging

logger = logging.getLogger(__name__)
MAX_NAME_LENGTH = 50
class Subnet(models.Model):
    ip = models.CharField(max_length=MAX_NAME_LENGTH)
    project = models.ForeignKey('Project', on_delete = models.CASCADE)

    @classmethod
    def create(cls, ip, user, proj_name):
        """ create a new VM
        """
        try:
            project = Project.objects.get(user=user, name=proj_name)
        except Project.DoesNotExist:
            project = Project.create(user=user, name=proj_name)

        subnet = Subnet(ip = ip, project = project)

        # save to db
        subnet.save()

        return subnet

    def __str__(self):
        return "id: " + str(self.pk) + ", ip: " + self.ip + ", project: " + self.project

    @classmethod
    def listall(cls): 
        res =[str(item) for item in Subnet.objects.all()]
        # logger.info(res)
        return res

    def initializa(self):
        """ create a new network namespace
        """

    def add_vm(self, vm):
        """ create a new L2 bridge and attach to the namespace
        """

    def remove_vm(self, vm):
        """ detach and destroy corresponding bridge
        """