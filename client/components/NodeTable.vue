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
        <tr v-for="result in results" :result="result">
          <td v-if="result.dns_data" :title="JSON.stringify(result.dns_data)"><i class="fa fa-chevron-down" aria-hidden="true"></i></td>
          <td v-else></td>
          <td>{{result.ip}}</td>
          <td>{{result.mac}}</td>
          <td>{{result.device_name}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
  export default {
    props: {
      'results': Array
    }
  }
</script>