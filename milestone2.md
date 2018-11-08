## Claim

- Project report

- code/scripts with readme

## Features

- HTTP/TCP
- Health check
- Autoscaling
- (optional) Monitoring and logging

## Logical flow

What happens when user create a new LB:

1. Controller create a VM ( get IP)
2. Configure LB function on that VM
3. Health checker machine register new VM
4. Register VM ip on DNS ( get URL)
5. Create a new namespace(subnet) if new project’
6. Return URL

How to monitor load?

1. Health checkers’ job ( using collectd framework)
2. Design data structure to store the monitor log

What happens when load increasing/decreasing ? (if auto-scaling)

increasing:

1. Health checker found it. 
2. Controller assigned a new VM
3. Repeat as above

What if one LB crash?

1. Health checker found it

2. Create a new one

3. Renew DNS

4. If old one keeps down

5. 1. For a period time? Delete it

6. If old one get healthy again

7. 1. Delete new one.

What if health checker down? Too evil to consider it.

## Architecture

VM

```c
enum Status {Running = 0, Suspend = 1, Shutdown = 2}; 
struct vm_info {
    char *name,
    int ram_size,
    int num_vcpu,
    Status status,
}
/**
    create a VM
    @param id assgined id of this vm.
    @param info the information of vm.
    @return 1 create successful
    		0 create fail.
*/
int CreateVM(int *id, struct vm_info *info);

/**
	get the information of the VM	
	@param id id of this VM
	@return the corresponding VM
*/
struct vm_info *GetVM(const int id);

/**
	delete the VM	
	@param id id of the VM
	@return 1 delete successful
			0 delete fail
*/
int DeleteVM(const int id);
```

- guest lb vm

```python
class LoadBalancer:
	id = -1
    servers = []
    healthcheck = False
    protocal = ""
	def __init__(self, ):
```

- bridge
- DNS server
- health checker vm

## UI

users send GET request containing the json file to our server, and return corresponding result.

Create a project:

```
{
    "action": "create"/"info"/"update"/"delete",
    "type": "project"/"subnet"/"instance",
    "info": {
        "name": example
    }
}
```

return value:

```json
{
    "status": "successful"/"fail",
    "action": "create",
    "type": "project",
    "info": {
        "name": example,
        "id": 1,
    }
}
```

### Configuration JSON File

#### project

```json
{
    "id": 1,
    "name": example,
    "instances": [],
}
```

#### Instance

```json
{
    "type": ["tcp"/"http"],
    "backend": {
        "entitys": [
            [ip/entity name], ...
        ],
        "health-check": {},
        "auto-scaling": true,
    }
}
```

##### health check

check the status of backend servers:

```json
"backends": {
    "entitys": [],
    "health-check": {
        "protocol": ("HTTP"/"TCP"),
        "port": 80,
        "request-path": "/",
        "criteria": {
            "interval": 5,
            "timeout": 5,
            "health-threshold": 2,
            "unhealth-threshold": 2
        }
    }
}
```