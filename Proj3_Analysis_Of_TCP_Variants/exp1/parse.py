#!/usr/bin/python

import os
import sys
import pylab
import matplotlib.pyplot as plt

source = sys.argv[1]
dest = sys.argv[2]
protocol = sys.argv[3]

path = 'Expr1_log'

f_throughput = open(protocol + "_throughput.xls", "w")
f_drop_rate = open(protocol + "_drop_rate.xls", "w")
f_latency = open(protocol + "_latency.xls", "w")

print 'Protocol' + '\t' + 'Bit-Rate' + '\t' + 'Throughput' + '\t' + 'Drop-rate' + '\t' + 'Latency'

for file in os.listdir(path):
   filename = os.path.join(path, file)

   file_split = file.split('_')
   tcp_type = file_split[0]
   bit_rate = file_split[1]

   if protocol == tcp_type:
      total_data = 0
      send_data = {}
      recv_data = {}
      drop_data = {}
      no_sent_packets = 0
      no_recv_packets = 0
      drop_packets = 0
      start_time = 0.1
      end_time = 0.0
      throughput_delay = 0.0
      delay = 0.0

      with open(filename) as lines:
         for line in lines:
            packet = line.split(' ')

	    if (packet[0] == '+' and packet[2] == '0' and packet[3] == '1' and packet[4] == "tcp" and packet[8] == source and packet[9] == dest):
	       send_data[packet[10]] = float(packet[1])
	       '''if packet[10] in send_data.keys():
	          send_data[packet[10]] = float(packet[1])
	       else:
	          send_data[packet[10]] = float(packet[1])'''
	       no_sent_packets += 1

	    if (packet[0] == 'r' and packet[2] == '2' and packet[3] == '3' and packet[4] == 'tcp' and packet[8] == source and packet[9] == dest):
	       recv_data[packet[10]] = float(packet[1]) - send_data[packet[10]]
	       delay += recv_data[packet[10]]
	       if packet[10] not in drop_data.keys():
	          total_data += int(packet[5])
	          no_recv_packets += 1
		  throughput_delay += recv_data[packet[10]]
	       end_time = float(packet[1])

	    if (packet[0] == 'd' and packet[4] == 'tcp' and packet[8] == source and packet[9] == dest):
	       drop_packets += 1
	       drop_data[packet[10]] = float(packet[1])

      end_time = end_time
      throughput = total_data / end_time
      #throughput = total_data / throughput_delay
      drop_rate = float(drop_packets) / no_sent_packets
      #latency = delay / no_sent_packets
      latency = delay / no_recv_packets

      print protocol + '\t' + bit_rate + '\t' + str(throughput) + '\t' + str(drop_rate) + '\t' + str(latency)
      f_throughput.write(bit_rate + "," + str(throughput) + '\n')
      f_drop_rate.write(bit_rate + "," + str(drop_rate) + '\n')
      f_latency.write(bit_rate + "," + str(latency) + '\n')


f_throughput.close()
f_drop_rate.close()
f_latency.close()

