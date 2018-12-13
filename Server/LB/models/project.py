from django.db import models
from . import util
import logging
from random import randint
logger = logging.getLogger(__name__)
# logging.basicConfig(filename="./log",filemode='a')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='log', filemode='a')
MAX_NAME_LENGTH = 50
class Project(models.Model):
    user = models.CharField(max_length=MAX_NAME_LENGTH)
    # project name
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    ip = models.CharField(max_length=MAX_NAME_LENGTH, default="")

    @classmethod
    def create(cls, user, name):
        try:
            project = Project.objects.get(user=user, name=name)
        except Project.DoesNotExist:
            project = Project(user=user, name=name)
            # save to db
            project.save()
            
            tempip = util._generate_ip()
            project.ip = tempip
            project.save()
            logger.info("save database item: {} {} {}".format(project.pk, project.user, project.name))

            # create project ns
            project.create_ns()

        return project

    @classmethod
    def getby(cls, user, name):
        try:
            project = Project.objects.get(user=user, name=name)
        except Project.DoesNotExist:
            logger.debug("delete unexisted project")
            return None

        return project
    
    def removeproj(self):
        for subnet in self.subnet_set.all():
            for vm in subnet.vm_set.all():
                vm.delete()
            subnet.delete()
            
        self.delete_ns()
        self.delete()
        logger.info("remove database item: {} {} {}".format(self.pk, self.user, self.name))

    def info(self):
        res = {
                "id": self.pk,
                "user": self.user,
                "name": self.name,
                "subnet": [],
                "ip": self.ip
        }
        for subnet in self.subnet_set.all():
            res["subnet"].append(subnet.info())
        return res

    def __str__(self):
        return "id: " + str(self.pk) + ", user: " + self.user + ", name: " + self.name 

    # helper function
    def create_ns(self):
        ns_name = self.get_ns_name()
        util._create_ns(ns_name, self.ip)
        logger.info("create namespace: {}, ip: {}".format(ns_name, self.ip))

    def delete_ns(self):
        ns_name = self.get_ns_name()
        util._remove_ns(ns_name, self.ip)
        logger.info("delete namespace: {}, ip:{}".format(ns_name, self.ip))

    def get_ns_name(self):
        return util._get_ns_name(self.user, self.name, self.pk)

    @classmethod
    def listall(cls): 
        res =[item.info() for item in Project.objects.all()]
        # logger.info(res)
        return res

    def get_id(self):
        return self.pk
