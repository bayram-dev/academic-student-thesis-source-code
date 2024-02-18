from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.link import TCLink  
from mininet.cli import CLI
import time

N = 10

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    def build(self, **_opts):
        global N
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='10.0.1.1/24')

        sender_list = []
        reciver_list = []
        # Adding hosts specifying the default route
        for i in range(0, N):
            ss1 = self.addHost( name=f'h_s{i+1}', ip=f'10.0.0.{i+2}/24', defaultRoute='via 10.0.0.1')
            sender_list.append(ss1)
            rr1 = self.addHost( name=f'h_r{i+1}', ip=f'10.0.1.{i+2}/24', defaultRoute='via 10.0.1.1')
            reciver_list.append(rr1)
            # Add host-router links
            self.addLink(ss1, r1, intfName2=f'h_s{i+1}-eth1', params2={'ip': '10.0.0.1/24'})
            self.addLink(rr1, r2, intfName2=f'h_r{i+1}-eth1', params2={'ip': '10.0.1.1/24'})

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2',
                     params1={'ip': '10.0.10.1/24'}, params2={'ip': '10.0.10.2/24'})

def run():
    global N
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Add routing for reaching networks that aren't directly connected
    info(net['r1'].cmd("ip route add 10.0.1.0/24 via 10.0.10.2 dev r1-eth2"))
    # Add routing for reaching networks that aren't directly connected
    info(net['r2'].cmd("ip route add 10.0.0.0/24 via 10.0.10.1 dev r2-eth2"))

    # Add red queue on r1-eth2 and r2-eth2
    net['r1'].cmd("tc qdisc add dev r1-eth2 root handle 1: prio")
    net['r1'].cmd("tc qdisc add dev r1-eth2 parent 1:1 handle 10: red limit 30000 min 2500 max 7500 avpkt 500 probability 0.1")

    net.start()

    net.waitConnected()
    
    CLI(net)

    for i in range(0, N):
        h2 = net.get(f'h_r{i+1}')
        h2.sendCmd("iperf3 -s -D -1")
        print("Started iperf 3 server", h2.name)
        h1 = net.get(f'h_s{i+1}')
        h1.sendCmd('iperf3 -c ', h2.IP(),f' -t 30 -J > tmp/iperf-{i+1}.json')
        print("Started iperf 3 client", h1.name)

    #for i in range(0, N):
        #h2 = net.get(f'h_r{i+1}')
        #h1 = net.get(f'h_s{i+1}')
        #h1.waitReadable()
        #h2.waitReadable()
        #print(f"Hosts {i+1} ended tests") 
    time.sleep(300)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
