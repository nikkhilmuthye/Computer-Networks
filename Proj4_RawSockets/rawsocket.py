
import socket, sys
from struct import *
import posixpath
import urlparse
import time

FIN = 0x01
SYN = 0x02
RST = 0x04
PSH = 0x08
ACK = 0x10
URG = 0x20

ip_id = 10
CRLF = "\r\n"

cur_seq = 454
cur_ack = 0
orig_ack_no = 0
get_packet = ''
start = 0

packet_data = {}

page_link = sys.argv[1]

# Parse input and extract relative path, file_name and domain
parsed_uri = urlparse.urlsplit(page_link)   
relavtive_path = parsed_uri.path
filename = posixpath.basename(relavtive_path)
domain = parsed_uri.netloc


try:
    if filename == '':
        filename = "index.html"
    file = open("temp.txt", "w+")
except:
    print "Could not create file"


# Get source IP address
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    exit()
 
packet = '';
source_ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
s.close()

# Creating raw socket to send data
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    exit()

# Creating raw socket to receive data
try:
    recv = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    exit()


# Returns available open port at source
def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    #print port
    return port
    
# Returns HTTP GET request for URL
def create_get_msg(domain, relavtive_path):
    if len(relavtive_path) % 2 == 1:
        relavtive_path += " "
    HTTPmsg = "GET " + relavtive_path + " HTTP/1.1" + CRLF
    HTTPmsg += "Host: " + domain + CRLF + '\n' + CRLF
    return HTTPmsg

# Returns checksum for input data
def checksum(data):
    cksum = 0
    n = len(data) % 2
    for i in range(0, len(data)-n, 2):
        cksum+= ord(data[i]) + (ord(data[i+1]) << 8)
    if n:
        cksum+= ord(data[i+1])
    while (cksum >> 16):
        cksum = (cksum & 0xFFFF) + (cksum >> 16)
        
    cksum = ~cksum & 0xffff
    return cksum

# Sends ACK packet with ack_no to server
def send_ack(ack_no):
    global ip_id
    
    ip_id += 1
    iph_obj = IP_Header()
    iph_obj.assign(source_ip, dest_ip, ip_id)
    ip_hdr = iph_obj.pack()
    
    tcph_obj = TCP_Header()
    tcph_obj.assign(tcp_source, tcp_dest, cur_seq, ack_no, 0, 1, 0, "")
    tcp_hdr = tcph_obj.pack(source_ip, dest_ip)
    
    packet = ip_hdr + tcp_hdr + ""
    s.sendto(packet, (dest_ip , 0))

# Terminate connection with server by sending ACK and FIN, ACK
def terminate_connection(ack_no):
    send_ack(ack_no)
    
    # Sending FIN packet
    global ip_id
    
    start = 0
    elapsed = 0
    seconds = 60
    
    ip_id += 1
    iph_obj = IP_Header()
    iph_obj.assign(source_ip, dest_ip, ip_id)
    ip_hdr = iph_obj.pack()
    
    tcph_obj = TCP_Header()
    tcph_obj.assign(tcp_source, tcp_dest, cur_seq, ack_no, 0, 1, 1, "")
    tcp_hdr = tcph_obj.pack(source_ip, dest_ip)
    
    packet = ip_hdr + tcp_hdr + ""
    s.sendto(packet, (dest_ip , 0))
    start = time.clock()
    # Wait to receive ACK for FIN
    while True:
        packet = recv.recvfrom(65565)
        packet = packet[0]
    
        ip_header = packet[0:20]
        iph = IP_Header()
        iph.unpack(ip_header)
        data_cksum = checksum(ip_header)
        
        elapsed = time.clock() - start
        if elapsed > seconds:
            s.sendto(packet, (dest_ip , 0))
            start = time.clock()
    
        if iph.protocol == 6 and iph.src_ip == dest_ip and iph.dest_ip == source_ip and data_cksum == 0:
            tcp_hstart = iph.ihl * 4
            tcp_header = packet[tcp_hstart:tcp_hstart+20]
            tcph = TCP_Header()
            tcph.unpack(tcp_header)
            if tcph.src_port == tcp_dest and tcph.dest_port == tcp_source and tcph.ack_no == (cur_seq + 1):
                return
            

# TCP header class
class TCP_Header:
    def __init__(self):
        self.src_port = 0
        self.dest_port = 0
        self.seq_no = 454
        self.ack_no = 0
        self.offset = 5
        self.resrv = 0
        self.urg = 0
        self.ack = 0
        self.psh = 0
        self.rst = 0
        self.syn = 0
        self.fin = 0
        self.window = socket.htons(58400)
        self.cksum = 0
        self.uptr = 0
        self.data = ""
        
    # Assign values to TCP header fields
    def assign(self, src, dest, seq_no, ack_no, syn, ack, fin, data):
        self.src_port = src
        self.dest_port = dest
        self.seq_no = seq_no
        self.ack_no = ack_no
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.data = data
    
    
    # Pack TCP data into TCP header    
    def pack(self, source_ip, destination_ip):
        self.syn = self.syn << 1
        self.rst = self.rst << 2
        self.psh = self.psh << 3
        self.ack = self.ack << 4
        self.urg = self.urg << 5
        flags = self.fin + self.syn + self.rst + self.psh + self.ack + self.urg
        self.offset = (self.offset << 4) + 0
        
        tcp_header = pack("!HHLLBBHHH", self.src_port, self.dest_port, self.seq_no,
                          self.ack_no, self.offset, flags, self.window,
                          self.cksum, self.uptr)
        
        # Dummy Header Fields
        src_ip = socket.inet_aton(source_ip)
        dest_ip = socket.inet_aton(destination_ip)
        reserved_bits = 0
        protocol = socket.IPPROTO_TCP
        length = len(tcp_header) + len(self.data)
        
        pseudo_tcp_header = pack('!4s4sBBH', src_ip, dest_ip, reserved_bits, protocol, length)
        pseudo_tcp_header = pseudo_tcp_header + tcp_header + self.data
        self.cksum = checksum(pseudo_tcp_header)
        
        tcp_header = pack("!HHLLBBH", self.src_port, self.dest_port, self.seq_no, 
                          self.ack_no, self.offset, flags, self.window) + pack('H', self.cksum) + pack("!H", self.uptr)
        return tcp_header

    
    # Unpack TCP header data into object fields
    def unpack(self, data):
        tcph = unpack('!HHLLBBHHH' , data)
        
        self.src_port = tcph[0]
        self.dest_port = tcph[1]
        self.seq_no = tcph[2]
        self.ack_no = tcph[3]
        doff_reserved = tcph[4]
        resv_flags = tcph[5]
        
        self.offset = doff_reserved >> 4
        self.resrv = ((doff_reserved & 0xF) << 2) + (resv_flags >> 6)
        
        flags = resv_flags & 0x3F
        self.urg = (flags & URG) >> 5
        self.ack = (flags & ACK) >> 4
        self.psh = (flags & PSH) >> 3
        self.rst = (flags & RST) >> 2
        self.syn = (flags & SYN) >> 1
        self.fin = flags & FIN
        
        self.window = tcph[6]
        self.cksum = tcph[7]
        self.uptr = tcph[8]

# IP header class
class IP_Header:
    def __init__(self):
        self.src_ip = 0
        self.dest_ip = 0
        self.version = 4
        self.ihl = 5
        self.tos = 0
        self.length = 0
        self.id = 54321
        self.flags = 0
        self.frg_offset = 0
        self.ttl = 255
        self.protocol = socket.IPPROTO_TCP
        self.cksum = 0
        
    # Assign values to IP header fields
    def assign(self, src, dest, id):
        self.src_ip = socket.inet_aton(src)
        self.dest_ip = socket.inet_aton(dest)
        self.id = id

    # Pack IP data into IP header        
    def pack(self):
        word1 = (self.version << 4) + self.ihl
        word2 = (self.flags << 13) + self.frg_offset
        iphdr = pack('!BBHHHBBH4s4s', word1, self.tos, self.length, self.id, word2,
                      self.ttl, self.protocol, self.cksum, self.src_ip, self.dest_ip)
        return iphdr
    
    # Unpack IP header data into class fields
    def unpack(self, data):
        iph = unpack('!BBHHHBBH4s4s' , data)
        version_ihl = iph[0]
        
        self.version = version_ihl >> 4
        self.ihl = version_ihl & 0xF
        self.tos = iph[1]
        self.length = iph[2]
        self.id = iph[3]
        flags_offset = iph[4]
        self.flags = flags_offset >> 13
        self.frg_offset = flags_offset & 0x1FFF
        self.ttl = iph[5]
        self.protocol = iph[6]
        self.cksum = iph[7]
        self.src_ip = socket.inet_ntoa(iph[8]);
        self.dest_ip = socket.inet_ntoa(iph[9]);
        
        

# Complete 3-Way Handshake
def handshake():
    global cur_ack, cur_seq, dest_ip, ip_id, orig_ack_no, get_packet, start
    elapsed = 0
    seconds = 60
    dest_ip = socket.gethostbyname(domain)
    
    # Sending first SYN packet
    iph_obj = IP_Header()
    iph_obj.assign(source_ip, dest_ip, ip_id)
    ip_hdr = iph_obj.pack()
    user_data = ''

    tcph_obj = TCP_Header()
    tcph_obj.assign(tcp_source, tcp_dest, cur_seq, cur_ack, 1, 0, 0, user_data)
    tcp_hdr = tcph_obj.pack(source_ip, dest_ip)
    
    syn_packet = ip_hdr + tcp_hdr + user_data
 
    s.sendto(syn_packet, (dest_ip , 0))
    start = time.clock()

    while True:
        recv.settimeout(180)
        try:
            packet = recv.recvfrom(65565)
        except socket.timeout:
            print'No packet received for 3 minutes...Terminating program.'
            s.close()
            recv.close()
            exit()
            
        packet = packet[0]
     
        # Accept SYN/ACK from server
        ip_header = packet[0:20]
        iph = IP_Header()
        iph.unpack(ip_header)
        ack_cksum = checksum(ip_header)
        
        elapsed = time.clock() - start
        if elapsed > seconds:
            s.sendto(syn_packet, (dest_ip , 0))
            start = time.clock()
                
        if iph.protocol == 6 and iph.src_ip == dest_ip and iph.dest_ip == source_ip and ack_cksum == 0:
            
            tcp_hstart = iph.ihl * 4
            tcp_header = packet[tcp_hstart:tcp_hstart+20]
            tcph = TCP_Header()
            tcph.unpack(tcp_header)
            
            if tcph.src_port == tcp_dest and tcph.dest_port == tcp_source and tcph.ack == 1 and tcph.ack_no == (cur_seq + 1) and not tcph.rst:
                
                cur_seq = tcph.ack_no
                cur_ack = tcph.seq_no + 1
                orig_ack_no = cur_ack
                
                # Sending ACK with GET request packet
                ip_id += 1
                iph_obj = IP_Header()
                iph_obj.assign(source_ip, dest_ip, ip_id)
                ip_hdr = iph_obj.pack()
                user_data = create_get_msg(domain, relavtive_path)

                tcph_obj = TCP_Header()
                tcph_obj.assign(tcp_source, tcp_dest, cur_seq, cur_ack, 0, 1, 0, user_data)
                tcp_hdr = tcph_obj.pack(source_ip, dest_ip)

                get_packet = ip_hdr + tcp_hdr + user_data
                s.sendto(get_packet, (dest_ip , 0))
                start = time.clock()
                break

tcp_source = get_open_port()    # source port
tcp_dest = 80                   # destination port    

handshake()

http_get = create_get_msg(domain, relavtive_path)
cur_seq += len(http_get)
http_ack = False
rtt_start = time.clock()

# Accept the incoming packets from server and finish the TCP connection
while True:

    # Terminate program after 3 minutes timeout
    recv.settimeout(180)
    try:
        packet = recv.recvfrom(65565)
    except socket.timeout:
        print'No packet received for 3 minutes...Terminating program.'
        s.close()
        recv.close()
        exit()
    
    packet = packet[0]
    
    # Resend GET request after 1 minutes timeout
    elapsed = time.clock() - start
    if elapsed > 60 and not http_ack:
        print 'Resending ACK and GET request'
        s.sendto(get_packet, (dest_ip , 0))
        start = time.clock()
            
    # Unpack IP header
    ip_header = packet[0:20]
    iph = IP_Header()
    iph.unpack(ip_header)
    data_cksum = checksum(ip_header)
    
    # Validate IP header
    if iph.protocol == 6 and iph.src_ip == dest_ip and iph.dest_ip == source_ip and data_cksum == 0:
        tcp_hstart = iph.ihl * 4
        tcp_header = packet[tcp_hstart:tcp_hstart+20]
        tcph = TCP_Header()
        tcph.unpack(tcp_header)
        header_len = tcp_hstart + tcph.offset * 4
        data_len = iph.length - header_len
        pack_data = packet[header_len:]
        
        # Calculating TCP checksum
        src_ip_net = socket.inet_aton(source_ip)
        dest_ip_net = socket.inet_aton(dest_ip)
        reserved_bits = 0
        length = len(tcp_header) + len(pack_data)
        pseudo_tcp_header = pack('!4s4sBBH', src_ip_net, dest_ip_net, reserved_bits, iph.protocol, length)
        pseudo_tcp_header += tcp_header + pack_data
        tcp_cksum = checksum(pseudo_tcp_header)
        
        # Validate TCP header
        if tcph.src_port == tcp_dest and tcph.dest_port == tcp_source and tcph.ack_no == cur_seq:
            rtt_elapsed = time.clock() - rtt_start
            if rtt_elapsed > 180:
                print'No packet received for 3 minutes...Terminating program.'
                s.close()
                recv.close()
                exit()
            
            rtt_start = time.clock()
                
            if tcph.fin == 1:
                cur_ack += 1
                terminate_connection(cur_ack)
                break
            if tcph.ack == 1 and http_ack == False and tcph.ack_no == cur_seq:
                http_ack = True
                continue
            if tcph.syn == 1 and tcph.ack == 1:
                continue
            else:
                if packet_data.has_key(tcph.seq_no):
                    # Packet is retransmission. Hence ACK Packet was lost and resend
                    send_ack(tcph.seq_no + data_len)
                else:
                    cur_ack += data_len
                    packet_data[tcph.seq_no] = pack_data
                    send_ack(cur_ack)

# Sort received data
file_data = sorted(packet_data.iteritems(), key=lambda key_value: key_value[0])

valid_format = False
write = False

# Write data to temporary file
for value in file_data:
    if ("HTTP/1.1" in value[1]) and ("200" not in value[1]):
        print "Error: HTTP response returned a status other than 200"
        file.close()
        s.close()
        recv.close()
        exit()
    file.write(value[1])
    
file.close()

op_file = open(filename, "w+")
f_temp = open("temp.txt", "r")
page_data = f_temp.readlines()

# Remove HTTP header and write to output file
for data in page_data:
    if write == True:
        op_file.write(data)

    if valid_format == True:
        write = True
    
    if "Content-Type:" in data:
        valid_format = True

# Terminate by closing file pointers and sockets
f_temp.close()
op_file.close()
s.close()
recv.close()
