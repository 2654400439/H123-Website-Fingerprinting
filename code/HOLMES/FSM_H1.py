from transitions import Machine
from scapy.all import *


class H1FSM:
    resource_num = 0
    def count_rs_num(self):
        self.resource_num += 1
    def show_rs_num(self):
        return self.resource_num

def check_with_h1fsm(packets):
    h1fsm = H1FSM()

    # define states
    states = ['idle', 'tls_hs', 'set', 'request', 'receive', 're_request', 'end']

    # define transitions
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

    for packet in packets:
        if IP in packet and TCP in packet:
            if packet[TCP].sport == 80 or packet[TCP].dport == 80:
                return int(1)
            if Raw in packet:
                tcp_payload = packet[Raw].load
                if h1fsm.state == 'idle' and tcp_payload[0] == 22:
                    h1fsm.trigger('tls_hs')

                if h1fsm.state == 'set' and tcp_payload[0] == 23 and packet[TCP].sport == 443:
                    h1fsm.trigger('start_rc')
                    h1fsm.trigger('recv-set')
                if h1fsm.state == 'set' and tcp_payload[0] == 23 and packet[TCP].dport == 443:
                    h1fsm.trigger('request')
                    h1fsm.trigger('rq-set')

                if h1fsm.state == 'tls_hs' and tcp_payload[0] == 23 and packet[TCP].dport == 443:
                    h1fsm.trigger('start_rq')
                    h1fsm.trigger('rq-set')

    if h1fsm.state == 'tls_hs':
        return 0
    else:
        h1fsm.trigger('end')
        return h1fsm.resource_num


if __name__ == '__main__':
    packets = rdpcap('./FSM_unit_test/h1fsm_test1.pcapng')
    resource_num = check_with_h1fsm(packets)
    print(resource_num)

