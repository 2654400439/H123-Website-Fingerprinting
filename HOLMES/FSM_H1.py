from transitions import Machine
from scapy.all import *


class H1FSM:
    resource_num = 0
    resource_timestamp = []

    def count_rs_num(self):
        self.resource_num += 1

    def show_rs_num(self):
        return self.resource_num


def check_with_h1fsm(packets):
    h1fsm = H1FSM()

    # 定义状态
    states = ['idle', 'tls_hs', 'set', 'request', 'receive', 're_request', 'end']

    # 定义状态转换
    transitions = [
        {'trigger': 'tls_hs', 'source': 'idle', 'dest': 'tls_hs'},
        {'trigger': 'start_rq', 'source': 'tls_hs', 'dest': 'request', 'prepare': 'count_rs_num'},
        {'trigger': 'start_rc', 'source': 'set', 'dest': 'receive'},
        {'trigger': 're_rq', 'source': 'receive', 'dest': 'request'},
        {'trigger': 'end', 'source': 'set', 'dest': 'end', 'prepare': 'show_rs_num'},
        {'trigger': 'rq-set', 'source': 'request', 'dest': 'set'},
        {'trigger': 'recv-set', 'source': 'receive', 'dest': 'set'},
        {'trigger': 'request', 'source': 'set', 'dest': 'request', 'prepare': 'count_rs_num'},
    ]

    my_fsm = Machine(model=h1fsm, states=states, transitions=transitions, initial='idle')

    def is_retransmission(packet, seen_seq_numbers):
        tcp = packet.getlayer(TCP)
        if tcp and tcp.seq in seen_seq_numbers:
            return True
        seen_seq_numbers.add(tcp.seq)
        return False

    seen_seq_numbers = set()
    filtered_packets = [pkt for pkt in packets if pkt.haslayer(TCP) and pkt[TCP].payload]
    filtered_packets = [pkt for pkt in filtered_packets if not is_retransmission(pkt, seen_seq_numbers)]

    if len(filtered_packets) == 0:
        return 0, []

    for packet in filtered_packets:
        if IP in packet and TCP in packet:
            if packet[TCP].sport == 80 or packet[TCP].dport == 80:
                return int(1), []
            if Raw in packet:
                tcp_payload = packet[Raw].load
                if len(tcp_payload) == 1:
                    continue

                if h1fsm.state == 'idle' and tcp_payload[0] == 22 and tcp_payload[1] == 3:
                    h1fsm.trigger('tls_hs')
                if h1fsm.state == 'set' and tcp_payload[0] == 23 and tcp_payload[1] == 3 and packet[TCP].sport == 443:
                    h1fsm.trigger('start_rc')
                    h1fsm.trigger('recv-set')
                if h1fsm.state == 'set' and tcp_payload[0] == 23 and tcp_payload[1] == 3 and packet[TCP].dport == 443:
                    h1fsm.trigger('request')
                    h1fsm.resource_timestamp.append(packet.time)
                    h1fsm.trigger('rq-set')

                if h1fsm.state == 'tls_hs' and tcp_payload[0] == 23 and tcp_payload[1] == 3 and packet[TCP].dport == 443:
                    h1fsm.trigger('start_rq')
                    h1fsm.resource_timestamp.append(packet.time)
                    h1fsm.trigger('rq-set')

    if h1fsm.state == 'tls_hs':
        return 0, []
    else:
        h1fsm.trigger('end')
        return h1fsm.resource_num, h1fsm.resource_timestamp


if __name__ == '__main__':
    packets = rdpcap('./FSM_unit_test/h1fsm_test2.pcapng')

    resource_num, resource_timestamp = check_with_h1fsm(packets)
    print(resource_num, resource_timestamp)

