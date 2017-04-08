<template>
  <div>
    <navbar :active="active" v-on:setActive="setActiveTab"></navbar>
    <div class="columns">
      <div class="column is-2">
        <scan-button :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></scan-button>
        <module-menu :modules="modules">
        </module-menu>
      </div>
      <div class="column is-10">
        <div v-if="has_results">
          <section class="section" v-if="isActiveTab('table')">
            <div class="columns">
              <!-- <node-graph :results="results" class="column is-6"></node-graph> -->
              <node-table :results="results" class="column is-12"></node-table>
            </div>
          </section>
          <section class="section" v-if="isActiveTab('json')">
            <div class="columns">
              <div class="column is-6">
                <h1 class="title is-5">Processed Results</h1>
                <pre><code class="json">{{results}}</code></pre>
              </div>
              <div class="column is-6">
                <h1 class="title is-5">Raw Results</h1>
                <pre><code class="json">{{results_raw}}</code></pre>
              </div>
            </div>
          </section>
          <section class="section" v-if="isActiveTab('graph')">
            <h3 class="title is-3">Graph not yet implemented</h3>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable, ModuleMenu, ScanButton } from './components/'
var merge = require('deepmerge');
var io = require('socket.io-client');

var namespace = '/scan'; // change to an empty string to use the global namespace
var socket = io.connect('http://' + document.domain + ':8080' + namespace);

  export default {
    data: function() {
      return {
        scanning: false,
        results: {},
        results_raw: [],
        modules: [],
        active: 'table'
      }
    },
    components: {
      navbar: Navbar,
      'scan-button': ScanButton,
      'node-graph': NodeGraph,
      'node-table': NodeTable,
      'module-menu': ModuleMenu
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
        socket.emit('sniffer_init', {});
        socket.emit('start_scan', {});
      },
      stopScan: function() {
        this.scanning = false
        socket.emit('sniffer_kill', {});
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
      getModules: function() {
        var _this = this;
        socket.on('get_mods', function(msg){
          _this.modules = JSON.parse(msg);
        });
        socket.emit('get_mods');
      },
      initSockets: function() {
        var _this = this;
        socket.on('icmp_echo_result', function(msg) {
          _this.mergeResult(msg);
        });
        socket.on('icmp_name_result', function(msg) {
          _this.mergeResult(msg);
        });
        socket.on('multicast_result', function(msg) {
          socket.emit('scan_llmnr', msg);
          _this.mergeResult(msg);
        });
        socket.on('mdns_result', function(msg) {
          _this.mergeResult(msg);
        });
        socket.on('llmnr_result', function(msg) {
          _this.mergeResult(msg);
        });
        // socket handlers
        socket.on('module_output', function(msg) {
          if(msg.log) {
            console.log(msg);
          }
        });

        socket.on('module_merge', function(msg) {
          _this.mergeResult(msg);
        })
      }
    }
  }
</script>
