import sys
import os
import json
import requests

fileAddress = os.path.abspath(sys.argv[1])
with open(fileAddress) as f:
    data = json.load(f)

server = "http://localhost:8000"
url = server + "/LB/" + data["type"] + "/"
headers = {
    'Content-type': 'application/json', 
    'Accept': 'text/plain'
}
body = data

res = requests.post(url, data=json.dumps(body), headers=headers)

# responseData = json.loads(res.content)
# print("Request type: " + responseData["type"])
# print("Request action: " + responseData["action"])
# print("Request Status: " + responseData["status"])
# print("Response:")
# print(responseData["info"])
print(res.content)
