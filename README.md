## Dependencies

- python 2.7
- python pip
- scapy (pip install)
- ~~dnslib (pip install)~~ No longer needed using built in scapy DNS parsing
- flask (pip install)
- netifaces (pip install) --hopefully we don't need this for too long
- Flask-SocketIO
- gevent-websocket -- for Flask-SocketIO

## How to run

$ sudo python server.py


### Other Notes

The main HTML files are in the templates directory.
You can probably even delete some of the files in there that aren't needed
