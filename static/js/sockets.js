  $(document).ready(function() {
    var namespace = '/scan'; // change to an empty string to use the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    // socket handlers

    /*
     * Handle the ICMP results and intialize the DNS scan
     */
    socket.on('icmp_results', function(msg) {
      // initiate next step(s)
      console.log('icmp_results', msg);
        // socket.emit('scan_dns', {res: msg.data});
        scanPage.showResults();
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
      new_result.updatePage(msg);
      socket.emit('scan_llmnr', msg);
    });
    socket.on('mdns_result', function(msg){
      new_result.updatePage(msg);
    });
    socket.on('llmnr_result', function(msg){
      console.log('llmnr', msg)
      new_result.updatePage(msg);
    });

    // event handler for scan action
    $('form#start-scan').submit(function(event) {
      console.log('scanning...');
      socket.emit('sniffer_init', {});
      scanPage.scanStart();
      scanPage.showResults();
      socket.emit('start_scan', {});
      return false;
    });
  });
