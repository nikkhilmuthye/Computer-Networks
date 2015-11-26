 #Make a NS simulator
  set ns [new Simulator]

  set tcp_type    [lindex $argv 0]
  set queue_type  [lindex $argv 1]
  set file_name   [lindex $argv 2]

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
  $ns duplex-link $n1 $n2   10Mb  2ms $queue_type
  $ns duplex-link $n2 $n3   10Mb  2ms $queue_type
  $ns duplex-link $n2 $n5   10Mb  2ms $queue_type
  $ns duplex-link $n3 $n4   10Mb  2ms $queue_type
  $ns duplex-link $n3 $n6   10Mb  2ms $queue_type

#############################################
  # Add a TCP sending module to node n1
  set tcp1 [new Agent/$tcp_type]
  $ns attach-agent $n1 $tcp1

  # Add a TCP receiving module to node n4
  set sink1 [new Agent/TCPSink]
  $ns attach-agent $n4 $sink1

  # Direct traffic from "tcp1" to "sink1"
  $ns connect $tcp1 $sink1

  # Setup a FTP traffic generator on "tcp1"
  set ftp1 [new Application/FTP]
  $ftp1 attach-agent $tcp1
  $ftp1 set class_ FTP

#############################################
  #Setup a UDP connection
  set udp [new Agent/UDP]
  $ns attach-agent $n5 $udp
  set null [new Agent/Null]
  $ns attach-agent $n6 $null
  $ns connect $udp $null
  $udp set fid_ 2

  #Setup a CBR over UDP connection
  set cbr [new Application/Traffic/CBR]
  $cbr attach-agent $udp
  $cbr set class_ CBR
  $cbr set packet_size_ 700
  $cbr set rate_ 7mb
  #$cbr set random_ false
#############################################


  # Schedule start/stop times
  $ns at 0.0   "$ftp1 start"
  $ns at 30.0   "$cbr  start"
  $ns at 120.0  "$ftp1 stop"
  $ns at 120.0  "$cbr  stop"

  # Set simulation end time
  $ns at 130.0 "finish"


  ##################################################
  ## Obtain Trace date at destination (n4)
  ##################################################

  # Run simulation !!!!
  $ns run


