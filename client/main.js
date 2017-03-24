import Vue from 'vue'
import App from './App.vue'

require('font-awesome/css/font-awesome.css');
require('bulma/css/bulma.css');

var d3 = require('d3');

var app = new Vue({
  el: '#app',
  components: {
    app: App
  }
})
// event handler for scan action
// $('#start-stop').on('click', function(e) {
//   console.log('scanning...');
//   e.preventDefault();

//   if($(this).hasClass('start-scan')){
//     socket.emit('sniffer_init', {});
//     scanPage.scanStart();
//     socket.emit('start_scan', {});
//   } else {
//     socket.emit('sniffer_kill', {});
//     scanPage.scanStop();
//   }
// });
