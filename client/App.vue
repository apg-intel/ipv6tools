<template>
  <div>
      <navbar :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></navbar>
      <section class="section" v-if="results.length">
        <div class="columns">
          <!-- <node-graph :results="results" class="column is-6"></node-graph> -->
          <node-table :results="results" class="column is-12"></node-table>
        </div>
      </section>
      <section v-if="results_raw.length">
        <pre>
          <code class="json">{{results_raw}}</code>
        </pre>
      </section>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable } from './components/'

// import websockets
var io = require('socket.io-client')
var namespace = '/scan'; // change to an empty string to use the global namespace
var socket = io.connect('http://' + document.domain + ':8081' + namespace);

  export default {
    data: function() {
      return {
        scanning: false,
        results: [],
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
        var ipMatch = function(obj){
          return obj.ip === data.ip
        }
        if(data){
          var obj = this.results.filter(ipMatch)[0]
          if(obj){
            this.results.filter(ipMatch)[0] = Object.assign(obj, data); //merged new
          } else {
            this.results.push(data)
          }
        }
      },
      startScan: function() {
        this.scanning = true
        this.results = []
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
