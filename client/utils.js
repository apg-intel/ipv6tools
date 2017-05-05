var namespace = '/scan'; // change to an empty string to use the global namespace
module.exports = {
  socket: require('socket.io-client').connect('http://' + document.domain + ':8080' + namespace)
}
