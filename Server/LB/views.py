from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models.project import Project
from .models.subnet import Subnet
from .models.vm import VM
from .models.controller import Controller


# Create your views here.
@csrf_exempt
def project(request):
    input = json.loads(request.body)
    if(input["action"] == "create"):
        print("project create...")
        project = Project.create(input['user'], input['info']['name'])
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
        instance = VM.create()
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

