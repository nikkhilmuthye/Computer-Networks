#!/bin/bash

if test $1 -eq 1
then
   TCP_type=("TCP" "TCP/Reno" "TCP/Newreno" "TCP/Vegas")
   Protocols=("TCP" "Reno" "Newreno" "Vegas")

   source=0.0
   dest=3.0
 
   rm Expr1_log/*

   for type in "${TCP_type[@]}"
   do
      file_prefix=`echo $type | cut -d '/' -f 2`

      if [ -z $file_prefix ]
      then
         file_prefix="TCP"
      fi

      for i in {1..10}
      do
         file_name=$file_prefix"_"$i
         cbr_rate=$i"mb"
         /course/cs4700f12/ns-allinone-2.35/bin/ns Experiment_1.tcl $type $cbr_rate $file_name
      done
   done

   mv TCP_* Reno_* Newreno_* Vegas_* Expr1_log/.

   for protocol in "${Protocols[@]}"
   do
      ./parse.py $source $dest $protocol
   done
elif test $1 -eq 2
then
   TCP_type1=("TCP/Reno" "TCP/Newreno" "TCP/Vegas" "TCP/Newreno")
   TCP_type2=("TCP/Reno" "TCP/Reno" "TCP/Vegas" "TCP/Vegas")

   source1=0.0
   dest1=3.0
   source2=4.0
   dest2=5.0

   rm Expr2_log/*

   for i in {0..3}
   do
      #protocol_1=${TCP_type1[`expr $i-1`]}
      #protocol_2=${TCP_type2[`expr $i-1`]}
      protocol_1=${TCP_type1[$i]}
      protocol_2=${TCP_type2[$i]}

      type1=`echo $protocol_1 | cut -d '/' -f 2`
      type2=`echo $protocol_2 | cut -d '/' -f 2`

      for j in {1..10}
      do
         file_name=$type1"_"$type2"_"$j
	 cbr_rate=$j"mb"
	 /course/cs4700f12/ns-allinone-2.35/bin/ns Experiment_2.tcl $protocol_1 $protocol_2 $cbr_rate $file_name
      done
   done

   for i in {0..3}
   do
      type1=`echo ${TCP_type1[$i]} | cut -d '/' -f 2`
      type2=`echo ${TCP_type2[$i]} | cut -d '/' -f 2`

      mv $type1"_"$type2"_"* Expr2_log/.
      ./parse_exp_2.py $source1 $dest1 $type1 $source2 $dest2 $type2
   done
elif test $1 -eq 3
then
   TCP_type=("TCP/Sack1" "TCP/Reno")
   Queue_type=("DropTail" "RED")

   rm Expr3_log/*

   for i in {0,1}
   do
      protocol=${TCP_type1[$i]}

      type=`echo $protocol | cut -d '/' -f 2`

      for queue in "${Queue_type[@]}"
      do
         file_name=$type"_"$queue
	 /course/cs4700f12/ns-allinone-2.35/bin/ns Experiment_3.tcl $protocol $queue $file_name
      done
   done

fi




