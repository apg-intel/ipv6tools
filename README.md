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

## Installation

1. `$ git clone http://github.com/ronmajic/ipv6tools.git`
2. `$ sudo pip install -r requirements.txt`
3. `$ sudo npm install`

## Usage

### Web client - dev
1. Run `$ npm run dev`
2. Navigate to [http://localhost:8080](http://localhost:8080) in a Chrome web browser

### Web client - prod

### CLI

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
    self.socket_log('Running DoS on '+target['ip'])

```

## Known Issues

* Not compatible with Firefox or IE
* Untested on large networks
