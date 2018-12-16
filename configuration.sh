# clone a vm
sudo virt-clone --original zlu24vm1 --name proj1vm1 --auto-clone
sudo virsh start proj1vm1
# zlu24vm1 is the template machine, it already atteched to zlu24net4, a NAT l3.
# in my test, proj1 attached to zlu24net3 automatically, and got a ip in about ten seconds.

# configure load balancing
# first ssh into the vm
# then configure iptables
sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 80 -m state --state NEW -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 35.237.181.53:80
sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 80 -m state --state NEW -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 35.237.181.53:80
sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 80 -m state --state NEW -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 35.237.181.53:80
sudo iptables -t nat -A POSTROUTING -p tcp -d 192.168 --dport 80 -j SNAT --to-source 192.168.x.x
sudo iptables -t nat -A POSTROUTING -p tcp -d 192.168 --dport 80 -j SNAT --to-source 192.168.x.x
sudo iptables -t nat -A POSTROUTING -p tcp -d 192.168 --dport 80 -j SNAT --to-source 192.168.x.x


# create project namespace (proj1ns -> adminns)

sudo ip netns add proj1ns
sudo ip netns list

# create a veth pair and attach to each namespace
sudo ip link add proj1int1 type veth peer name proj1int2
sudo ip link set proj1int1 netns proj1ns
sudo ip addr add 1.1.2.2/24 dev proj1int1
sudo ip link set dev proj1int1 up

sudo ip link set proj1int2 netns adminns
sudo ip addr add 1.1.2.1/24 dev proj1int2
sudo ip link set dev proj1int2 up

sudo ip netns exec proj1ns ip route add default via 1.1.2.1

# test
sudo ip netns exec tesns1 ping 8.8.8.8

# proj1vm1 -> proj1ns
# create a l2 network
echo "<network> 
    <name>proj1vm1net1</name> 
    <forward mode='bridge'/> 
    <bridge name='proj1vm1br1'/> 
</network>" >> l2.xml

sudo virsh net-define l2.xml
sudo virsh net-start proj1vm1net1
sudo brctl addbr proj1vm1br1

# attach it to vm
sudo virsh edit zlu24vm1
# add this interface:
# <interface type='network'>
#     <source network='proj1vm1net1'/>
#     <model type='virtio'/>
#     <address type='pci' domain='0x0000' bus='0x00' slot='0x09' function='0x0'/>
# </interface>
sudo virsh destroy proj1vm1 && sudo virsh start proj1vm1

sudo ip link add proj1int3 type veth peer name proj1int4
sudo ip link set proj1int3 netns proj1ns
sudo ip netns exec proj1ns ip addr add 1.1.3.1/24 dev proj1int3
sudo ip netns exec proj1ns ip link set dev proj1int3 up

sudo ip link set dev proj1int4 up
sudo brctl addif proj1vm1br1 proj1int4
sudo ip link set dev proj1vm1br1 up

sudo ip netns exec proj1ns iptables -t nat -A POSTROUTING -o proj1int1 -j MASQUERADE

# in proj1vm1 
sudo ip addr add 1.1.3.2/24 dev eth1
sudo ip link set dev eth1 up
sudo ip route del default
sudo ip route add default via 1.1.3.1 dev eth1
# test
ping 8.8.8.8


# docker
sudo docker network create --driver bridge --internal --subnet 172.28.100.0/24 --gateway 172.28.100.1 testbr1
# create image
sudo docker build -t myubuntu .
# create container
sudo docker run -itd --name testctn --network testbr1 myubuntu

# add adminns
  812  sudo ip netns add adminns
  814  sudo ip link add adminnsint1 type veth peer name adminnsint2
  815  sudo ip link set adminnsint2 netns adminns
  816  sudo ip link exec adminns ip link set dev adminnsint2 up
  817  sudo ip netns exec adminns ip link set dev adminnsint2 up
  818  sudo ip addr add 102.1.1.1/24 dev adminnsint1
  819  sudo ip link set dev adminnsint1 up
  820  sudo ip netns exec adminns ip addr 102.1.1.2/24 dev adminnsint2
  821  sudo ip netns exec adminns ip addr add 102.1.1.2/24 dev adminnsint2
  822  sudo ip netns exec adminns ip route add default via 102.1.1.1
  824  sudo iptables -t nat -A POSTROUTING  -s 102.1.1.0/24   -o enp0s3 -j MASQUERADE
  825  sudo ip netns exec adminns ping 8.8.8.8

# debug 
sudo python3 manage.py shell 
>>> from LB.models.project import Project                                                                                    
>>> Project.create("a", "sd")   

docker exec test1 bash -c 'ping 172.17.0.3'

sudo python3 manage.py test LB.tests.ProjectTests.testcreate

# connect docker bridge to namespace
  919  sudo docker network create --driver bridge --internal --subnet 172.28.100.0/24 --gateway 172.28.100.1 testbr1
  920  sudo docker network ls
  921  sudo brctl show
  922  sudo ip link add testbrint1 type veth peer name testbrint2
  923  sudo ip link set testbrint1 netns asd10
  924  sudo ip netns exec asd10 ip addr add 172.28.100.2 dev testbrint1
  925  sudo ip netns exec asd10 ip link set dev testbrint1 up
  926  sudo brctl addif br-e4320b435139 testbrint2
  927  sudo ip link set dev testbrint2 up
  928  sudo ip netns exec asd10 ip route
  929  sudo ip netns exec asd10 ping 172.28.199.1
  930  sudo ip netns exec asd10 ip a
  931  sudo ip netns exec asd10 iptables -t nat -A POSTROUTING -o asd10int1 -j MASQUERADE

# configure port and lb
sudo ip netns exec adminns iptables -t nat -A PREROUTING -p tcp -s 2.1.1.0/24 --dport 5001 -j DNAT --to-destination 1.1.3.2:5001
sudo ip netns exec proj0ns iptables -t nat -A PREROUTING -p tcp -s 2.1.1.0/24 --dport 5001 -j DNAT --to-destination 1.1.4.2:5001

sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 5001  -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 35.237.181.53:80
sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 5001  -m statistic --mode nth --every 3 --packet 1 -j DNAT --to-destination 35.196.112.92:80
sudo iptables -t nat -A PREROUTING -p tcp  -i eth0 --dport 5001  -m statistic --mode nth --every 3 --packet 2 -j DNAT --to-destination 35.227.124.229:80

sudo iptables -t nat -A PREROUTING -p tcp -i eth0 -j DNAT --to-destination 35.237.181.53:80

default via 202.132.25.1 dev eth0

docker network create --driver=bridge --ip-range=10.0.190.0/24 --subnet=10.0.0.0/16 --aux-address='ip1=10.0.190.1' --aux-address='ip2=10.0.190.2' --aux-address='ip3=10.0.190.3' -o "com.docker.network.bridge.name=br0" br0
docker network create --driver=bridge --ip-range=101.12.32.0/26 --subnet=101.12.32.0/24 -o "com.docker.network.bridge.name=tutbr0" tutbr0

sudo docker inspect --format '{{.State.Pid}}' dtedpr5
sudo ip link delete stbrint2  

# create a docker
sudo docker run -itd --name tctn --network none myubuntu
# create a namespace
sudo ip netns add tns
# create 
sudo virsh net-define l2.xml
sudo virsh net-start tnet0
sudo brctl addbr tbr0
# sudo ip link set tbr0 up

sudo ip link add tint1 type veth peer name tint2
sudo ip link set tint1 netns 31478
sudo brctl addif tbr0 tint2

sudo ip link add tint3 type veth peer name tint4
sudo ip link set tint3 netns tns
sudo brctl addif tbr0 tint4

sudo docker exec --privileged tctn ip addr add 202.5.2.2/24 dev tint1
sudo docker exec --privileged tctn ip link set tint1 up
sudo ip netns exec tns ip addr add 202.5.2.1/24 dev tint3
sudo ip netns exec tns ip link set tint3 up
sudo ip link set tint2 up
sudo ip link set tbr0 up
sudo ip link set tint4 up

sudo ip link add tint5 type veth peer name tint6
sudo ip link set tint5 netns tns
sudo ip link set tint6 netns adminns
sudo ip netns exec tns ip addr add 202.5.3.2/24 dev tint5
sudo ip netns exec adminns ip addr add 202.5.3.1/24 dev tint6
sudo ip netns exec tns ip link set dev tint5 up
sudo ip netns exec adminns ip link set dev tint6 up

sudo ip netns exec tns iptables -t nat -A POSTROUTING -s 202.5.2.0/24 -o tint5 -j MASQUERADE
sudo ip netns exec adminns iptables -t nat -A POSTROUTING -s 202.5.3.0/24 -o adminint2 -j MASQUERADE
sudo docker exec --privileged tctn ip route add default via 202.5.2.1 dev tint1
