<template>
  <div>
    <table id="nodetable" class="table">
      <thead>
        <tr>
          <td colspan="6">
            <input class="input" type="text" placeholder="Search..." v-model="search">
          </td>
        </tr>
        <tr>
          <th>Details</th>
          <th>
            <a @click="sortBy('ip')" :class="{active: sortKey == 'ip'}">
              IP Address
              <span class="icon is-small" v-if="sortKey == 'ip'"><i class="fa" :class="{'fa-chevron-up': reverse, 'fa-chevron-down': !reverse}"></i></span>
            </a>
          </th>
          <th>
            <a @click="sortBy('mac')" :class="{active: sortKey == 'mac'}">
              MAC Address
              <span class="icon is-small" v-if="sortKey == 'mac'"><i class="fa" :class="{'fa-chevron-up': reverse, 'fa-chevron-down': !reverse}"></i></span>
            </a>
          </th>
          <th>
            <a @click="sortBy('device_name')" :class="{active: sortKey == 'device_name'}">
              Device Name
              <span class="icon is-small" v-if="sortKey == 'device_name'"><i class="fa" :class="{'fa-chevron-up': reverse, 'fa-chevron-down': !reverse}"></i></span>
            </a>
          </th>
          <th>
            <a @click="sortBy('services')" :class="{active: sortKey == 'services'}">
              Services
              <span class="icon is-small" v-if="sortKey == 'services'"><i class="fa" :class="{'fa-chevron-up': reverse, 'fa-chevron-down': !reverse}"></i></span>
            </a>
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-for="result in results_arr" :result="result">
          <tr v-on:contextmenu.prevent="rightclick(result.ip, $event)" class="clickable-row">
            <td v-if="result.dns_data || result.multicast_report" :title="JSON.stringify(result.multicast_report)+JSON.stringify(result.dns_data)">
              <a href="#" v-on:click.prevent="show(result.ip)">
                <i class="fa" :class="{'fa-chevron-up': isShown(result.ip), 'fa-chevron-down': !isShown(result.ip)}" aria-hidden="true"></i>
              </a>
            </td>
            <td v-else></td>
            <td>{{result.ip}}</td>
            <td>{{result.mac}}</td>
            <td>{{result.device_name}}</td>
            <td>{{result.services}}</td>
          </tr>
          <tr v-if="showDetails.indexOf(result.ip) >= 0">
            <td colspan="5">
              <table class="table detail-table" v-if="result.dns_data">
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
              <table class="table" v-if="result.multicast_report">
                <thead>
                  <tr>
                    <th>multicast_address</th>
                    <th>record_type</th>
                    <th>service</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="result in result.multicast_report">
                    <td>{{result.multicast_address}}</td>
                    <td>{{result.record_type}}</td>
                    <td>{{result.service}}</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
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
        showDetails: [],
        sortKey: 'device_name',
        reverse: false,
        search: ''
      }
    },
    computed: {
      results_values: function() {
        let _this = this;
        return Object.keys(this.results).map(function(key){ return _this.results[key]; })
      },
      results_arr: function() {
        let _this = this;
        let arr = _this.results_values.sort(function(a,b){
          if ((!a[_this.sortKey]) && (!b[_this.sortKey]))
            return 0;
          else if (!a[_this.sortKey])
            return 1;
          else if (!b[_this.sortKey])
            return -1;
          return (a[_this.sortKey]).localeCompare(b[_this.sortKey]);
        });
        if(_this.reverse)
          arr = arr.reverse();
        if(_this.search.length >= 2) {
          arr = arr.filter(function(result) {
            return (new RegExp(_this.search, "i")).test(JSON.stringify(_this.results_values));
          })
          console.log(arr);
        }
        return arr;
      }
    },
    methods: {
      isShown: function(ip) {
        return this.showDetails.indexOf(ip) >= 0;
      },
      show: function(ip) {
        if(this.isShown(ip)) {
          this.showDetails.splice(this.showDetails.indexOf(ip), 1)
        } else {
          this.showDetails.push(ip)
        }
      },
      rightclick: function(ip, event) {
        this.contextmenu(ip, event.pageX, event.pageY);
      },
      sortBy: function(sortKey) {
        this.reverse = (this.sortKey == sortKey) ? ! this.reverse : false;
        this.sortKey = sortKey;
      }
    }
  }
</script>

<style type="text/css">
  tr.clickable-row {
    cursor: pointer;
  }

  th > a {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;

  }

  th > a.active {
    color: #3273dc;
  }

  table.detail-table td {
    word-break: break-word;
  }
</style>
