from mininet.topo import Topo
from linux_router import LinuxRouter

class NetworkTopo(Topo):
    def build(self, N, **_opts):
        #создание маршрутизаторы
        r0 = self.addHost('r0', cls=LinuxRouter, ip='10.0.0.1/24')
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.1.1/24')
        #добавление коммутаторов для связи хостов 
        s0 = self.addSwitch('s1')
        s1 = self.addSwitch('s2')
        #соединение между маршрутизаторами и коммутаторами
        self.addLink(s0, r0, intfName2='r0-eth1', params2={'ip': '10.0.0.1/24'})
        self.addLink(s1, r1, intfName2='r1-eth1', params2={'ip': '10.0.1.1/24'})
        #соединение между маршрутизаторами
        self.addLink(r0, r1, 
        		intfName1='r0-eth2', 
        		intfName2='r1-eth2', 
        		params1={'ip': '10.0.2.1/24'}, 
        		params2={'ip': '10.0.2.2/24'}
        		)
        #добавление оконечных устройств
        for i in range(0, N):
            s = self.addHost(f'hs{i+1}', ip=f'10.0.0.{i+2}/24', defaultRoute='via 10.0.0.1')
            r = self.addHost(f'hr{i+1}', ip=f'10.0.1.{i+2}/24', defaultRoute='via 10.0.1.1')
            self.addLink(s, s0)
            self.addLink(r, s1)
