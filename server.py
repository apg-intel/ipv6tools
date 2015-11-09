from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
import icmpv6
import dns
from collections import Counter
from operator import add


PROPAGATE_EXCEPTIONS = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def convertToList(entryDict):
    returnList = []
    for key in entryDict.keys():
        newDict = {}
        newDict["ip"] = key
        newDict["mac"] = entryDict[key]["mac"]
        if "device_name" in entryDict[key]:
            newDict["device_name"] = entryDict[key]["device_name"]
        if "dns_data" in entryDict[key]:
            newDict["dns_data"] = entryDict[key]["dns_data"]
        returnList.append(newDict)
    return returnList

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


# flask routes
@app.route('/')
def index():
  return render_template('index.html')


# socket events
@socketio.on('start_scan', namespace='/scan')
def scan(message):
  handler = icmpv6.ICMPv6()
  all_nodes = handler.echoAllNodes()
  node_names = handler.echoAllNodeNames()
  res = merge(all_nodes,node_names)
  emit('icmp_results', {'data': res, 'asdf': node_names})


@socketio.on('scan_dns', namespace='/scan')
def scan_dns(message):
  handler = dns.DNS()
  dns_query = Counter(handler.mDNSQuery())
  emit('dns_results', {'data': dns_query})

@socketio.on('dig_listen', namespace='/scan')
def dig_listen(message):
  handler = dns.DNS()
  dig = handler.dig_and_listen(message['ips'])
  emit('dig_results', {'data': dig})


if __name__ == '__main__':
    socketio.run(app)
