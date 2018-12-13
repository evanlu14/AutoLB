from django.test import TestCase
from .models.project import Project
import os

class ProjectTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # user = "utestusr"
        # name = "utestproj"
        # project = Project.create(user, name)
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
    
    # def testgetall(self):
    #     res = Project.listall()
    #     print(res)

    # def testremove(self):
    #     tproj = Project.create("utestrm", "utestrm")
    #     tproj.remove()
    #     tproj2 = Project.get("utestrm", "utestrm")
    #     self.assertIsNone(tproj2)
    
    # def testinfo(self):
    #     project = Project.get("utestusr", "utestproj")
    #     res = project.info()
    #     print(res)

    def tearDown(self):
        pass

    @classmethod 
    def tearDownClass(cls):
        # project = Project.get("utestusr", "utestproj")
        # project.remove()
        pass