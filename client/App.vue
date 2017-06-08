<template>
  <div>
    <div v-on:click="menu_options.show = false">
      <navbar :active="active" v-on:setActive="setActiveTab"></navbar>
      <div class="columns is-gapless">
        <div class="column is-narrow hero is-fullheight">
          <scan-button :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></scan-button>
          <module-menu :modules="modules">
          </module-menu>
        </div>
        <div class="column">
          <div class="columns is-gapless" v-if="has_results">
            <template v-if="isActiveTab('results')">
              <node-table :results="results" class="column hero is-fullheight is-scrollable" :contextmenu="contextmenu"></node-table>
              <node-graph :results="results" class="column hero is-fullheight" :contextmenu="contextmenu"></node-graph>
            </template>
          </div>
          <template v-if="isActiveTab('console')">
            <console :results="results" :console_output="console_output" class="column is-12"></console>
          </template>
        </div>
      </div>
    </div>
    <contextmenu :results="results" :modules="modules" :menu_options="menu_options"></contextmenu>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable, ModuleMenu, ContextMenu, ScanButton, Console } from './components/'
var merge = require('deepmerge');

  export default {
    data: function() {
      // app data
      return {
        scanning: false,
        results: {},
        results_raw: [],
        modules: [],
        active: 'results',
        console_output: [],
        menu_options: {
          x: "0px",
          y: "0px",
          ip: "",
          show: false
        }
      }
    },
    // register components with the vue instance
    components: {
      navbar: Navbar,
      console: Console,
      'scan-button': ScanButton,
      'node-graph': NodeGraph,
      'node-table': NodeTable,
      'module-menu': ModuleMenu,
      'contextmenu': ContextMenu
    },
    // dynamic properties
    computed: {
      has_results: function() {
        return Object.keys(this.results).length > 0;
      }
    },
    mounted: function() {
      this.getModules();
      this.initSockets();
    },
    // instance methods
    methods: {
      // deep merge two json objects on IP
      mergeResult: function(data) {
        this.results_raw.push(data);
        if(data) {
          if(data.ip in this.results) {
            this.$set(this.results, data.ip, merge(this.results[data.ip], data));
          } else {
            this.$set(this.results, data.ip, data);
          }
        }
      },
      // start the scan
      startScan: function() {
        this.scanning = true;
        this.results = {};
        this.results_raw = [];
        this.logMessage('Initializing sniffer...')
        utils.socket.emit('sniffer_init', {});
        this.logMessage('Sniffer initialized, beginning scan.')
        utils.socket.emit('start_scan', {});
      },
      // stop the scan
      stopScan: function() {
        this.scanning = false
        this.logMessage('Sniffer stopped.')
        utils.socket.emit('sniffer_kill', {});
      },
      setActiveTab: function(tab) {
        // change tabs 
        this.active = tab;
      },
      // check if the current tab is the active tab
      isActiveTab: function(tab) {
        return this.active === tab;
      },
      // remove .local from the names - should move this to server-side?
      formatName: function(name) {
        return name.replace(/\.local\./g, "");
      },
      // log a message to the console with the current time
      logMessage: function(msg) {
        msg = {log: msg}
        msg.timestamp = new Date().toISOString()
        this.console_output.push(msg)
      },
      // load modules via WS
      getModules: function() {
        var _this = this;
        utils.socket.on('get_mods', function(msg){
          _this.modules = JSON.parse(msg);
          _this.logMessage('Modules loaded: ['+ _this.modules.map(function(obj){ return obj.modname }).join(", ") +"]")
        });
        utils.socket.emit('get_mods');
      },
      // init the websocket listeners
      initSockets: function() {
        var _this = this;
        utils.socket.on('icmp_echo_result', function(msg) {
          _this.mergeResult(msg);
        });
        utils.socket.on('icmp_name_result', function(msg) {
          _this.mergeResult(msg);
        });
        utils.socket.on('multicast_result', function(msg) {
          utils.socket.emit('scan_llmnr', msg);
          _this.mergeResult(msg);
        });
        utils.socket.on('mdns_result', function(msg) {
          _this.mergeResult(msg);
        });
        utils.socket.on('llmnr_result', function(msg) {
          _this.mergeResult(msg);
        });

        // mod handlers
        utils.socket.on('module_output', function(msg) {
          if(msg.log) {
            msg.timestamp = new Date().toISOString()
            _this.console_output.push(msg)
          }
        });
        utils.socket.on('module_merge', function(msg) {
          _this.mergeResult(msg);
        })
      },
      // set the right click menu
      contextmenu: function(ip, x, y) {
        this.menu_options.show = false;
        this.menu_options = {
          x: x,
          y: y,
          ip: ip,
          show: true
        }
      }
    }
  }
</script>

<style type="css">
  html { overflow-x: auto; }

  .hero.is-fullheight { min-height: 92.7vh!important; }
  .hero.is-fullheight.is-scrollable {
    height: 92.7vh!important;
    overflow: scroll;
  }
</style>
