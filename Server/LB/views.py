from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models.project import Project
from .models.subnet import Subnet
from .models.vm import VM
from .models.controller import Controller
import chardet

# Create your views here.
@csrf_exempt
def project(request):
    input = json.loads(request.body.decode(chardet.detect(request.body)["encoding"]))

    status = "successful"
    action = input["action"]
    type = input["type"]
    res = {
        "status": status,
        "action": action,
        "type": type,
        "info": {}
    }

    if(input["action"] == "create"):
        print("project create...")
        project = Project.create(input['user'], input['info']['name'])
        res["info"]["id"] = project.get_id()

    if(input["action"] == "info"):
        print("project info...")
    if(input["action"] == "update"):
        print("project update...")
    if(input["action"] == "delete"):
        print("project delete...")
        Project().delete(input['user'], input['info']['name'])

    if(input["action"] == "list"):
        res["info"] = Project.listall()
    
    return HttpResponse(json.dumps(res))

@csrf_exempt
def instance(request):
    input = json.loads(request.body.decode(chardet.detect(request.body)["encoding"]))

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

    if(input["action"] == "create"):
        print("instance create...")
        # user, proj_name, subnet_ip, traffic_type, backend, healthcheck
        instance = VM.create(input["user"], input["project"], input["info"]["subnet"], input["info"]["traffic_type"], input["info"]["backend"]["entities"], input["info"]["backend"]["health-check"])

    if(input["action"] == "info"):
        print("instance info...")
    if(input["action"] == "update"):
        print("instance update...")

    if(input["action"] == "delete"):
        print("instance delete...")
        VM().delete(input["info"]["name"])

    
    return HttpResponse(json.dumps(res))

