var io = require('socket.io-client')

var namespace = '/scan'; // change to an empty string to use the global namespace
var socket = io.connect('http://' + document.domain + ':8081' + namespace);
// var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

// socket handlers
socket.on('module_output', function(msg) {
  if(msg.log){
    console.log(msg)
  }
});

/*
*  listen for sniffed results
*  result channels: ['icmp_echo_result', 'icmp_name_result', 'multicast_result', 'mdns_result', 'llmnr_result']
*/
socket.on('icmp_echo_result', function(msg){
  console.log(msg)
});
socket.on('icmp_name_result', function(msg){
  console.log(msg)
});
socket.on('multicast_result', function(msg){
  socket.emit('scan_llmnr', msg);
  console.log(msg)
});
socket.on('mdns_result', function(msg){
  console.log(msg)
});
socket.on('llmnr_result', function(msg){
  console.log(msg)
});

module.exports = {
  socket: socket
}
