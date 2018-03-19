
# CS 176B Project: FTP Server/Client

----------

Please see our docs for our reports
By: Ben Patient, Danish Vaid, Jake Can

### How to Run
--------------------
Currently the execution of our program is fairly simple, within 5 seconds you must run the following 2 commands in 2 terminals (in the \`src\` directory) and the avaliable commands for client:
1.  `./run -s`
2.  `./run -c`


Once the server and client have connected, you can see the commands avaliable to the client and use our FTP program to its potential.

### File Structure
-----------------------

```
client_home/ (directory) * Client's starting directory *

server_home/ (directory) * Server's starting directory *

docs/ (directory)
	deliverable_a.pdf
	deliverable_b.pdf
	final_report.pdf

submissions/ (directory)
	deliverable_a.pdf
	deliverable_a_submission.png
	ftpxpress_delv_b.zip

src/ (directory)
	client_pkg/ (directory)
		client.py
		communication.py
		
	server_pkg/ (directory)
		server.py
		message_queue.py
		connection_handler.py
	shared/ (directory)
		connection.py
		directory.py
		files.py
		packets.py
```

  

### Code Breakdown

---------------------------

##### client.py:

This class handles connecting to the server. It is the highest level class so it contains all relevant objects like Communication. Sequentially, the Client class makes the connection to the server, allows the user to enter commands, processes the commands, and terminates connections when the user is done issuing commands.

  

##### communication.py:

This class handles all of the communication between the client and the server. Within this class, the user can input commands and the class has branching logic to decide what action to take based off of what command. Because of our structural decisions, this class handles sending and receiving messages over the network, so the communication must be sequential, meaning the class will be blocking when it is expecting to receive messages.

  

##### server.py:

This class is the server side equivalent of client.py. It handles accepting the connection from the client side. Just like the Client class, sequentially, it makes the connection, initializes a message queue, starts receiving messages, and closes all socket connections when the session is over.

  

##### message_queue.py:

This class manages all incoming packets. It is used to take in the data stream, deserialize into a Packet object, and then send it off to the ConnectionHandler object to process the packet.

  

##### connection_handler.py:

This class manages responding to packets sent by the client. By nature, it is reactive in the sense that it never acts by itself, and only acts when a packet is received. Data streams are never received here, but the Packet objects are passed down to this class by the MessageQueue object. The main branching logic in this class is deciding what type of packet is received, and to respond accordingly, whether it is updating the state of the server, or responding back to the client side.

  

##### connection.py:

This file is for socket connection utility and contains various functions for creating sockets and accepting connections to a socket. This also contains a utility function to close connections to ensure that the sockets are closed before we want to terminate our program.

  

##### directory.py:

This class is used to handle traversing through and showing information in the directory structure. Bash commands like 'ls', 'cd', and 'pwd' are implemented so the user can navigate around and look for desired files to transfer.

  

##### files.py:

This class is used for reading and writing to a file. It is mostly meant for modularizing our code and keep states on which chunks of data to read and write to on the specified files.

  

##### packets.py:

This file contains multiple classes, one for each type of packet, as well as a few utility functions for interpreting data streams into Packet objects. Each type of Packet object has its member variables to handle various information on commands and file transfers. Each type also includes a serialize function to convert the object into a data stream that can be sent through the socket connections.