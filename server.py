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

@app.route('/scan')
def scan():
  return render_template('show_node_names.html')



# socket events
@socketio.on('start_scan', namespace='/scan')
def scan(message):
  a = icmpv6.ICMPv6()
  aa = dns.DNS()
  all_nodes = a.echoAllNodes()
  emit('scan_results', {'data': all_nodes, 'name': 'all_nodes'})

  dns_query = Counter(aa.mDNSQuery())
  emit('scan_results', {'data': dns_query, 'name': 'dns_query'})

  node_names = a.echoAllNodeNames()
  emit('scan_results', {'data': node_names, 'name': 'node_names'})





  b = merge(all_nodes,node_names)
  b = merge(b,dns_query)

  keylist = []
  for x in b:
      keylist.append(x)

  dig = aa.dig_and_listen(keylist)
  b = merge(b,dig)
  entries = convertToList(b)

  emit('scan_results', {'data': entries, 'name': 'entries'})

if __name__ == '__main__':
    socketio.run(app)