<template>
  <div>
    <navbar :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></navbar>
    <div v-if="has_results">
      <section class="section">
        <div class="columns">
          <!-- <node-graph :results="results" class="column is-6"></node-graph> -->
          <node-table :results="results" class="column is-12"></node-table>
        </div>
      </section>
      <div class="columns">
        <section class="column is-6">
          <h1 class="title is-5">Processed Results</h1>
          <pre><code class="json">{{results}}</code></pre>
        </section>
        <section class="column is-6">
          <h1 class="title is-5">Raw Results</h1>
          <pre><code class="json">{{results_raw}}</code></pre>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable } from './components/'
var merge = require('deepmerge')
var io = require('socket.io-client')

var namespace = '/scan'; // change to an empty string to use the global namespace
var socket = io.connect('http://' + document.domain + ':8081' + namespace);

  export default {
    data: function() {
      return {
        scanning: false,
        results: {},
        results_raw: []
      }
    },
    components: {
      navbar: Navbar,
      'node-graph': NodeGraph,
      'node-table': NodeTable
    },
    computed: {
      has_results: function() {
        return Object.keys(this.results).length > 0
      }
    },
    mounted: function() {
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
          console.log(msg)
        }
      });

      socket.on('module_merge', function(msg) {
        _this.mergeResult(msg)
      })
    },
    methods: {
      mergeResult: function(data) {
        this.results_raw.push(data)
        if(data) {
          if(data.ip in this.results) {
            this.$set(this.results, data.ip, merge(this.results[data.ip], data))
          } else {
            this.$set(this.results, data.ip, data)
          }
        }
      },
      startScan: function() {
        this.scanning = true
        this.results = {}
        this.results_raw = []
        socket.emit('sniffer_init', {})
        socket.emit('start_scan', {})
      },
      stopScan: function() {
        this.scanning = false
        socket.emit('sniffer_kill', {});
      },
      formatName: function(name) {
        return name.replace(/\.local\./g, "");
      }
    }
  }
</script>
