#!/usr/bin/python

import os
import sys

source1 = sys.argv[1]
dest1 = sys.argv[2]
source2 = sys.argv[3]
dest2 = sys.argv[4]

path = 'Expr3_log'

for file in os.listdir(path):
   filename = os.path.join(path, file)

   print '\n' + 'Protocol' + '\t' + 'Queue' + '\t' + 'TCP' + '\t' + '\t' + 'CBR' + '\t' + 'TCP_Drop' + '\t' + 'CBR_Drop' + '\t' + 'Drop Rate1' + '\t' + 'Drop Rate2' + '\t' + 'Latency 1' + '\t' + 'Latency 2' + '\n'
   file_split = file.split('_')
   protocol = file_split[0].split('1')[0]
   Queue = file_split[1]
   f_output = open(protocol + "_" + Queue + "_THR.xls", "w")

   time = 1.0
   total_data1 = 0
   total_data2 = 0
   tcp_drop = 0
   cbr_drop = 0
   drop_data1 = {}
   drop_data2 = {}
   no_sent_packets1 = 0
   no_sent_packets2 = 0
   delay1 = 0.0
   delay2 = 0.0
   no_recv_packets1 = 0
   no_recv_packets2 = 0
   drop_packets1 = 0
   drop_packets2 = 0
   send_data1 = {}
   send_data2 = {}
   recv_data1 = {}
   recv_data2 = {}
   drop_rate1 = 0.0
   drop_rate2 = 0.0
   latency1 = 0.0
   latency2 = 0.0

   with open(filename) as lines:
      for line in lines:
         packet = line.split(' ')

         if (float(packet[1]) > time):

            if no_sent_packets1 == 0:
	       drop_rate = 0.0
	    else:
	       drop_rate1 = float(drop_packets1) / no_sent_packets1

            if no_recv_packets1 == 0:
	       latency1 = 0.0
	    else:
	       latency1 = delay1/ no_recv_packets1

            if no_sent_packets2 == 0:
	       drop_rate = 0.0
	    else:
	       drop_rate2 = float(drop_packets2) / no_sent_packets2

            if no_recv_packets2 == 0:
	       latency2 = 0.0
	    else:
	       latency2 = delay2/ no_recv_packets2

            total_data1 = total_data1 / 128
            total_data2 = total_data2 / 128

            print protocol + '\t' + Queue + '\t' + str(int(time)) + '\t' + str(total_data1) + '\t' + '\t' + str(total_data2) + '\t' + str(tcp_drop) + '\t' + str(cbr_drop) + '\t' + str(drop_rate1) + '\t' + str(drop_rate2) + '\t' + str(latency1) + '\t' + str(latency2) + '\n'
            f_output.write(str(int(time)) + ',' + str(total_data1) + ',' + str(total_data2) + ',' + str(tcp_drop) + ',' + str(cbr_drop) + ',' + str(drop_rate1) + ',' + str(drop_rate2) + ',' + str(latency1) + ',' + str(latency2) + '\n')
            #f_output.write(str(int(time)) + ',' + str(total_data1) + ',' + str(total_data2) + ',' + str(tcp_drop) + ',' + str(cbr_drop) + '\n')
            #print protocol + '\t' + Queue + '\t' + str(int(time)) + '\t' + str(total_data1) + '\t' + '\t' + str(total_data2) + '\t' + str(tcp_drop) + '\t' + str(cbr_drop) + '\n'
            time += 1
            total_data1 = 0
            total_data2 = 0
            tcp_drop = 0
            cbr_drop = 0
            no_sent_packets1 = 0
            no_sent_packets2 = 0
            delay1 = 0.0
            delay2 = 0.0
            no_recv_packets1 = 0
            no_recv_packets2 = 0
            drop_packets1 = 0
            drop_packets2 = 0
            drop_rate1 = 0.0
            drop_rate2 = 0.0
            latency1 = 0.0
            latency2 = 0.0
         else:
	    # Calculation for TCP flow
	    if (packet[0] == '+' and packet[2] == '0' and packet[3] == '1' and packet[4] == "tcp" and packet[8] == source1 and packet[9] == dest1):
	       send_data1[packet[10]] = float(packet[1])
	       no_sent_packets1 += 1

	    if (packet[0] == 'r' and packet[2] == '2' and packet[3] == '3' and packet[4] == "tcp" and packet[8] == source1 and packet[9] == dest1):
               recv_data1[packet[10]] = float(packet[1]) - send_data1[packet[10]]
               delay1 += recv_data1[packet[10]]
	       if packet[10] not in drop_data1.keys():
	          no_recv_packets1 += 1
	          total_data1 += int(packet[5])

	    if (packet[0] == 'd' and packet[4] == 'tcp' and packet[8] == source1 and packet[9] == dest1):
	       drop_packets1 += 1
	       drop_data1[packet[10]] = float(packet[1])
	       tcp_drop += int(packet[5])

	    # Calculation for CBR flow
	    if (packet[0] == '+' and packet[2] == '4' and packet[3] == '1' and packet[4] == 'cbr' and packet[8] == source2 and packet[9] == dest2):
	       send_data2[packet[10]] = float(packet[1])
	       no_sent_packets2 += 1

            if (packet[0] == 'r' and packet[2] == '2' and packet[3] == '5' and packet[4] == 'cbr' and packet[8] == source2 and packet[9] == dest2):
               recv_data2[packet[10]] = float(packet[1]) - send_data2[packet[10]]
               delay2 += recv_data2[packet[10]]
               if packet[10] not in drop_data2.keys():
	          no_recv_packets2 += 1
                  total_data2 += int(packet[5])

            if (packet[0] == 'd' and packet[4] == 'cbr' and packet[8] == source2 and packet[9] == dest2):
	       drop_packets2 += 1
               drop_data2[packet[10]] = float(packet[1])
	       cbr_drop += int(packet[5])


      if no_sent_packets1 == 0:
         drop_rate = 0.0
      else:
         drop_rate1 = float(drop_packets1) / no_sent_packets1

      if no_recv_packets1 == 0:
         latency1 = 0.0
      else:
         latency1 = delay1/ no_recv_packets1

      if no_sent_packets2 == 0:
         drop_rate = 0.0
      else:
         drop_rate2 = float(drop_packets2) / no_sent_packets2

      if no_recv_packets2 == 0:
         latency2 = 0.0
      else:
         latency2 = delay2/ no_recv_packets2
   
      total_data1 = total_data1 / 128
      total_data2 = total_data2 / 128

   #print protocol + '\t' + Queue + '\t' + str(int(time)) + '\t' + str(total_data1) + '\t' + str(total_data2) + '\n'
   print protocol + '\t' + Queue + '\t' + str(int(time)) + '\t' + str(total_data1) + '\t' + '\t' + str(total_data2) + '\t' + str(tcp_drop) + '\t' + str(cbr_drop) + '\t' + str(drop_rate1) + '\t' + str(drop_rate2) + '\t' + str(latency1) + '\t' + str(latency2) + '\n'
   f_output.write(str(int(time)) + ',' + str(total_data1) + ',' + str(total_data2) + ',' + str(tcp_drop) + ',' + str(cbr_drop) + ',' + str(drop_rate1) + ',' + str(drop_rate2) + ',' + str(latency1) + ',' + str(latency2) + '\n')
   f_output.close()


