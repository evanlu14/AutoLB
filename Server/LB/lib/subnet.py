from django.db import models

MAX_NAME_LENGTH = 50
class Subnet(models.Model):
    ip = models.CharField(max_length=MAX_NAME_LENGTH)
    vms = models.ForeignKey('VM', on_delete = models.CASCADE)

    def __init__(self):
        self.name = ""
        self.id = -1

    def initializa(self):
        """ create a new network namespace
        """

    def add_vm(self, vm):
        """ create a new L2 bridge and attach to the namespace
        """

    def remove_vm(self, vm):
        """ detach and destroy corresponding bridge
        """