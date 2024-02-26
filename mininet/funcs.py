from threading import Thread

# Функция для мониторинга очереди
def monitor_queue(net, interface, interval=1, output_file='queue_monitor.log'):
    with open(output_file, 'w') as file:
        try:
            while True:
                result = net['r0'].cmd(f'tc -s qdisc show dev {interface}')
                print(result, file=file)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Мониторинг завершен")
 
             
#Функция для запуска iperf между парой хостов
def run_iperf(net, host1_name, host2_name):
    h1 = net.get(host1_name)
    h2 = net.get(host2_name)
    # Запуск iperf сервера на втором хосте
    h2.cmdPrint("iperf3 -s -D")
    # Запуск iperf клиента на первом хосте, соединяющегося со вторым хостом
    h1.cmd(f"mkdir -p output/{host1_name}_to_{host2_name}")
    h1.cmdPrint(f'iperf3 -c {h2.IP()} -t 30 -J > output/{host1_name}_to_{host2_name}/{host1_name}_to_{host2_name}_iperf3.json')
    h1.cmd(f"cd output/{host1_name}_to_{host2_name} && plot_iperf.sh {host1_name}_to_{host2_name}_iperf3.json")


def monitor_queue(net, interface="r0-eth2", interval=1, output_file='queue_monitor.log'):
    t = threading.currentThread()
    with open(output_file, 'w') as file:
        while getattr(t, "do_run", True):
            result = net['r0'].cmd(f'tc -s qdisc show dev {interface}')
            print(result, file=file)
            time.sleep(interval)
