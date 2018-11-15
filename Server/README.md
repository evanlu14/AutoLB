# LBaaS(Server)
## 1. Introduction
This is the server part of our Load Balancers.

This server can receive users' inputs and do corresponding automation tasks. Use the command to start the server: `python3 manage.py runserver`

## 2. Routing

|API|function|
|:---:|:---:|
|/project/create|create new projects|
|/project/info|retrieve projects' info|
|/project/update| update projects|
|/project/delete| delete projects|
|/instance/create| create instances|
|/instance/info| retrieve projects' info|
|/instance/update| update instances|
|/instance/delete| delete instances|

## 3. User Interface
Users can configure their requests in the json files and use the python script to send those json files to the server.
