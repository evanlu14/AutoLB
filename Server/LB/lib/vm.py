from django.db import models

MAX_NAME_LENGTH = 50
class VM(models.Model):
    traffic = models.CharField(max_length=MAX_NAME_LENGTH)
    backends = models.TextField(null=True) # JSON-serialized, like ['192.168.1.1', '192.168.1.2']
    healthcheck = models.BooleanField(default=False)

    def __init__(self):
        self.id = -1

    def create(self):
        """ create a new VM
        """

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