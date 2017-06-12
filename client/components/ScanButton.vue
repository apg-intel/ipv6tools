<template>
    <a class="button is-primary is-fullwidth" id="start-stop-scan" v-on:click.prevent="startStopScan" :class="{'scan-active': scanning}">
        <span class="icon">
            <i class="fa" :class="{'fa-spin': scanning, 'fa-circle-o-notch': scanning, 'fa-circle-o': !scanning}"></i>
        </span>
        <span v-if="scanning">Scanning</span>
        <span v-else>Scan</span>
    </a>
</template>

<script>
  export default {
    props: {
      'results': Array,
      'scanning': Boolean
    },
    methods: {
      startStopScan: function() {
          if(this.scanning) {
              this.$emit('stop')
          } else {
              this.$emit('start')
          }
      }
    }
  }
</script>

<style type="css">
  #start-stop-scan {
    border-radius: 0;
    padding: 35px 0;
  }
  .scan-active:hover {
      background-color: #ff3860!important;
  }
  .scan-active:hover span {
      display: none;
  }
  .scan-active:hover:before {
      content: 'Stop Scanning';
  }
</style>