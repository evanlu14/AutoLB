
# CSC792 Linux Networking

A load balance as a service scheme.

## Getting Started

### Prerequisites

python3, django, ansible, libvirt, docker.

```
# libvirt
sudo apt install qemu-kvm libvirt-bin virt-manager virt-viewer virtinst
sudo apt install libvirt-python libvirt-dev
pip3 install libvirt-python

# ansible
sudo apt-get install ansible libssl-dev
pip3 install ansible

# django
sudo pip3 install Django
```

### Installing

1. create a admin namespace using `ip`:

```bash
sudo ip netns add admin_ns
```

2. To use the virtual machine, first create a virtual machine as a template.

    1. download a centos 7 image
    2. create a new vm named using `virt-install`.
    3. name it as `zlu24vm1`, add user `zecao` and password `123`. 

3. Run the server

    1. enter the Server directory
    2. `python3 manage.py makemigrations`
    3. `python3 manage.py migrate`
    4. `python3 manage.py runserver port-number`

4. Run the client

    1. enter the Client directory
    2. change the port-number in the `client.py` to the server port-number
    3. change the coreesponding template file.
    3. run it: `python3 client.py template/insCreate.json`

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Anran Zhou** - [AnranZhou](https://github.com/AnranZhou)
* **Zecao Lu**

## License

This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE.md) file for details

## Acknowledgments

* This project is a course project of NCSU CSC792
* We would like to express our very great appreciation to Professor Anand.
