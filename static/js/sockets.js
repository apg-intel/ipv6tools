  $(document).ready(function(){
  var namespace = '/scan'; // change to an empty string to use the global namespace
  var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

  // socket handler for scan results
  socket.on('scan_results', function(msg) {
    console.log(msg);
    $('body').append('<hr>' + msg.name + ': ' + JSON.stringify(msg.data));
  });

  // event handler for scan action
  $('form#start-scan').submit(function(event) {
    console.log('scanning...');
    socket.emit('start_scan', {data: 'sadf'});
    return false;
  });


});