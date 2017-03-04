UNI : zx1298

RUN COMMAND:
  Server: python UdpClient.py -s 1024
  Client: python UdpClient.py -c xzk 127.0.0.1 1024 2000
  
The program runs as the spec.
The basic algorithm is to use a daemon thread to listen packet
When we want to send a packet, we create a new thread to send and then end the thread.


Example:

Client xzk:
uestcxzk@instance-w4119:~/UpdChat$ python UdpClient.py -c xzk 127.0.0.1 1024 2000
>>>  
>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>  
>>> [Client table update.]
>>> dereg xzkresgsd
 
>>> [msg invalid]
>>> dereg xzk

>>> [Your are Offline. Bye.]
>>> reg dfgdsfgs

>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>           
>>> [Client table update.]
>>> dereg dfgdsfgs
 
>>> [Your are Offline. Bye.]
>>> reg xzk

>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>  
>>> [Sat Mar  4 08:18:52 2017] tty: sdfdsg

>>> send tty aaaaa
 
>>> [Message received by tty.]

>>>  
>>> tty: fffff
>>> dereg tty
 
>>> [msg invalid]
>>> dereg xzk

>>> [Your are Offline. Bye.]
>>> reg xzk

>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>  
>>> [Sat Mar  4 08:19:43 2017] tty: asdfsdfds
>>> dereg xzk
 
>>> [Your are Offline. Bye.]
------------------------------------------------------------------
Client tty:

>>>  
>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>  
>>> xzk: adsfdgsterghsrthsrths
>>> send xzk sfsdgsergrses
 
>>> [Message received by xzk.]

>>>  send adsfas

>>> [msg invalid]
>>> 
>>> [Client table update.]
>>> ^C 
>>> [Server not responding]

>>> [Exiting]
uestcxzk@instance-w4119:~/UpdChat$ python UdpClient.py -c tty 127.0.0.1 1024 2002

>>>  
>>> 
>>> [Welcome, You are registered.]
>>>  
>>> [Client table update.]
>>>  
>>> [Client table update.]
>>>  
>>> [Client table update.]
>>> send xzk sdfdsg
 
>>> [xzk is offline, message sent to server.]
>>>  
>>> [Client table update.]
>>>  
>>> [Messages received by the server and saved]
>>>  
>>> [Client table update.]
>>>  
>>> [Client table update.]
>>>  
>>> xzk: aaaaa
>>> send xzk fffff
 
>>> [Message received by xzk.]

>>>  
>>> [Client table update.]
>>> send xzk asdfsdfds
 
>>> [xzk is offline, message sent to server.]
>>>  
>>> [Client table update.]
>>>  
>>> [Messages received by the server and saved]
>>>  
>>> [Client table update.]
>>>                             <-server is closed at this time
>>> [Client table update.]
>>> send xzk sdgsergr
 
>>> [xzk is offline, message sent to server.]
>>>  
>>> [Server not responding]

>>> [Exiting]
