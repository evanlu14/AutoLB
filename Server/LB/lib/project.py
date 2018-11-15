class Project:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.subnet = Subnet()
        self.vms = []

    def init_subnet(self):
        """ create and initializa a network namespace
        """
        self.subnet.initialize()
    
    def add_vm(self, vm):
        """ attach a new VM in the current project
        """
        self.subnet.add_vm(vm)
        self.vms.append(vm)

    def remove_vm(self, vm):
        """ remove a VM from the current project
        """
        self.subnet.remove_vm(vm)
        self.vms.remove(vm)