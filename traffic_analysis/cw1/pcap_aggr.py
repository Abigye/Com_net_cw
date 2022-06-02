from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from ipaddress import ip_address, ip_network
import sys
import matplotlib.pyplot as plt

class Node(object):
    def __init__(self, ip, plen):
        self.bytes = plen
        self.left = None
        self.right = None
        self.ip = ip
    def add(self, ip, plen):
        #
        # write your code here
        #
        if Node(self.ip,self.bytes):
            if int(ip) < int(self.ip):
                if self.left is None:
                    self.left = Node(ip,plen)
                else:
                    self.left.add(ip,plen)
            elif int(ip) >int(self.ip):
                if self.right is None:
                    self.right = Node(ip,plen)
                else:
                    self.right.add(ip,plen)
        else:
            node = Node(self.ip,self.bytes)
            node = Node(ip,plen)
                
    def data(self, data):
        if self.left:
            self.left.data(data)
        if self.bytes > 0:
            data[ip_network(self.ip)] = self.bytes
        if self.right:
            self.right.data(data)

    @staticmethod 
    def supernet(ip1, ip2):
        # arguments are either IPv4Address or IPv4Network
        na1 = ip_network(ip1).network_address
        na2 = ip_network(ip2).network_address
        #
        # write your code here
        #

        na1_bin = ''.join(['{0:08b}'.format(int(i)) for i in str(na1).split('.')])
        na2_bin = ''.join(['{0:08b}'.format(int(i)) for i in str(na2).split('.')])

        s = ''
        num = 0
        for i in range(0, len(na1_bin)):
            if na1_bin[i] == na2_bin[i]:
                s += na1_bin[i]
            else:
                num = i
                break

        if len(s) != len(na1_bin):
            d = len(na1_bin) - len(s)
            s += '0'*d

        supernet_ip = '.'.join([str(int(s[8*i:8*(i+1)], 2)) for i in range(0, 4)])

        na1, netmask = ip_address(supernet_ip), num
        return ip_network('{}/{}'.format(na1, netmask), strict=False)
    
    def aggr(self, byte_thresh):
        #
        # write your code here
        #
        #
        if self.left is not None:
            self.left = self.left.aggr(byte_thresh)

            if self.left.bytes is not None and self.left.bytes < byte_thresh:
                self.bytes += self.left.bytes
                self.ip = Node.supernet(self.ip, self.left.ip)
                self.left = Node(self.left.ip, 0)

        if self.right is not None:
            self.right = self.right.aggr(byte_thresh)

            if self.right.bytes is not None and self.right.bytes < byte_thresh:
                self.bytes+=self.right.bytes
                self.ip = Node.supernet(self.ip,self.right.ip)
                self.right = Node(self.right.ip,0)

        return Node(self.ip,self.bytes)

class Data(object):
    def __init__(self, data):
        self.tot_bytes = 0
        self.data = {}
        self.aggr_ratio = 0.05
        root = None
        cnt = 0
        for pkt, metadata in RawPcapReader(data):
            ether = Ether(pkt)
            if not 'type' in ether.fields:
                continue
            if ether.type != 0x0800:
                continue
            ip = ether[IP]
            self.tot_bytes += ip.len
            if root is None:
                root = Node(ip_address(ip.src), ip.len)
            else:
                root.add(ip_address(ip.src), ip.len)
            cnt += 1
        root.aggr(self.tot_bytes * self.aggr_ratio)
        root.data(self.data)
    def Plot(self):
        data = {k: v/1000 for k, v in self.data.items()}
        plt.rcParams['font.size'] = 8
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.grid(which='major', axis='y')
        ax.tick_params(axis='both', which='major')
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels([str(l) for l in data.keys()], rotation=45,
            rotation_mode='default', horizontalalignment='right')
        ax.set_ylabel('Total bytes [KB]')
        ax.bar(ax.get_xticks(), data.values(), zorder=2)
        ax.set_title('IPv4 sources sending {} % ({}KB) or more traffic.'.format(
            self.aggr_ratio * 100, self.tot_bytes * self.aggr_ratio / 1000))
        plt.savefig(sys.argv[1] + '.aggr.pdf', bbox_inches='tight')
        plt.close()
    def _Dump(self):
        with open(sys.argv[1] + '.aggr.data', 'w') as f:
            f.write('{}'.format({str(k): v for k, v in self.data.items()}))

if __name__ == '__main__':
    d = Data(sys.argv[1])
    d.Plot()
    d._Dump()
