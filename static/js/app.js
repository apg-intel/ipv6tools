console.log('initialized');


// control the ajax-ness of the page
var scanPage = {
  form: $('#scan-form'),
  progress: $('#scan-progress'),
  error: $('#scan-error'),
  results: $('#scan-results'),
  results_header: $('#results-header'),
  scanStart: function() {
    this.form.find('button#submit').hide();
    this.error.hide();
    this.progress.show();
    this.results.hide();
  },
  showResults: function() {
    this.form.hide();
    this.results.show();
    this.results_header.show();
    nodegraph.init();
    nodetable.init();
  },
  showError: function(){
    this.form.show();
    this.form.find('button#submit').show();
    this.results.hide();
    this.results_header.hide();
    this.progress.hide();
    this.error.show();
  },
  scanDone: function() {
    this.progress.hide();
    this.form.find('button#submit').show();
    // this.form.show();
  }
};

// initialize, modify, and update the table
var nodetable = {
  table: null,
  data: null,
  init: function(data) {
    data = data || [];
    var table = $('#nodetable').DataTable({
      data: data,
      columns: [{
        className: 'details-control',
        data: null,
        defaultContent: "",
        render: function(data, type, full, meta) {
          if (data.dns_data && !$.isEmptyObject(data.dns_data)) {
            return "<span class='glyphicon glyphicon-chevron-down'></span>";
          }
        }
      }, {
        data: "ip"
      }, {
        data: "mac"
      }, {
        data: "device_name",
        defaultContent: ""
      }],
      order: [
        [0, 'desc'],
        [3, 'desc']
      ],
      rowCallback: function(row, d, index) {
        $(row).attr('id', ipv6_id(d.ip));
        if (d.dns_data && !$.isEmptyObject(d.dns_data)) {
          $(row).addClass('has-dns');
        }

        if (nodegraph.pinned.indexOf(d.ip) >= 0) {
          $(row).addClass('highlighted-row');
        }
      }
    });
    this.table = table;
    this.oTable = $('#nodetable').dataTable();

    $('#nodetable tbody').on('click', 'tr.has-dns > td', function(e) {
      var tr = $(this).closest('tr'),
        row = table.row(tr);

      tr.find('.details-control > .glyphicon').toggleClass('glyphicon-chevron-down').toggleClass('glyphicon-chevron-up');

      if (row.child.isShown()) {
        row.child.hide();
        tr.removeClass('shown');
      } else {
        row.child(nodetable.formatSubrow(row.data()), 'dns-details').show();
        tr.addClass('shown');
      }
    });
  },
  update: function(data) {
    this.data = data;
    // update device count
    $('#scan-results-count').text(data.length);
    this.oTable.fnClearTable(this);
    this.oTable.fnAddData(data);
  },
  addDNS: function(data) {
    var ipMatch = function(obj) {
      return obj.ip === ip;
    };
    if (data) {
      for (var ip in data) {
        if (!$.isEmptyObject(data[ip].dns_data)) {
          var obj = this.data.filter(ipMatch)[0];
          if (obj) {
            obj.dns_data = data[ip].dns_data;
            // set the name if answer_type is 28
            var name = data[ip].dns_data.filter(function(obj) {
              return obj.answer_type == 28;
            })[0];
            if (name) {
              obj.device_name = formatName(name.answer_name);
            }
          }
        }
      }
    }
    this.update(this.data);
  },
  formatSubrow: function(d) {
    var table = "";
    if (d.dns_data && !$.isEmptyObject(d.dns_data)) {
      table = '<table class="table table-bordered table-condensed table-hover dns-details-table">';
      table += '<tr><th>';
      table += Object.keys(d.dns_data[0]).join("</th><th>");
      table += '</th></tr>';

      $.each(d.dns_data, function(i, row) {
        table += '<tr>';
        $.each(row, function(k, v) {
          table += '<td class="' + k + '">' + (v) + '</td>';
        });
        table += '</tr>';
      });
      table += '</table>';
    }

    return table;
  }
};

var nodegraph = {
  div: '#nodegraph',
  width: 500,
  height: 500,
  radius: 12, //value * 12
  graph: {
    nodes: [],
    links: []
  },
  link: [],
  gnode: [],
  svg: null,
  force: null,
  pinned: [],

  init: function() {
    // set width and height
    this.setDim();
    this.force = d3.layout.force()
      .nodes(this.graph.nodes)
      .links(this.graph.links)
      .on('tick', this.tick);
    this.setForce();

    this.graph.nodes.push({
      "x": this.width / 2,
      "y": this.height / 2,
      "fixed": true,
      "index": 0,
      "value": 3,
      "root": true,
      "id": "root"
    });

    var drag = this.force.drag()
      .on('dragstart', this.dragstart);

    var svg = d3.select(this.div).html('').append("svg")
      .attr("width", this.width)
      .attr("height", this.height);
    this.svg = svg;

    var loading = svg.append("text")
      .attr("x", this.width / 2)
      .attr("y", this.height / 2)
      .attr("dy", ".35em")
      .style("text-anchor", "middle")
      .text("Loading. One moment please…");

    this.link = svg.selectAll(".link");
    this.gnode = svg.selectAll(".gnode");

    // resize listener
    d3.select(window).on('resize', this.resize);

    this.update();

    // timeout so page doesn't lock while simulating
    setTimeout(function() {
      // simulate ticks while stuff isn't visible
      var n = nodegraph.graph.nodes.length;
      if (n < 100) n = 100;
      nodegraph.force.start();
      for (var i = n * n; i > 0; --i) nodegraph.force.tick();
      nodegraph.force.stop();

      // remove loading sign and make stuff visible
      loading.remove();
      nodegraph.gnode.attr('opacity', 1);
      nodegraph.link.attr('opacity', 1);
    }, 10);
  },
  setDim: function() {
    var width = $(this.div).outerWidth();
    var aspect = (width > 700) ? 9 / 16 : 3 / 4;
    this.width = width;
    this.height = width * aspect;
  },
  setForce: function() {
    var k = Math.sqrt(this.graph.nodes.length / (this.width * this.height)); //linear scale for gravity, charge, and linkDistance

    return this.force.charge(function(d) {
        return (d.value || 1) * (-10 / k);
      })
      .linkDistance(2000 * k)
      .gravity(10 * k)
      .size([this.width, this.height]);
  },
  getFill: function(d) {
    var hovered = d3.select(this).classed("hovered");
    var fixed = d3.select(this).classed("fixed");

    if (d.root) {
      return "rgb(51, 103, 153)";
    } else if (d.dns) {
      if (hovered || fixed) {
        return "rgb(157, 42, 25)";
      }
      return "rgb(197, 82, 65)";
    } else {
      if (hovered || fixed) {
        return "rgb(140, 140, 140)";
      }
      return "rgb(170, 170, 170)";
    }
  },
  getStroke: function(d) {
    var hovered = d3.select(this).classed("hovered");
    var fixed = d3.select(this).classed("fixed");

    if (d.root) {
      return "rgb(0, 66, 128)";
    } else if (d.dns) {
      if (hovered || fixed) {
        return "rgb(143, 11, 8)";
      }
      return "rgb(183, 39, 18)";
    } else {
      if (hovered || fixed) {
        return "rgb(90, 90, 90)";
      }
      return "rgb(130, 130, 130)";
    }
  },
  // tick for d3 positioning
  tick: function() {
    nodegraph.gnode.attr("transform", function(d) {
      var r = nodegraph.radius * (d.value || 1);
      d.x = Math.max(r, Math.min(nodegraph.width - r, d.x));
      d.y = Math.max(r, Math.min(nodegraph.height - r, d.y));
      return 'translate(' + d.x + ',' + d.y + ')';
    });
    nodegraph.link.attr("x1", function(d) {
        return d.source.x;
      })
      .attr("y1", function(d) {
        return d.source.y;
      })
      .attr("x2", function(d) {
        return d.target.x;
      })
      .attr("y2", function(d) {
        return d.target.y;
      });
  },
  // event listeners
  dblclick: function(d) {
    d3.select(this).classed("fixed", d.fixed = false)
      .select('circle.node')
      .attr("fill", nodegraph.getFill)
      .attr("stroke", nodegraph.getStroke);

    if (d.id && nodegraph.pinned.indexOf(d.id) >= 0) nodegraph.pinned.splice(nodegraph.pinned.indexOf(d.id), 1);
  },
  dragstart: function(d) {
    if (d3.event.sourceEvent.which === 1) { //only on left click drag
      d3.select(this)
        .select('circle.node')
        .classed("fixed", d.fixed = true)
        .attr("fill", nodegraph.getFill)
        .attr("stroke", nodegraph.getStroke);
      if (d.id && nodegraph.pinned.indexOf(d.id) === -1) nodegraph.pinned.push(d.id);
    }
  },
  mouseover: function(d) {
    // highlight node
    d3.select(this)
      .classed("hovered", true)
      .attr("fill", nodegraph.getFill)
      .attr("stroke", nodegraph.getStroke);

    // find in table
    if (d.id) $('#' + ipv6_id(d.id)).addClass('highlighted-row');
  },
  mouseout: function(d) {
    d3.select(this)
      .classed("hovered", false)
      .attr("fill", nodegraph.getFill)
      .attr("stroke", nodegraph.getStroke);

    if (d.id) {
      if (!d3.select(this).classed("fixed") && nodegraph.pinned.indexOf(d.id) < 0) {
        $('#' + ipv6_id(d.id)).removeClass('highlighted-row');
      }
    }
  },
  contextmenu: function(d, i) {
    // add context menu
    d3.select('.nodegraph-context-menu')
      .data([1])
      .enter()
      .append('div')
      .attr('class', 'nodegraph-context-menu')
      .html('<ul><li>asdf</li></ul>');

    // set up listener to close CM
    d3.select('body').on('click.nodegraph-context-menu', function() {
      d3.select('.nodegraph-context-menu').style('display', 'none');
    });


    if (d.root) {
      // nothing yet
    } else {
      nodegraph.buildMenu();
      d3.select('.nodegraph-context-menu')
        .style('left', (d3.event.pageX - 2) + 'px')
        .style('top', (d3.event.pageY - 2) + 'px')
        .style('display', 'block');
    }
    d3.event.preventDefault();
    console.log(d);
  },
  buildMenu: function(d) {
    var menu = [{
      title: 'Do Something',
      action: function(e, d, i) {
        console.log('asdf', e, d, i);
      }
    }, {
      title: 'Do Something Else',
      action: function(e, d, i) {
        console.log('asdf2', e, d, i);
      }
    }];

    var elm = this;
    d3.selectAll('.nodegraph-context-menu').html('');
    var list = d3.selectAll('.nodegraph-context-menu').append('ul').attr('class', 'dropdown-menu');
    list.selectAll('li').data(menu).enter()
      .append('li')
      .append('a')
      .attr('href', '#')
      .html(function(d) {
        return d.title;
      })
      .on('click', function(d, i) {
        d.action(elm, d, i);
        d3.select('.nodegraph-context-menu').style('display', 'none');
      });
  },
  resize: function() {
    nodegraph.setDim();

    // set SVG w/h
    nodegraph.svg
      .attr('width', nodegraph.width)
      .attr('height', nodegraph.height);

    // center root node
    nodegraph.graph.nodes[0].x = nodegraph.width / 2;
    nodegraph.graph.nodes[0].cx = nodegraph.width / 2;
    nodegraph.graph.nodes[0].px = nodegraph.width / 2;
    nodegraph.graph.nodes[0].y = nodegraph.height / 2;
    nodegraph.graph.nodes[0].cy = nodegraph.height / 2;
    nodegraph.graph.nodes[0].py = nodegraph.height / 2;

    // set force w/h
    nodegraph.force.size([nodegraph.width, nodegraph.height]).resume();
  },
  addNode: function(node) {
    this.graph.nodes.push(node);
    this.update();
  },
  removeNode: function(id) {

  },
  addLink: function(sourceId, targetId) {
    var sourceNode = this.findNode(sourceId);
    var targetNode = this.findNode(targetId);

    if (sourceNode !== undefined && targetNode !== undefined) {
      this.graph.links.push({
        source: sourceNode,
        target: targetNode
      });
      this.update();
    }
  },
  findNode: function(id) {
    for (var i = 0; i < nodegraph.graph.nodes.length; i++) {
      if (nodegraph.graph.nodes[i].id === id)
        return i;
    }
  },
  update: function() {
    this.force.stop();

    this.link = this.link.data(this.force.links(), function(d) {
      return d.source.id + "-" + d.target.id;
    });
    this.link.enter().insert("line", ".gnode")
      .attr("class", "link")
      .attr("stroke-width", 1)
      .attr("stroke", "#999");
    this.link.exit().remove();

    this.gnode = this.gnode.data(this.force.nodes(), function(d) {
      return d.id;
    });
    var node = this.gnode.enter()
      .append("g")
      .classed("gnode", true)
      .call(this.force.drag);

    node.append("circle")
      .attr("class", function(d) {
        return (d.fixed) ? "node root_node" : "node";
      })
      .attr("r", function(d) {
        return (d.value || 1) * nodegraph.radius;
      })
      .attr("fill", this.getFill)
      .attr("stroke", this.getStroke)
      .attr("stroke-width", 2)
      .on("dblclick", this.dblclick)
      .on("mouseover", this.mouseover)
      .on("mouseout", this.mouseout)
      .on("contextmenu", this.contextmenu);

    node.append("text")
      .attr("class", "nodelabel")
      .attr("dx", "1em")
      .attr("dy", "0.3em")
      .text(function(d) {
        return d.name || '';
      });

    this.gnode.exit().remove();

    // update node colors
    d3.selectAll("circle.node")
      .attr("fill", this.getFill)
      .attr("stroke", this.getStroke);

    // update nodelabels
    d3.selectAll("text.nodelabel")
      .text(function(d) {
        return d.name || '';
      });

    this.gnode.sort(function(a, b) {
      if (!a.name) return -1;
      else return 1;
    });

    // reset the dim
    this.setDim();

    // reset the force
    this.setForce().start();
  },
  addDNS: function(data) {
    var ipMatch = function(obj) {
      return obj.id === ip;
    };
    if (data) {
      for (var ip in data) {
        if (!$.isEmptyObject(data[ip].dns_data)) {
          var obj = this.graph.nodes.filter(ipMatch)[0];
          if (obj) {
            obj.dns = data[ip].dns_data;
            // set the name if answer_type is 28
            var name = data[ip].dns_data.filter(function(obj) {
              return obj.answer_type == 28;
            })[0];
            if (name) {
              obj.name = formatName(name.answer_name);
            }
          }

        }
      }
      this.update();
    }
  }
};

function formatName(name){
  return name.replace(/\.local\./g, "");
}
function ipv6_id(ip) {
  return ip.replace(/\:/g, "");
}
