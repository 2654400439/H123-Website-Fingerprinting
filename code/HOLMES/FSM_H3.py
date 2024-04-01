from transitions import Machine
from scapy.all import *


class H3FSM:
    resource_produce = 0
    def produce(self):
        self.resource_produce += 1
    def show_result(self):
        return max(self.resource_produce, 0)

def check_with_h3fsm(packets):
    h3fsm = H3FSM()

    states = ['idle', 'quic_hs', 'set', 'send_settings', 'send_header', 'end']

    transitions = [
        {'trigger': 'quic_hs', 'source': 'idle', 'dest': 'quic_hs'},
        {'trigger': 'send_s', 'source': 'quic_hs', 'dest': 'send_settings'},
        {'trigger': 's-set', 'source': 'send_settings', 'dest': 'set'},
        {'trigger': 'send_header', 'source': 'set', 'dest': 'send_header', 'after': 'produce'},
        {'trigger': 'header-set', 'source': 'send_header', 'dest': 'set'},
        {'trigger': 'end', 'source': 'set', 'dest': 'end'},
    ]

    my_fsm = Machine(model=h3fsm, states=states, transitions=transitions, initial='idle')

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
                if h3fsm.state == 'set' and short_header and packet[UDP].dport == 443:
                    if len(udp_payload) < 120:
                        continue
                    else:
                        h3fsm.trigger('send_header')
                        h3fsm.trigger('header-set')

    if h3fsm.state == 'tls_hs':
        return 0
    else:
        h3fsm.trigger('end')
        return max(h3fsm.resource_produce, 0)


if __name__ == '__main__':
    packets = rdpcap('./FSM_unit_test/h3fsm_test.pcapng')
    resource_num = check_with_h3fsm(packets)
    print(resource_num)
