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
        var tableData = [];
        for (var ip in msg.data) {
          var tmp = msg.data[ip];
          tmp.name = msg.data[ip].device_name;
          tmp.id = ip;
          tmp.ip = ip;
          tableData.push(tmp);

          tmp.x = 0;
          tmp.y = 0;
          nodegraph.addNode(tmp);
          nodegraph.addLink("root", ip);

        }
        nodetable.update(tableData);
      } else {
        scanPage.showError();
      }
    });


    /*
     * Handle the DNS query results
     */
    socket.on('dns_results', function(msg) {
      console.log('dns_results', msg);
      if(!$.isEmptyObject(msg.data)){
        nodetable.addDNS(msg.data);
        nodegraph.addDNS(msg.data);
      }
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

    // event handler for scan action
    $('form#start-scan').submit(function(event) {
      console.log('scanning...');
      scanPage.scanStart();
      socket.emit('start_scan', {});
      return false;
    });
  });
