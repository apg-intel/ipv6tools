<template>
  <div>
    <table id="nodetable" class="table">
      <thead>
        <tr>
          <th>Details</th>
          <th>IP Address</th>
          <th>MAC Address</th>
          <th>Device Name</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="result in results_arr" :result="result">
          <tr v-on:contextmenu.prevent="rightclick(result.ip, $event)" class="clickable-row">
            <td v-if="result.dns_data" :title="JSON.stringify(result.dns_data)">
              <a href="#" v-on:click.prevent="show(result.ip)">
                <i class="fa" :class="{'fa-chevron-up': isShown(result.ip), 'fa-chevron-down': !isShown(result.ip)}" aria-hidden="true"></i>
              </a>
            </td>
            <td v-else></td>
            <td>{{result.ip}}</td>
            <td>{{result.mac}}</td>
            <td>{{result.device_name}}</td>
          </tr>
          <tr v-if="showDetails.indexOf(result.ip) >= 0">
            <td colspan="5">
            <table class="table">
              <thead>
                <tr>
                  <th>isAnswer</th>
                  <th>answer_data</th>
                  <th>answer_type</th>
                  <th>answer_name</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in result.dns_data">
                  <td>{{result.isAnswer}}</td>
                  <td>{{result.answer_data}}</td>
                  <td>{{result.answer_type}}</td>
                  <td>{{result.answer_name}}</td>
                </tr>
              </tbody>
            </table>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    asdf: {{results_arr.map(function(obj){ return obj.device_name })}}
  </div>
</template>

<script>
  export default {
    props: {
      results: Object,
      contextmenu: Function
    },
    data: function() {
      return {
        showDetails: []
      }
    },
    computed: {
      results_arr: function() {
        return Object.values(this.results).sort(function(a,b){
          return (b.device_name || '').localeCompare(a.device_name || '');
        })
      }
    },
    methods: {
      isShown: function(ip) {
        return this.showDetails.indexOf(ip) >= 0;
      },
      show: function(ip) {
        console.log(this.showDetails)
        if(this.isShown(ip)) {
          this.showDetails.splice(this.showDetails.indexOf(ip), 1)
        } else {
          this.showDetails.push(ip)
        }
      },
      rightclick: function(ip, event) {
        this.contextmenu(ip, event.pageX, event.pageY);
      }
    }
  }
</script>

<style type="text/css">
  tr.clickable-row {
    cursor: pointer;
  }
</style>