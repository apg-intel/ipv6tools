# IPv6 Validation Toolkit

The IPv6 Validation Toolkit is a framework containing a set of modules used to test and validate a network of IPv6-capable devices.

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

## Usage

1. Run `$ sudo python server.py`
2. Navigate to [http://localhost:5000](http://localhost:5000) in a Chrome web browser

## Modules

Modules are classes that allow interaction with individual nodes or all nodes. These show up as a right click option on each node, or as a button below the graph.

### Included Modules

Included in the project are a couple of modules to help validate your network, as well as use as examples for your own modules.

**TODO** write descriptions for these modules
* **poisonLLMNR**
* **CVE-2016-1879**

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
