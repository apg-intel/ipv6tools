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
          <td><i class="fa fa-chevron-down" aria-hidden="true"></i></td>
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