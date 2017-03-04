UNI : zx1298

RUN COMMAND:
  Server: python UdpClient.py -s 1024
  Client: python UdpClient.py -c xzk 127.0.0.1 1024 2000
  
The program runs as the spec.
The basic algorithm is to use a daemon thread to listen packet
When we want to send a packet, we create a new thread to send and then end the thread.
