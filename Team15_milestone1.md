# CSC792 Linux Networking milestone 1
Anran Zhou(azhou6@ncsu.edu) && Zecao Lu(zlu24@ncsu.edu)
## 1) project description
We choose the load balancing as a service as our project topic.

Load balancing is a technology that has been around for some time and is a foundation for delivering highly available resources over a network.

At a high level, load balancing is typically accomplished by having a load balancer or set of load balancers present a virtual server to a set of clients. This virtual server is backed by a pool of “real” servers that provide some type of resource to those clients. The role of the load balancer is to distribute client requests across the pool of servers including rerouting requests when a member of the pool fails. Clients are not aware which “real” server in the pool are servicing their requests since they are only aware of the virtual server presented by the load balancer. 

Load balancers were implemented by hardware devices in the past. With the advent of the cloud, we can see virtual load balancers are used to provide services to a pool of virtual servers. The function of virtual load balancers and physical load balancers are the same. But there are two major benefits of using virtual load balancers. The first is allowing users to provision load balancers on demand and in the case of metered clouds. The second is allowing users to pay for load balancing services on a utility basis.

In this project, we plan to make a Linux server act as load balancers to distribute loads on multiple Linux VMs in same or different server. Thse oad balancers are VM migrated and auto scaling. The rough idea is shown in the graph below:

![](https://lh6.googleusercontent.com/kVGfXSWQvBqzMDC54aZB_hVMJKAtIVXPq6qSJ1bjiw7yVGifsUKdE-W5kFjwxKHJ3PLT91azx_fS60SuHFf6O9Tzzw5V2W4TepsM-xeUmeTLiFIHIhGYX8CsB0BbflZI5Ar8Lxap)

Overall, what we need to do is to develop a linux box serving as the virtualized load balancer to provide services for other linux boxes. Just like the linux box1 in the graph above to provide services to Linux box 2 and Linux box 3.

## 2) related work
We investigated two popular products in the market. One is AWS Elastic Load Balancing. The other is Google Cloud Load Balancing.
### 2a) AWS Elastic Load Balancing
There are three types of Load balancers provided by AWS which are **Application Load Balancer**, **Network Load Balancer** and **Classic Load Balancer**. 

There are some common features among these three load balancer, like: **High Availability**, **Health checks**, **Performance Monitoring**, **Logging** and **Cross-zone load balancing**. The representative unique features of each Load balancer are summarized as follows:
| Load balancer | Unique Features |
|:--------:|:-------------:|
| Application | Layer-7 Load Balancing, Content-Based Routing, More Security Options|
| Network | High Throughput, Low Latency, Static and Elastic IP address |	
So the customers can select the appropriate load balancers based on their application needs. If they need flexible application management, they can use an Application Load Balancer. If extreme performance and static IP is needed for their application, they can use a Network Load Balancer. If they have an existing application that was built within the EC2-Classic network, they can use a Classic Load Balancer.

### 2b) Google Cloud Load Balancing
Google Cloud Load Balancing provides 5 different load balancers. We can divide those five load balancers by three aspects: Area(Global/Regional), Scope(External/Internal) and Traffic Type. The following table provides some specifics about each load balancer:
| Load balancer | Traffic type |Global/Regional |External/Internal |
|:--------:|:-------------:|:-------------:|:-------------:|
| HTTP(S) | HTTP or HTTPS |Global |External |right-aligned |
| SSL Proxy | TCP with SSL offload |Global |External |
| TCP Proxy | TCP without SSL offload. Does not preserve client IP addresses|Global |External |
| Network TCP/UDP | TCP/UDP without SSL offload. Preserves client IP addresses. |Regional |External |
| Internal TCP/UDP | TCP or UDP |Regional |Internal |
The features of google load balancers are summarized as below:
* Provide HTTP(S), TCP/SSL, UDP Load Balancing.
* Advanced Features. Such as IPv6 Global Load Balancing, WebSockets, user-defined request headers, and protocol forwarding for private VIPs.
* Stack driver Logging logs all the load balancing requests to debug and analyze user traffics.
* Autoscaling handles increases in traffic and reduces cost when the need for resources is lower.
* Health Checks ensure that new connections are only load balanced to healthy backends that are up and ready to receive them.
* Cloud CDN Integration improves the performance.

### 2c) Comparison
AWS load balancers and Google Cloud Load Balancer both provide the feature of high availability, automatic scaling, internal load balancing, global load balancing and robust security, etc. But there are still some differences listed in the table below.

| feature | AWS |Google |comments
|:--------:|:-------------:|:-------------:|:-------------:|
|load balancers types| 3 different LBs | 5 different LBs | Google provides LBs with more detailed classification.
|platform|AWS VPC | Google cloud| they both need their own platform to use load balancing feature.
|supported protocols|HTTP(s), TCP, SSL|HTTP(S), TCP/SSL, UDP and proxy| Google support more protocols when applying LB |
|CDN|no use| Google cloud CDN| Google combined CDN with LB to improve performance.


## 3) feature list implementation proposal
### 3a) functional feature
We plan to implement the application layer load balancer. The network communication must travel all the way back up to the application layer, and the application load balancer reads the HTTP request to determine where it should be directed.

When the number of client requests is very large, we need to autoscale load balancers to ensure that  the load balancer part will not be the bottleneck of the whole server. The relationship among load balancers are mainly two types. The first one is parallel. We can use more than one LB to deal with the incoming traffic to relief the load of a single LB. The second one is hierarchical. We can use a tree structure LBs to redirect the incoming traffic. In this way, we can relief each LB layers' load.

How to evaluate the traffic load in the network is also important. The evaluation standard is different between the network layer and the application layer. In the network layer, we can count the number of packets to evaluate the traffic. While in the application layer, we can statistic the number of requests(like GET requests) to infer the traffic condition of the network.

There are some methods to deal with the coming traffic:
1. Round Robin
Requests are distributed evenly across the servers, with server weights taken into consideration.

2. Least Connections
A request is sent to the server with the least number of active connections, again with server weights taken into consideration.

3. IP Hash
The server to which a request is sent is determined from the client IP address. In this case, either the first three octets of the IPv4 address or the whole IPv6 address are used to calculate the hash value. The method guarantees that requests from the same address get to the same server unless it is not available.

### 3b) management feature 
#### 1. Performance & Scalability
When the client requests are very large, we can use the autoscaler to improve the performance. Autoscaling can help applications handle increases in traffic and reduces cost when the need for resources is lower. We provide the autoscale feature on our load balancers. The autoscaler will collect information based on the policy, compare it to the desired target utilization value, and determine if it needs to perform scaling. Our policy ideas are from the [Google cloud autoscaling](https://cloud.google.com/compute/docs/autoscaler/).
-   Average CPU utilization
-   HTTP load balancing serving capacity, which can be based on either utilization or requests per second.

For example, if the user choose the scale based on CPU utilization, he can set his target utilization level at 75% and the autoscaler will maintain the CPU utilization of the specified group of instances at or close to 75%. The utilization level for each metric is interpreted differently based on the autoscaling policy.

#### 2.  Availability & Reliability
There are three features that we use to ensure the availability and reliability which are health monitor, log and connection limits.

We set a health monitor to monitor the current status of each load balancer. Borrowed the idea from NGINX, we adopted [passive health checks](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/#passive-health-checks). We monitor transactions as they happen and log them, and try to resume failed connections. If the transaction still cannot be resumed,  mark the server as unavailable and temporarily stop sending requests to it until it is marked active again.

The conditions under which an upstream server is marked unavailable are defined for each upstream server with parameters to the server directive in the upstream block:
* `fail_timeout`
Sets the time during which a number of failed attempts must happen for the server to be marked unavailable, and also the time for which the server is marked unavailable (default is 10 seconds).
* `max failtimes`
Sets the number of failed attempts that must occur during the fail_timeout period for the server to be marked unavailable (default is 1 attempt).Our Load Balancing automatically distributes traffic across multiple targets.

Beside that, we also set connection limits to ensure the reliability. This feature allows workload control and can also assist with mitigating DoS (Denial of Service) attacks.

#### 3. User Interface & Configurability
The user interface of our load balancer can be CLI and scripts. Users perform administrative management of load balancers through the CLI. The application layer services(for example, REST API) are available for scripting.

We use config file to set the configuration of Our load balancers. The syntax borrows from NGINX. The simplest example can be like the codes below. We just set two servers with weight and max_fails and fail_timeout.
```
backend {
    rr
    server backend1.example.com weight=2;
    server backend2.example.com max_fails=3 fail_timeout=30s;
}
```





