 #Make a NS simulator
  set ns [new Simulator]

  set tcp_type1  [lindex $argv 0]
  set tcp_type2  [lindex $argv 1]
  set cbr_rate   [lindex $argv 2]
  set file_name  [lindex $argv 3]
  
  puts "Protocol 1 = $tcp_type1 "
  puts "Protocol 2 = $tcp_type2 "
  puts "cbr_rate = $cbr_rate "
  puts "file_name = $file_name "
  # Write trace data to output file
  set trace_file [open  $file_name  w]
  $ns  trace-all  $trace_file

  # Define a finish procedure
  proc finish {} {
     global ns trace_file
     $ns flush-trace
     close $trace_file
     exit 0
  }

  # Create the nodes:
  set n1 [$ns node]
  set n2 [$ns node]
  set n3 [$ns node]
  set n4 [$ns node]
  set n5 [$ns node]
  set n6 [$ns node]

  # Create the links:
  $ns duplex-link $n1 $n2   10Mb  2ms DropTail
  $ns duplex-link $n2 $n3   10Mb  2ms DropTail
  $ns duplex-link $n2 $n5   10Mb  2ms DropTail
  $ns duplex-link $n3 $n4   10Mb  2ms DropTail
  $ns duplex-link $n3 $n6   10Mb  2ms DropTail

#############################################
  # TCP Stream 1 from node n1 to node n4
  # Add a TCP sending module to node n1
  set tcp1 [new Agent/$tcp_type1]
  $ns attach-agent $n1 $tcp1

  # Add a TCP receiving module to node n4
  set sink1 [new Agent/TCPSink]
  $ns attach-agent $n4 $sink1

  # Direct traffic from "tcp1" to "sink1"
  $ns connect $tcp1 $sink1
  $tcp1 set fid_ 1

  # Setup a FTP traffic generator on "tcp1"
  set ftp1 [new Application/FTP]
  $ftp1 attach-agent $tcp1
  $ftp1 set type_ FTP

#############################################
  # TCP Stream 2 from node n5 to node n6
  # Add a TCP sending module to node n5
  set tcp2 [new Agent/$tcp_type2]
  $ns attach-agent $n5 $tcp2

  # Add a TCP receiving module to node n6
  set sink2 [new Agent/TCPSink]
  $ns attach-agent $n6 $sink2

  # Direct traffic from "tcp2" to "sink2"
  $ns connect $tcp2 $sink2
  $tcp2 set fid_ 2

  # Setup a FTP traffic generator on "tcp1"
  set ftp2 [new Application/FTP]
  $ftp2 attach-agent $tcp2
  $ftp2 set type_ FTP

#############################################
  #Setup a UDP connection
  set udp [new Agent/UDP]
  $ns attach-agent $n2 $udp
  set null [new Agent/Null]
  $ns attach-agent $n3 $null
  $ns connect $udp $null
  $udp set fid_ 3

  #Setup a CBR over UDP connection
  set cbr [new Application/Traffic/CBR]
  $cbr attach-agent $udp
  $cbr set type_ CBR
  $cbr set packet_size_ 500
  $cbr set rate_ $cbr_rate
  #$cbr set random_ false
#############################################


  # Schedule start/stop times
  $ns at 0.0   "$cbr start"
  $ns at 0.2   "$ftp1 start"
  $ns at 0.2   "$ftp2 start"
  $ns at 30.0   "$ftp2 stop"
  $ns at 30.0   "$ftp1 stop"
  $ns at 32.0   "$cbr stop"

  # Set simulation end time
  $ns at 31.0 "finish"


  ##################################################
  ## Obtain Trace date at destination (n4)
  ##################################################

  # Run simulation !!!!
  $ns run


