<template>
  <div>
    <navbar :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></navbar>
    <section class="section" v-if="results">
      <div class="columns">
        <!-- <node-graph :results="results" class="column is-6"></node-graph> -->
        <node-table :results="results" class="column is-12"></node-table>
      </div>
    </section>
    <div class="columns">
      <section v-if="results" class="column is-6">
        <h1 class="title is-5">Processed Results</h1>
        <pre><code class="json">{{results}}</code></pre>
      </section>
      <section v-if="results_raw.length" class="column is-6">
        <h1 class="title is-5">Raw Results</h1>
        <pre><code class="json">{{results_raw}}</code></pre>
      </section>
    </div>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable } from './components/'

var merge = require('deepmerge')

// import websockets
var io = require('socket.io-client')
var namespace = '/scan'; // change to an empty string to use the global namespace
var socket = io.connect('http://' + document.domain + ':8081' + namespace);

  export default {
    data: function() {
      return {
        scanning: false,
        results: false,
        results_raw: []
      }
    },
    components: {
      navbar: Navbar,
      'node-graph': NodeGraph,
      'node-table': NodeTable
    },
    mounted: function(){
      var _this = this;
      socket.on('icmp_echo_result', function(msg){
        _this.addOrUpdateResult(msg);
      });
      socket.on('icmp_name_result', function(msg){
        _this.addOrUpdateResult(msg);
      });
      socket.on('multicast_result', function(msg){
        socket.emit('scan_llmnr', msg);
        _this.addOrUpdateResult(msg);
      });
      socket.on('mdns_result', function(msg){
        _this.addOrUpdateResult(msg);
      });
      socket.on('llmnr_result', function(msg){
        _this.addOrUpdateResult(msg);
      });
      // socket handlers
      socket.on('module_output', function(msg) {
        if(msg.log){
          console.log(msg)
        }
      });
    },
    methods: {
      addOrUpdateResult: function(data){
        this.results_raw.push(data)
        if(data){
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
      formatName: function(name){
        return name.replace(/\.local\./g, "");
      }
    }
  }
</script>
