# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import icmpv6
import dns
from collections import Counter
from operator import add

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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

@app.route('/')
def show_entries():
    a = icmpv6.ICMPv6()
    aa = dns.DNS()
    all_nodes = a.echoAllNodes()
    dns_query = Counter(aa.mDNSQuery())
    node_names = a.echoAllNodeNames()
    b = merge(all_nodes,node_names)
    b = merge(b,dns_query)

    keylist = []
    for x in b:
        keylist.append(x)

    dig = aa.dig_and_listen(keylist)
    b = merge(b,dig)
    entries = convertToList(b)
    print entries
    return render_template('show_node_names.html', entries=entries)

@app.route('/node/<ipv6>')
def node(ipv6=None):
    return

if __name__ == '__main__':
    app.run()
