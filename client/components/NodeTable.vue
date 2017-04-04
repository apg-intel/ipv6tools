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
              <a href="#" v-on:click.prevent="show(result.ip)">
                <i class="fa" :class="{'fa-chevron-up': isShown(result.ip), 'fa-chevron-down': !isShown(result.ip)}" aria-hidden="true"></i>
              </a>
            </td>
            <td v-else></td>
            <td>{{result.ip}}</td>
            <td>{{result.mac}}</td>
            <td>{{result.device_name}}</td>
          </tr>
          <tr v-if="showDetails.includes(result.ip)">
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
                <tr>
                  <td>{{}}</td>
                </tr>
              </tbody>
            </table>
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
        showDetails: []
      }
    },
    methods: {
      isShown: function(ip) {
        return this.showDetails.includes(ip);
      },
      show: function(ip) {
        console.log(this.showDetails)
        if(this.isShown(ip)) {
          this.showDetails.splice(this.showDetails.indexOf(ip), 1)
        } else {
          this.showDetails.push(ip)
        }
      }
    }
  }
</script>