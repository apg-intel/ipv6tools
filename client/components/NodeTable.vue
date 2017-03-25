<template>
  <div>
    <table class="table">
      <thead>
        <tr>
          <th>Details</th>
          <th>IP Address</th>
          <th>MAC Address</th>
          <th>Device Name</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="result in results" :result="result">
          <tr>
            <td v-if="result.dns_data" :title="JSON.stringify(result.dns_data)">
              <a href="#" v-on:click="show(result.ip)">
                <i class="fa fa-chevron-down" aria-hidden="true"></i>
              </a>
            </td>
            <td v-else></td>
            <td>{{result.ip}}</td>
            <td>{{result.mac}}</td>
            <td>{{result.device_name}}</td>
          </tr>
          <tr v-if="showDetails==result.ip">
            <td colspan="5">
              <pre><code class="json">{{result.dns_data}}</code></pre>
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
      'results': Object
    },
    data: function() {
      return {
        showDetails: false
      }
    },
    methods: {
      show: function(ip) {
        if(this.showDetails == ip) {
          this.showDetails = false
        } else {
          this.showDetails = ip
        }
      }
    }
  }
</script>