import Vue from 'vue'
import App from './App.vue'

require('font-awesome/css/font-awesome.css');
require('bulma/css/bulma.css');

var app = new Vue({
  el: '#app',
  components: {
    app: App
  }
})
