#!/usr/bin/python

import os
import sys
import pylab
import matplotlib.pyplot as plt

source1 = sys.argv[1]
dest1 = sys.argv[2]
protocol1 = sys.argv[3]
source2 = sys.argv[4]
dest2 = sys.argv[5]
protocol2 = sys.argv[6]

path = 'Expr2_log'

f_throughput = open(protocol1 + "_" + protocol2 + "_THR.xls", "w")
f_drop_rate = open(protocol1 + "_" + protocol2 + "_DR.xls", "w")
f_latency = open(protocol1 + "_" + protocol2 + "_LAT.xls", "w")

#print "Source 1 = " + source1 + " Source2 = " + source2 + '\n'
print 'Protocol' + '\t' + 'Bit-Rate' + '\t' + 'Throughput' + '\t' + 'Drop-rate' + '\t' + 'Latency' + '\n'

for file in os.listdir(path):
   filename = os.path.join(path, file)

   file_split = file.split('_')
   tcp_type1 = file_split[0]
   tcp_type2 = file_split[1]
   bit_rate = file_split[2]
   #print file

   if protocol1 == tcp_type1 and protocol2 == tcp_type2:
      total_data1 = 0
      total_data2 = 0
      send_data1 = {}
      recv_data1 = {}
      drop_data1 = {}
      send_data2 = {}
      recv_data2 = {}
      drop_data2 = {}

      no_sent_packets1 = 0
      no_recv_packets1 = 0
      drop_packets1 = 0
      no_sent_packets2 = 0
      no_recv_packets2 = 0
      drop_packets2 = 0

      start_time = 0.1
      end_time1 = 0.0
      end_time2 = 0.0
      throughput_delay1 = 0.0
      throughput_delay2 = 0.0
      delay1 = 0.0
      delay2 = 0.0

      with open(filename) as lines:
         for line in lines:
            packet = line.split(' ')

	    # Calculation for TCP flow 1
	    if (packet[0] == '+' and packet[2] == '0' and packet[3] == '1' and packet[4] == "tcp" and packet[7] == '1' and packet[8] == source1 and packet[9] == dest1):
	       send_data1[packet[10]] = float(packet[1])
	       '''if packet[10] in send_data.keys():
	          send_data[packet[10]] = float(packet[1])
	       else:
	          send_data[packet[10]] = float(packet[1])'''
	       no_sent_packets1 += 1

	    if (packet[0] == 'r' and packet[2] == '2' and packet[3] == '3' and packet[4] == "tcp" and packet[7] == '1' and packet[8] == source1 and packet[9] == dest1):
	       recv_data1[packet[10]] = float(packet[1]) - send_data1[packet[10]]
	       delay1 += recv_data1[packet[10]]
	       if packet[10] not in drop_data1.keys():
	          total_data1 += int(packet[5])
	          no_recv_packets1 += 1
		  throughput_delay1 += recv_data1[packet[10]]
	       end_time1 = float(packet[1])

	    if (packet[0] == 'd' and packet[4] == 'tcp' and packet[7] == '1' and packet[8] == source1 and packet[9] == dest1):
	       drop_packets1 += 1
	       drop_data1[packet[10]] = float(packet[1])


	    # Calculation for TCP flow 2
            if (packet[0] == '+' and packet[2] == '4' and packet[3] == '1' and packet[4] == "tcp" and packet[7] == '2' and packet[8] == source2 and packet[9] == dest2):
               send_data2[packet[10]] = float(packet[1])
               '''if packet[10] in send_data.keys():
                  send_data[packet[10]] = float(packet[1])
               else:
                  send_data[packet[10]] = float(packet[1])'''
               no_sent_packets2 += 1

            if (packet[0] == 'r' and packet[2] == '2' and packet[3] == '5' and packet[4] == 'tcp' and packet[7] == '2' and packet[8] == source2 and packet[9] == dest2):
               recv_data2[packet[10]] = float(packet[1]) - send_data2[packet[10]]
               delay2 += recv_data2[packet[10]]
               if packet[10] not in drop_data2.keys():
                  total_data2 += int(packet[5])
                  no_recv_packets2 += 1
                  throughput_delay2 += recv_data2[packet[10]]
               end_time2 = float(packet[1])

            if (packet[0] == 'd' and packet[4] == "tcp" and packet[7] == '2' and packet[8] == source2 and packet[9] == dest2):
               drop_packets2 += 1
               drop_data2[packet[10]] = float(packet[1])


      #print "Hello End_time 1 = " + str(end_time1) + " End_time 2  = " + str(end_time2)
      if end_time1 == 0.0:
         throughput1 = 0.0
      else:
         throughput1 = total_data1 / end_time1
      #throughput = total_data / throughput_delay
      drop_rate1 = float(drop_packets1) / no_sent_packets1
      #latency = delay / no_sent_packets
      if no_recv_packets1 == 0:
         latency1 = 0.0
      else:
         latency1 = delay1 / no_recv_packets1

      if end_time2 == 0.0:
         throughput2 = 0.0
      else:
         throughput2 = total_data2 / end_time2
      #throughput = total_data / throughput_delay
      drop_rate2 = float(drop_packets2) / no_sent_packets2
      #latency = delay / no_sent_packets
      if no_recv_packets2 == 0:
         latency2 = 0.0
      else:
         latency2 = delay2 / no_recv_packets2


      print protocol1 + '\t' + bit_rate + '\t' + str(throughput1) + '\t' + str(drop_rate1) + '\t' + str(latency1)
      print protocol2 + '\t' + bit_rate + '\t' + str(throughput2) + '\t' + str(drop_rate2) + '\t' + str(latency2) + '\n'
      f_throughput.write(bit_rate + "," + str(throughput1) + "," + str(throughput2) + '\n')
      f_drop_rate.write(bit_rate + "," + str(drop_rate1) + "," + str(drop_rate2) + '\n')
      f_latency.write(bit_rate + "," + str(latency1) + "," + str(latency2) + '\n')


f_throughput.close()
f_drop_rate.close()
f_latency.close()

