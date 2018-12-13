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