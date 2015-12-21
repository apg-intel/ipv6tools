  $(document).ready(function() {
    var namespace = '/scan'; // change to an empty string to use the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    // socket handlers

    /*
     * Handle the ICMP results and intialize the DNS scan
     */
    socket.on('reception', function(msg) {
      // initiate next step(s)
      console.log('stop', msg);
    });

    /*
    *  listen for sniffed results
    *  result channels: ['icmp_echo_result', 'icmp_name_result', 'multicast_result', 'mdns_result', 'llmnr_result']
    */
    socket.on('icmp_echo_result', function(msg){
      new_result.updatePage(msg);
    });
    socket.on('icmp_name_result', function(msg){
      new_result.updatePage(msg);
    });
    socket.on('multicast_result', function(msg){
      socket.emit('scan_llmnr', msg);
      new_result.updatePage(msg);
    });
    socket.on('mdns_result', function(msg){
      new_result.updatePage(msg);
    });
    socket.on('llmnr_result', function(msg){
      new_result.updatePage(msg);
    });

    // event handler for scan action
    $('#start-stop').on('click', function(e) {
      console.log('scanning...');
      e.preventDefault();

      if($(this).hasClass('start-scan')){
        socket.emit('sniffer_init', {});
        scanPage.scanStart();
        socket.emit('start_scan', {});
      } else {
        socket.emit('sniffer_kill', {});
        scanPage.scanStop();
      }
    });
  });
