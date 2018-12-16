from django.db import models
import os
from .project import Project
from .subnet import Subnet
from . import util
from random import randint
import time
import subprocess
import threading
import docker

MAX_NAME_LENGTH = 50
class VM(models.Model):
    subnet = models.ForeignKey('Subnet', on_delete=models.CASCADE)
    backends = models.TextField(null=True) # JSON-serialized, like ['192.168.1.1', '192.168.1.2']
    healthcheck = models.BooleanField(default=False)
    port_num = models.IntegerField(null=True)
    health_interval = models.IntegerField(null=True)
    health_timeout = models.IntegerField(null=True)
    health_threshold = models.IntegerField(null=True)

    health_status = models.IntegerField(default=0)
    health_cpu_usage = models.FloatField(default=0)
    health_io_rx = models.IntegerField(default=0)
    health_io_tx = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, proj_name, subnet_ip, backends, healthcheck, health_interval, health_timeout, health_threshold):
        """ create a new VM
        """
        subnet = Subnet.create(ip=subnet_ip, user=user, proj_name=proj_name)

        ins = VM(subnet=subnet, backends=backends, healthcheck=healthcheck, 
            health_interval=health_interval, health_timeout=health_timeout, 
            health_threshold=health_threshold)
        port_num = ins.get_port_number()
        ins.port_num = port_num
        ins.save()

        ins.create_ins()
        ins.config_lb()

        ins.monitor()
        return ins

    def removeins(self):
        self.delete_vm()

    def info(self):
        res = {
                "id": self.pk,
                "backends": self.backends,
                "healthcheck": self.healthcheck,
                "port_num": self.port_num,
                "instance": {
                    "name": self.get_ins_name(),
                    "ip": self.get_ins_ip()
                }
        }
        if self.health_status >= self.health_threshold:
            res["status"] = "unhealthy"
        else:
            res["status"] = "healthy"
            res["cpu_usage"] = self.health_cpu_usage
            res["received_bytes"] = self.health_io_rx
            res["transceived_bytes"] = self.health_io_tx
        return res

    def create_ins(self):
        """ create a instance
        """
        ins_name = self.get_ins_name()
        util._create_ins(ins_name)

        br_name = self.subnet.get_br_name()
        ins_ip = self.get_ins_ip()
        util._attach_to_br(ins_name, br_name, ins_ip, self.subnet.ip)

    def config_lb(self):
        """ config lb on vm
        """
        ns_int_ip = self.subnet.project.ip[:-3]
        ns_int_ip = ns_int_ip[:-1] + "2"
        ns_name = self.subnet.project.get_ns_name()
        ins_name = self.get_ins_name()
        ins_ip = self.get_ins_ip()
        util._config_lb_pre(self.port_num, ns_int_ip, ns_name, ins_name, ins_ip)

        backend_list = self.get_backends_list()
        print(self.backends, backend_list)
        for i in range(len(backend_list)):
            tot_num = len(backend_list)
            bip = backend_list[i]
            util._config_lb(ins_name, self.port_num, tot_num, i, bip, "80")

    def delete_vm(self):
        """ delete the vm
        """
        ins_name = self.get_ins_name()
        util._delete_ins(ins_name)
        self.delete()

    def check(self):
        client = docker.from_env()
        container = client.containers.get(self.get_ins_name())
        x = container.stats(stream=False)
        # with open('ctn.json', 'w') as f:
        #     f.write(json.dumps(x,indent=2))
        if x['precpu_stats']['cpu_usage']['total_usage'] == 0:
            self.health_status = self.health_status + 1
        else:
            self.health_status = 0
            self.health_cpu_usage = util.calculate_cpu_percent(x)
            self.health_io_rx, self.health_io_tx = util.calculate_network_bytes(x)
        self.save()
            # print({
            #     "cpu": "%.6f" % util.calculate_cpu_percent(x),
            #     "network": util.calculate_network_bytes(x)
            # })

    def monitor(self):
        event = threading.Event()
        k = util.ThreadJob(self.check, event, self.health_interval)
        k.start()

    # helper method

    def get_ins_name(self):
        project = self.subnet.get_project()
        return util._get_ins_name(project.user, project.name, self.pk)

    def get_port_number(self):
        is_occupied = True
        port_num = randint(10000, 20000)
        while VM.objects.filter(port_num=port_num).exists():
            port_num = randint(10000, 20000)
        return port_num

    def get_ins_ip(self):
        return util._generate_ins_ip(self.subnet.ip, self.pk)

    def get_backends_list(self):
        #back = self.backends[1:-1].split(",")
        #res = []
        #for x in back:
        #    while x.startswith(("'", '"', ' ')):
        #        x = x[1:]
        #    while x.endswith(("'", '"')):
        #        x = x[:-1]
        #    res.append(x)
        #return res
        return self.backends
