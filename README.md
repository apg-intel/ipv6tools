# IPv6 Validation Toolkit

The IPv6 framework is a robust set of modules and plugins that allow a user to audit an IPv6 enabled network.  The built-in modules support enumeration of IPv6 features such as ICMPv6 and Multicast Listener Discovery (MLD).  In addition, the framework also supports enumeration of Upper Layer Protocols (ULP) such as multicast DNS (mDNS) and Link-Local Multicast Name Resolution (LLMNR).  Users can easily expand the capability of the framework by creating plugins and modules in the Python language.

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Modules](#modules)
* [Known Issues](#known-issues)

## Requirements

* python 2.7
* pip
* npm [development only]

## Installation

### Standard

*[Optional] Use a virtualenv for installation:* `virtualenv venv && source venv/bin/activate`

1. `git clone http://github.com/ronmajic/ipv6tools.git`
2. `sudo pip install -r requirements.txt`


### Development
1. `git clone http://github.com/ronmajic/ipv6tools.git`
2. `git checkout dev`
3. `npm run setup`

## Usage

### Standard
1. `sudo python app.py`
2. Navigate to [http://localhost:8080](http://localhost:8080) in a web browser

### Development
1. Run `$ npm run serve`
2. In a separate terminal, run `npm run dev`
3. Navigate to [http://localhost:8081](http://localhost:8081) in a web browser

### CLI
**TODO**

## Modules

Modules are classes that allow interaction with individual nodes or all nodes. These show up as a right click option on each node, or as a button below the graph.

### Included Modules

Included in the project are a couple of modules to help validate your network, as well as use as examples for your own modules.

* **poisonLLMNR** - Link-Local Multicast Name Resolution is the successor of of NBT-NS, which allows local nodes to resolve names and IP addresses.  Enabling this module poisons LLMNR queries to all nodes on the local link.
* **CVE-2016-1879** - The following CVE is a vulnerability in SCTP that affects FreeBSD 9.3, 10.1 and 10.2.  Enabling this module will launch a crafted ICMPv6 packet and potentially cause a DoS (assertion failure or NULL pointer dereference and kernel panic) to a single node.

### Custom Modules

All modules are located in `/modules` and are automatically loaded when starting the server. Included in `/modules` is a file called `template.py`. This file contains the class that all modules must extend in order to display correctly and communicate with the webpage.

Use this template to build a custom module

```python
from template import Template

class IPv6Module(Template):

  def __init__(self, socketio, namespace):
    super(IPv6Module, self).__init__(socketio, namespace)
    self.modname = "CVE-2016-1879"
    self.menu_text = "FreeBSD IPv6 DoS"
    self.actions = [
      {
        "title": "FreeBSD IPv6 DoS", #name that's displayed on the buttons/menu
        "action": "action", #method name to call
        "target": True #set this to true to display it in the right-click menu
      }
    ]

  def action(self, target=None):
    # send a log msg
    self.socket_log('Running DoS on '+target['ip'])
    
    # do stuff, etc

    # merge results with main result set
    listOfDicts = [{ip: '::1', device_name: 'test'}]
    self.module_merge(listOfDicts)

```

## Known Issues

* Untested on large networks
* Any stack traces mentioning `dnet` or `dumbnet` - follow the instructions below.
* Some operating systems may require the libpcap headers. See notes below.

### Installing libdnet
```
wget http://libdnet.googlecode.com/files/libdnet-1.12.tgz
tar xfz libdnet-1.12.tgz
./configure
make
sudo make install
cd python
python setup.py install
```

### libpcap headers in Ubuntu
`sudo apt install libpcap-dev`