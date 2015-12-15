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
      if(!$.isEmptyObject(msg.data)){
        socket.emit('scan_dns', {res: msg.data});
        scanPage.showResults();
      } else {
        scanPage.showError();
      }
    });


    /*
     * Handle the DNS query results
     */
    socket.on('dns_results', function(msg) {
      console.log('dns_results', msg);
      scanPage.scanDone();
      // socket.emit('dig_listen', {ips: Object.keys(msg.data)}); // not needed yet i guess? no results...
    });

    /*
     * Handle the dig query results
     */
    socket.on('dig_results', function(msg) {
      console.log(msg);
      $('body').append('<hr>dig: ' + JSON.stringify(msg.data));
    });

    /*
    *  listen for sniffed results
    *  result channels: ['icmp_echo_result', 'icmp_name_result', 'multicast_result', 'mdns_result', 'llmnr_result']
    */
    socket.on('icmp_echo_result', function(msg){
      nodetable.updateRow(msg);
      nodegraph.updateNode(msg);
    });
    socket.on('icmp_name_result', function(msg){
      nodetable.updateRow(msg);
      nodegraph.updateNode(msg);
    });
    socket.on('multicast_result', function(msg){
      nodetable.updateRow(msg);
      nodegraph.updateNode(msg);
    });
    socket.on('mdns_result', function(msg){
      nodetable.updateRow(msg);
      nodegraph.updateNode(msg);
    });
    socket.on('llmnr_result', function(msg){
      nodetable.updateRow(msg);
      nodegraph.updateNode(msg);
    });

    // event handler for scan action
    $('form#start-scan').submit(function(event) {
      console.log('scanning...');
      scanPage.scanStart();
      socket.emit('sniffer_init', {});
      socket.emit('start_scan', {});
      return false;
    });
  });
