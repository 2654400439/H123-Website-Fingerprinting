from transitions import Machine
from scapy.all import *
from itertools import groupby


class H3FSM:
    resource_produce = 0
    resource_timestamp = []

    def produce(self):
        self.resource_produce += 1

    def show_result(self):
        return max(self.resource_produce, 0)


def check_with_h3fsm(packets):
    h3fsm = H3FSM()

    # 定义状态
    states = ['idle', 'quic_hs', 'set', 'send_settings', 'send_header', 'end']

    # 定义状态转换
    transitions = [
        {'trigger': 'quic_hs', 'source': 'idle', 'dest': 'quic_hs'},
        {'trigger': 'send_s', 'source': 'quic_hs', 'dest': 'send_settings'},
        {'trigger': 's-set', 'source': 'send_settings', 'dest': 'set'},
        {'trigger': 'send_header', 'source': 'set', 'dest': 'send_header', 'after': 'produce'},
        {'trigger': 'header-set', 'source': 'send_header', 'dest': 'set'},
        {'trigger': 'end', 'source': 'set', 'dest': 'end'},
    ]

    # 创建状态机实例
    my_fsm = Machine(model=h3fsm, states=states, transitions=transitions, initial='idle')

    burst = []

    for packet in packets:
        if IP in packet and UDP in packet:
            if Raw in packet:
                udp_payload = packet[Raw].load
                short_header = udp_payload[0] < 128

                if h3fsm.state == 'idle' and not short_header:
                    h3fsm.trigger('quic_hs')
                if h3fsm.state == 'quic_hs' and short_header:
                    h3fsm.trigger('send_s')
                    h3fsm.trigger('s-set')
                # 客户端发包
                if h3fsm.state == 'set' and short_header and packet[UDP].dport == 443:
                    # 排除小包控制包
                    if len(udp_payload) < 120:
                        burst.append(0)
                        continue
                    else:
                        h3fsm.trigger('send_header')
                        h3fsm.resource_timestamp.append(packet.time)
                        h3fsm.trigger('header-set')
                        burst.append(1)

    if h3fsm.state == 'tls_hs':
        return 0, []
    else:
        h3fsm.trigger('end')
        grouped = groupby(burst)
        lengths = [len(list(group)) for _, group in grouped if _ == 1]
        return max(h3fsm.resource_produce, 0), lengths


if __name__ == '__main__':
    packets = rdpcap("./FSM_unit_test/h3fsm_test1.pcapng")
    resource_num, burst = check_with_h3fsm(packets)
    print(resource_num, burst)
