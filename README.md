# CS 176B Project
FTP Server/Client
-----------------

Please see our docs for more information

By: Ben Patient, Danish Vaid, Jake Can

How to Run
----------
Currently the execution of our program is fairly simple, within 5 seconds you must run the following 2 commands in 2 terminals (in the `src` directory) and the test data file will be transferred:
1. `./run -s`
2. `./run -c`

Once the server and client have connected, you can upload the test file by typing `upload` client's console.
The program so far tests with reading in "test.txt" and transferring to the server, where the server then writes out "received_test.txt" on the server side. We are working on building out the logic for the commands and did not want to include broken code in our submission.