class Subnet:
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