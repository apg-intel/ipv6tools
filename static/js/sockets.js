  $(document).ready(function(){
  var namespace = '/scan'; // change to an empty string to use the global namespace
  var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

  // socket handlers

  /*
  * Handle the ICMP results and intialize the DNS scan
  */
  socket.on('icmp_results', function(msg) {
    for(var ip in msg.data){
      var tmp = {
        id: ip,
        mac: msg.data[ip].mac,
        name: msg.data[ip].device_name,
        x: 0,
        y: 0
      }
      nodegraph.addNode(tmp)
      nodegraph.addLink("root", ip);
    }
    socket.emit('scan_dns', {});
  });


  /*
  * Handle the DNS query results
  */
  socket.on('dns_results', function(msg){
    console.log(msg);
    $('body').append('<hr>dns_data: ' + JSON.stringify(msg.data));
    // socket.emit('dig_listen', {ips: Object.keys(msg.data)}); // not needed yet i guess? no results...
  });

  /*
  * Handle the dig query results
  */
  socket.on('dig_results', function(msg){
    console.log(msg);
    $('body').append('<hr>dig: ' + JSON.stringify(msg.data));
  });

  // event handler for scan action
  $('form#start-scan').submit(function(event) {
    console.log('scanning...');
    socket.emit('start_scan', {data: 'sadf'});
    return false;
  });


});
