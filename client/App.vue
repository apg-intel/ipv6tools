<template>
  <div>
      <navbar :scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></navbar>
      <section class="section" v-if="results.length">
        <div class="columns">
          <!-- <node-graph :results="results" class="column is-6"></node-graph> -->
          <node-table :results="results" class="column is-12"></node-table>
        </div>
      </section>
  </div>
</template>

<script>
import { Navbar, NodeGraph, NodeTable } from './components/'

  export default {
    data: function() {
      return {
        scanning: false,
        results: []
      }
    },
    components: {
      navbar: Navbar,
      'node-graph': NodeGraph,
      'node-table': NodeTable
    },
    methods: {
      generateFakeResults: function() {
        function genMAC(){
            var hexDigits = "0123456789ABCDEF";
            var macAddress = "";
            for (var i = 0; i < 6; i++) {
                macAddress+=hexDigits.charAt(Math.round(Math.random() * 15));
                macAddress+=hexDigits.charAt(Math.round(Math.random() * 15));
                if (i != 5) macAddress += ":";
            }

            return macAddress;
        }
        let res = []
        for(let i = 0; i < 15; i++){
          let n = Math.floor(Math.random()*255);
          res.push({ip: '192.168.1.'+n, mac: genMAC(), device_name: 'test-macbook-'+n, dns_data: [], multicast_report: []})
        }
        return res
      },
      startScan: function() {
        this.scanning = true
        this.results = this.generateFakeResults()
        console.log('scanning!')
      },
      stopScan: function() {
        this.scanning = false
        console.log('Stop scanning...')
      }
    }
  }
</script>