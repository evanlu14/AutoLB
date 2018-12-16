from django.db import models
from .project import Project
from . import util
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='log', filemode='a')
MAX_NAME_LENGTH = 50
class Subnet(models.Model):
    ip = models.CharField(max_length=MAX_NAME_LENGTH)
    project = models.ForeignKey('Project', on_delete = models.CASCADE)

    @classmethod
    def create(cls, ip, user, proj_name):
        """ create a new Subnet
        """
        project = Project.create(user=user, name=proj_name)

        try:
            subnet = Subnet.objects.get(ip=ip, project=project)
        except Subnet.DoesNotExist:
            subnet = Subnet(ip = ip, project = project)
            # save to db
            subnet.save()

            subnet.create_br()

        return subnet
    
    @classmethod
    def getby(cls, ip, user, proj_name):
        try:
            project = Project.objects.get(user=user, name=proj_name)
            subnet = Subnet.objects.get(ip=ip, project=project)
            return subnet
        except Project.DoesNotExist:
            logger.debug("Subnet.getby: can not find corresponding project")
            return None
        except Subnet.DoesNotExist:
            logger.debug("Subnet.getby: can not find corresponding subnet")
            return None

    def removebr(self):
        for instance in self.vm_set.all():
            instance.removeins()
        
        self.delete_br()
        self.delete()

    def __str__(self):
        return "id: {}, user: {}, name: {}, ip: {}".format(self.pk, self.project.user, self.project.name, self.ip)

    def info(self):
        res = {
            "id": self.pk,
            "ip": self.ip,
            "instance": [],
            "bridge": {
                "name": self.get_br_name()
            }
        }
        for instance in self.vm_set.all():
            res["instance"].append(instance.info())
        return res

    @classmethod
    def listall(cls): 
        res =[str(item) for item in Subnet.objects.all()]
        # logger.info(res)
        return res

    # helper method

    def create_br(self):
        br_name = self.get_br_name()
        util._create_br(br_name)

        ns_name = self.project.get_ns_name()
        util._attach_to_ns(br_name, ns_name, self.ip)

    def delete_br(self):
        br_name = self.get_br_name()
        util._delete_br(br_name)

    def get_project(self):
        return self.project

    def get_br_name(self):
        return util._get_br_name(self.project.name, self.pk)
