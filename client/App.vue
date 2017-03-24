<template>
  <navbar v-bind:scanning="scanning" v-on:start="startScan" v-on:stop="stopScan"></navbar>
</template>

<script>
import { Navbar } from './components/'
  export default {
    data: function() {
        return {
            scanning: false,
            results: []
        }
    },
    components: {
        navbar: Navbar
    },
    methods: {
        startScan: function() {
            this.scanning = true
            console.log('scanning!')
        },
        stopScan: function() {
            this.scanning = false
            console.log('Stop scanning...')
        }
    }
  }
</script>