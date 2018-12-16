from django.test import TestCase
from .models.project import Project
from .models.subnet import Subnet
from .models import util
import os

class ProjectTests(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def check_ping(self, ns_name):
        hostname = "8.8.8.8"
        response = os.system("ip netns exec " + ns_name + " ping -c 1 " + hostname)
        if response == 0:
            # successful
            pingstatus = 1
        else:
            # fail
            pingstatus = 0

        return pingstatus

    def testall(self):
        project = Project.create("utestusr", "utestproj")
        val = Project.getby("utestusr", "utestproj")
        self.assertIsNotNone(val)

        res = project.info()
        print(res)

        ns_name = project.get_ns_name()
        self.assertEquals(self.check_ping(ns_name), 1)

        val.removeproj()
        val2 =Project.getby("utestusr", "utestproj")
        self.assertIsNone(val2)
    
    def testgetall(self):
        res = Project.listall()
        print(res)

    def tearDown(self):
        pass

    @classmethod 
    def tearDownClass(cls):
        # project = Project.get("utestusr", "utestproj")
        # project.remove()
        pass

class SubnetTests(TestCase):
    def testall(self):
        subnet = Subnet.create("102.10.1.0/24", "utestusr", "utestproj")
        val = Subnet.getby("102.10.1.0/24", "utestusr", "utestproj")
        self.assertIsNotNone(val)

        res = val.info()
        print(res)

        val.removebr()
        val2 = Subnet.getby("102.10.1.0/24", "utestusr", "utestproj")
        self.assertIsNone(val2)

class UtilsTests(TestCase):
    def test_generate_ip(self):
        print(util._generate_ip())
        print(util._generate_ip())
        print(util._generate_ip())

    def test_generate_gateway_ip(self):
        subnet_ip1 = "102.100.1.0/24"
        self.assertEquals(util._generate_gateway_ip(subnet_ip1), "102.100.1.1")
        
        subnet_ip1 = "102.100.1.0/16"
        self.assertEquals(util._generate_gateway_ip(subnet_ip1), "102.100.0.1")
    
    def test_get_docker_network_id(self):
        br_name = "testbr1"
        id = util._get_docker_network_id(br_name)
        self.assertAlmostEquals(id, 'e4320b435139669bbd681508a8f43e77d9e521b6a958dd8f43336efd09713e52')

        br_name = "testbr101"
        id2 = util._get_docker_network_id(br_name)
        self.assertIsNone(id2)