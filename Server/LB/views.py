from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .lib.project import Project
from .lib.subnet import Subnet
from .lib.vm import VM
from .lib.controller import Controller


# Create your views here.
@csrf_exempt
def project(request):
    input = json.loads(request.body)
    if(input["action"] == "create"):
        print("project create...")
    if(input["action"] == "info"):
        print("project info...")
    if(input["action"] == "update"):
        print("project update...")
    if(input["action"] == "delete"):
        print("project delete...")
    
    status = "successful"


    action = input["action"]
    type = input["type"]
    res = {
        "status": status,
        "action": action,
        "type": type,
        "info": {
            "id": 1,
        }
    }
    return HttpResponse(json.dumps(res))

@csrf_exempt
def instance(request):
    input = json.loads(request.body)

    if(input["action"] == "create"):
        print("instance create...")
    if(input["action"] == "info"):
        print("instance info...")
    if(input["action"] == "update"):
        print("instance update...")
    if(input["action"] == "delete"):
        print("instance delete...")

    status = "successful"
    

    action = input["action"]
    type = input["type"]
    res = {
        "status": status,
        "action": action,
        "type": type,
        "info": {
            "id": 1,
        }
    }
    return HttpResponse(json.dumps(res))

