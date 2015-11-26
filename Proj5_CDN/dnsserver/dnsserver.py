#!/usr/bin/python

import sys, os
PWD = os.getcwd()
sys.path.append(PWD)

from SocketServer import BaseRequestHandler, ThreadingUDPServer
from cStringIO import StringIO
import socket
import struct
import time
import datetime
import random
import threading
import signal

dns_mappings = {}
client_mappings = {}
replica_time = {}
client_min_time = {}
scamper_ip = []

user_name = ''

condition = threading.Condition()

TYPE_A = 1
TYPE_AAAA = 28
CLASS_IN = 1



def to_net_addr(address):
    try:
        return socket.inet_pton(socket.AF_INET, address)
    except:
        return socket.inet_pton(socket.AF_INET6, address)


def _get_dns_labels(msg):
    all_labels = []
    length = ord(msg.read(1))
    while length > 0:
        if length >= 64:
            length = length & 0x3f
            offset = (length << 8) + ord(msg.read(1))
            msg = StringIO(msg.getvalue())
            msg.seek(offset)
            all_labels.extend(_get_dns_labels(msg))
            return all_labels
        else:
            all_labels.append(msg.read(length))
            length = ord(msg.read(1))
    return all_labels


def get_question(msg):
    name = get_dns_name(msg)
    type, que_class = struct.unpack('!HH', msg.read(4))
    offset = msg.tell()
    return Struct(name=name, type_=type, class_=que_class, end_offset=offset)


def get_dns_name(msg):
    return '.'.join(_get_dns_labels(msg))


def get_record(msg):
    get_dns_name(msg)
    msg.seek(4, os.SEEK_CUR)
    ttl_off = msg.tell()
    time_to_live = struct.unpack('!I', msg.read(4))[0]
    len_record = struct.unpack('!H', msg.read(2))[0]
    msg.seek(len_record, os.SEEK_CUR)
    return Struct(ttl_offset=ttl_off, ttl=time_to_live)


def get_message(data):
    msg = StringIO(data)
    msg.seek(4)
    c_qd, c_an, c_ns, c_ar = struct.unpack('!4H', msg.read(8))
    question = get_question(msg)
    for i in range(1, c_qd):
        get_question(msg)
    records = []
    for i in range(c_an+c_ns+c_ar):
        records.append(get_record(msg))
    return Struct(question=question, records=records)


class DNSHandler(BaseRequestHandler):
    
    def handle(self):
        request, socket = self.request
        req = get_message(request)
        
        q = req.question
        #if !q.name.endswith(CDN_Name):
        if q.name != CDN_Name:
            return
        #    return

        if q.type_ in (TYPE_A, TYPE_AAAA) and (q.class_ == CLASS_IN):
            packed_ip = self.find_best_server(q)
            rspdata = request[:2] + '\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00'
            rspdata += request[12:q.end_offset]
            rspdata += '\xc0\x0c'
            if len(packed_ip) == 4:
                rspdata += '\x00\x01'
            else:
                rspdata += '\x00\x1c'
            rspdata += '\x00\x01\x00\x00\x07\xd0'
            rspdata += '\x00' + chr(len(packed_ip))
            rspdata += packed_ip
            socket.sendto(rspdata, self.client_address)
            return

        if not self.server.disable_cache:
            cache = self.server.cache
            cache_key = (q.name, q.type_, q.class_)
            cache_entry = cache.get(cache_key)

    def _get_response(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.server.dns_server, 53))
        sock.sendall(data)
        sock.settimeout(60)
        rspdata = sock.recv(65535)
        sock.close()
        return rspdata

    def find_best_server(self, query):
        global client_mappings, scamper_ip
        client_ip = self.client_address[0]
        if client_ip not in client_mappings:
            key = random.choice(dns_mappings.keys())
            closest_ip = dns_mappings[key]
            client_mappings[client_ip] = closest_ip

            scamper_ip.append(client_ip)
        else:
            closest_ip = client_mappings[client_ip]

        closest_ip = to_net_addr(closest_ip)
        return closest_ip

    
class Struct(object):
    def __init__(self, **kwargs):
        for key, values in kwargs.items():
            setattr(self, key, values)
    
    
class DNSServer(ThreadingUDPServer):
    def __init__(self, disable_cache=False, host='127.0.0.1', port=53000):
        self.disable_cache = disable_cache
        self.cache = {}
        ThreadingUDPServer.__init__(self, (host, port), DNSHandler)


def scamper_handler(replica, client, avg_time):
    replica_ip = dns_mappings[replica]
    last_probe_duration = time.time() - replica_time[replica_ip]

    if last_probe_duration < 1:
        time.sleep(1 - last_probe_duration)


    # Check if the httpserver is running on replica server
    f = os.popen("ssh " + replica + " \'ps acux | grep httpserver | grep " + user_name + "\'")
    process_running = f.read().split('\n')[0]

    if process_running == '':
        replica_running = False
    else:
        replica_running = True

    # If httpserver running, then get the RTO between replica and client
    if replica_running:
        command = 'ssh ' + replica + ' \'scamper -i ' + client + ' -c ping\''
        f = os.popen(command)
        result = f.read().split('\n')[0:-1][-1]

        result = result.split('=')[1].strip()
        avg_rto = float(result.split('/')[1]) / 1000000000


        avg_time.append(avg_rto)

        replica_time[replica] = time.time()
    else:
        avg_time.append(100002.0)



def thread_for_replica(name, client):
    result = []
    thread = threading.Thread(target=scamper_handler, args=(name, client, result, ))
    return (thread, name, result)


def run():
    while True:
        i = 0
        number_of_clients = len(scamper_ip)
        if number_of_clients == 0:
            time.sleep(10)
        else:
            while i < number_of_clients:
                client = scamper_ip[i]
                relica_servers = list(dns_mappings.keys())
                threads = [thread_for_replica(k, client) for k in relica_servers]

                for t in threads:
                    t[0].start()

                if client not in client_min_time:
                    min_time = 100000.0
                else:
                    min_time = client_min_time[client]
                curr_min_replica = client_mappings[client]

                for t in threads:
                    t[0].join()
                    if t[2][0] < min_time:
                        min_time = t[2][0]
                        client_mappings[client] = dns_mappings[t[1]]

                client_min_time[client] = min_time
                i += 1

def signal_handler(signal, frame):
	dnsserver.shutdown()
        dnsserver.server_close()
        sys.exit(0)

def main():
    global dns_mappings, CDN_Name, user_name
    if len(sys.argv) == 7 and sys.argv[1] == '-p' and sys.argv[3] == '-n':
        port_number = int(sys.argv[2])
        CDN_Name = sys.argv[4]
        host_ip = sys.argv[5]
        hosts_file = sys.argv[6]
    else:
        print 'Incorrect Usage.'
        print 'Usage : '
        print './dnsserver -p <port> -n <name>'
        print 'Exiting program.'
        exit()
    
    try:
        disable_cache = True
    
        f_temp = open(hosts_file, "r")
        readlines = f_temp.readlines()
        
        for line in readlines:
            data = line.split('\t')
            replica = data[0]
            ip = data[1].strip()
            dns_mappings[replica] = ip
            ts = time.time()
            replica_time[ip] = ts

        # Get the Username on replica server
        f = os.popen("whoami")
        user_name = f.read().split('\n')[0]

        dnsserver = DNSServer(disable_cache=disable_cache, host=host_ip, port=port_number)

        thread = threading.Thread(target=run, args=())
        thread.daemon = True

        thread.start()
	signal.signal(signal.SIGINT, signal_handler)

        dnsserver.serve_forever()
    except KeyboardInterrupt:
        dnsserver.shutdown()
        dnsserver.server_close()

    
if __name__ == '__main__':
    main()


