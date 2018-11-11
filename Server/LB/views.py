from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
@csrf_exempt
def projCreate(request):
    input = json.loads(request.body)

    
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
def projInfo(request):
    input = json.loads(request.body)

    
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
def projUpdate(request):
    input = json.loads(request.body)

    
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
def projDelete(request):
    input = json.loads(request.body)

    
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
def insCreate(request):
    input = json.loads(request.body)

    
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
def insInfo(request):
    input = json.loads(request.body)

    
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
def insUpdate(request):
    input = json.loads(request.body)

    
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
def insDelete(request):
    input = json.loads(request.body)

    
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

