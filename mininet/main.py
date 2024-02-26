from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from threading import Thread

import time

from network_topo import NetworkTopo
from funcs import *

def run(_N=20):
    topo = NetworkTopo(N=_N)
    net = Mininet(topo=topo)

    info(net['r0'].cmd("ip route add 10.0.1.0/24 via 10.0.2.2 dev r0-eth2"))
    info(net['r1'].cmd("ip route add 10.0.0.0/24 via 10.0.2.1 dev r1-eth2"))
    info(net['c0'].cmd("sudo sysctl -w net.ipv4.tcp_congestion_control=reno"))
    info(net['c0'].cmd("sudo sysctl -w net.ipv4.tcp_rmem='2000 8000 16000'"))
    info(net['c0'].cmd("sudo sysctl -w net.ipv4.tcp_wmem='2000 8000 16000'"))

    #настройка алгоритма RED
    avpkt = 1000 
    limit = avpkt * 300
    min_ = avpkt * 75
    max_ = avpkt * 150
    probability = 0.1
    bandwidth = 20
    #burst = 125

    net['r0'].cmdPrint(f"tc qdisc add dev r0-eth2 root handle 1: red limit {limit} min {min_} max {max_} avpkt {avpkt} bandwidth {bandwidth} probability {probability}")

    net.start()
    # CLI(net)
    threads = []
            
    for i in range(0,_N):
        host1 = f'hs{i+1}'
        host2 = f'hr{i+1}'
        t = Thread(target=run_iperf, args=(net, host1, host2))
        t.start()
        threads.append(t)
  
    for t in threads:
        t.join()
    
       
    print(net['r0'].cmd("tc -s qdisc show dev r0-eth2"))
    net.stop()


#запуск программы
if __name__ == '__main__':
    setLogLevel('info')
    run(10)

