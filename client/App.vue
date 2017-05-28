<template>
  <div>
    <div v-on:click="menu_options.show = false">
      <navbar :active="active" v-on:setActive="setActiveTab"></navbar>
      <div class="columns is-gapless">
        <div class="column is-narrow">
          <scan-button :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></scan-button>
          <module-menu :modules="modules">
          </module-menu>
        </div>
        <div class="column">
          <template v-if="has_results">
            <template v-if="isActiveTab('table')">
              <node-table :results="results" class="column is-12" :contextmenu="contextmenu"></node-table>
            </template>
            <template v-if="isActiveTab('graph')">
              <node-graph :results="results" class="column is-12" :contextmenu="contextmenu"></node-graph>
            </template>
          </template>
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
      return {
        scanning: false,
        results: {},
        results_raw: [],
        modules: [],
        active: 'table',
        console_output: [],
        menu_options: {
          x: "0px",
          y: "0px",
          ip: "",
          show: false
        }
      }
    },
    components: {
      navbar: Navbar,
      console: Console,
      'scan-button': ScanButton,
      'node-graph': NodeGraph,
      'node-table': NodeTable,
      'module-menu': ModuleMenu,
      'contextmenu': ContextMenu
    },
    computed: {
      has_results: function() {
        return Object.keys(this.results).length > 0;
      }
    },
    mounted: function() {
      this.getModules();
      this.initSockets();
    },
    methods: {
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
      startScan: function() {
        this.scanning = true;
        this.results = {};
        this.results_raw = [];
        this.logMessage('Initializing sniffer...')
        utils.socket.emit('sniffer_init', {});
        this.logMessage('Sniffer initialized, beginning scan.')
        utils.socket.emit('start_scan', {});
      },
      stopScan: function() {
        this.scanning = false
        this.logMessage('Sniffer stopped.')
        utils.socket.emit('sniffer_kill', {});
      },
      setActiveTab: function(tab) {
        this.active = tab;
      },
      isActiveTab: function(tab) {
        return this.active === tab;
      },
      formatName: function(name) {
        return name.replace(/\.local\./g, "");
      },
      logMessage: function(msg) {
        msg = {log: msg}
        msg.timestamp = new Date().toISOString()
        this.console_output.push(msg)
      },
      getModules: function() {
        var _this = this;
        utils.socket.on('get_mods', function(msg){
          _this.modules = JSON.parse(msg);
        });
        this.logMessage('Modules loaded.')
        utils.socket.emit('get_mods');
      },
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
</style>
