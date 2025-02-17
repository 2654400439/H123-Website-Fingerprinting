from transitions import Machine
from scapy.all import *
from itertools import groupby


class H2FSM:
    resource_produce = -1
    resource_consume = -1
    resource_timestamp = []

    def produce(self):
        self.resource_produce += 1

    def consume(self):
        self.resource_consume += 1

    def show_result(self):
        return max(self.resource_produce, 0)


def check_with_h2fsm(packets):
    h2fsm = H2FSM()

    states = ['idle', 'tls_hs', 'send_magic', 'set', 'send_header', 'recv_s_uw', 'send_s', 'recv_header', 'end']

    transitions = [
        {'trigger': 'tls_hs', 'source': 'idle', 'dest': 'tls_hs'},
        {'trigger': 'send_magic', 'source': 'tls_hs', 'dest': 'send_magic'},
        {'trigger': 'set', 'source': 'send_magic', 'dest': 'set'},
        {'trigger': 'send_header', 'source': 'set', 'dest': 'send_header', 'after': 'produce'},
        {'trigger': 'send-set', 'source': 'send_header', 'dest': 'set'},
        {'trigger': 'recv_header', 'source': 'set', 'dest': 'recv_header', 'after': 'consume'},
        {'trigger': 'recv-set', 'source': 'recv_header', 'dest': 'set'},
        {'trigger': 'end', 'source': 'set', 'dest': 'end', 'prepare': 'show_result'},
    ]

    my_fsm = Machine(model=h2fsm, states=states, transitions=transitions, initial='idle')

    flag_new_session = 0
    max_len = 1300
    burst = []

    for packet in packets:
        if IP in packet and TCP in packet:
            if Raw in packet:
                tcp_payload = packet[Raw].load
                max_len = len(tcp_payload) if len(tcp_payload) > max_len else max_len
                if flag_new_session == 0:
                    if h2fsm.state != 'idle' and tcp_payload[0] == 23 and int.from_bytes(tcp_payload[3:5],
                                                                                         byteorder='big') < 150:
                        flag_new_session = 1
                if h2fsm.state == 'idle' and tcp_payload[0] == 22:
                    h2fsm.trigger('tls_hs')
                if h2fsm.state == 'tls_hs' and tcp_payload[0] == 23:
                    h2fsm.trigger('send_magic')
                    h2fsm.trigger('set')
                if h2fsm.state == 'set' and tcp_payload[0] == 23 and packet[TCP].dport == 443:
                    if int.from_bytes(tcp_payload[3:5], byteorder='big') <= 40:
                        continue
                    else:
                        burst.append(1)
                        h2fsm.trigger('send_header')
                        h2fsm.trigger('send-set')
                if h2fsm.state == 'set' and tcp_payload[0] == 23 and packet[TCP].sport == 443 and len(
                        tcp_payload) < max_len:
                    h2fsm.trigger('recv_header')
                    h2fsm.trigger('recv-set')
            else:
                if packet[TCP].dport == 443 and h2fsm.state == 'set':
                    burst.append(0)

    if h2fsm.state == 'tls_hs':
        return 0, []
    else:
        h2fsm.trigger('end')
        grouped = groupby(burst)
        lengths = [len(list(group)) for _, group in grouped if _ == 1]
        return max(h2fsm.resource_produce, 0), lengths


if __name__ == '__main__':
    packets = rdpcap("./FSM_unit_test/h2fsm_test3.pcapng")

    resource_num, burst = check_with_h2fsm(packets)
    print(resource_num, burst)
