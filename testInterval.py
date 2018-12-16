import threading
import docker
import json
ctn_name = "dtedpr5"

def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

def calculate_network_bytes(d):
    """
    :param d:
    :return: (received_bytes, transceived_bytes)
    """
    networks = graceful_chain_get(d, "networks")
    if not networks:
        return 0, 0
    r = 0
    t = 0
    for if_name, data in networks.items():
        r += data["rx_bytes"]
        t += data["tx_bytes"]
    return r, t

def graceful_chain_get(d, *args, default=None):
    t = d
    for a in args:
        try:
            t = t[a]
        except (KeyError, ValueError, TypeError, AttributeError):
            print("can't get %r from %s", a, t)
            return default
    return t

def check():
    client = docker.from_env()
    container = client.containers.get(ctn_name)
    x = container.stats(stream=False)
    # with open('ctn.json', 'w') as f:
    #     f.write(json.dumps(x,indent=2))
    if x['precpu_stats']['cpu_usage']['total_usage'] == 0:
        print(-1)
    else:
        print({
            "cpu": "%.6f" % calculate_cpu_percent(x),
            "network": calculate_network_bytes(x)
        })

class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()


if __name__ == "__main__":
    interval = 2
    timeout = 2
    threshold = 2

    event = threading.Event()
    k = ThreadJob(check,event,2)
    k.start()
    
