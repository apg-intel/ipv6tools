console.log('initialized')

var nodegraph = {
  div: '#nodegraph',
  width: 500,
  height: 500,
  graph: {
    nodes: [],
    links: []
  },
  link: [],
  ngroups: [],
  svg: null,
  force: null,

  init: function(){
    // set width and height
    this.setDim();

    // add root node
    this.graph.nodes.unshift({
      "x": this.width/2,
      "y": this.height/2,
      "fixed": true,
      "index": 0,
      "value": 2
    });

    var force = d3.layout.force()
      .size([this.width, this.height])
      .charge(-800)
      .linkDistance(60)
      .on('tick', this.tick)
      .nodes(this.graph.nodes)
      .links(this.graph.links);
    this.force = force;

    var drag = force.drag()
      .on('dragstart', this.dragstart)

    var svg = d3.select(this.div).append("svg")
      .attr("width", this.width)
      .attr("height", this.height);
    this.svg = svg;

    var loading = svg.append("text")
      .attr("x", this.width / 2)
      .attr("y", this.height / 2)
      .attr("dy", ".35em")
      .style("text-anchor", "middle")
      .text("Loading. One moment please…");

    this.link = svg.selectAll(".link")
      .data(this.graph.links)
      .enter().append("line")
        .attr("opacity", 0)
        .attr("class", "link")
        .attr("stroke-width", 1)
        .attr("stroke", "#999");

    this.gnode = svg.selectAll("g.node")
      .data(this.graph.nodes)
      .enter()
      .append("g")
        .classed("gnode", true)
        .attr("opacity", 0)
        .call(drag);

    this.gnode.append("circle")
      .attr("class", function(d){ return (d.fixed) ? "node root_node" : "node" })
      .attr("r", function(d){ return d.value * 12 })
      .attr("fill", this.getFill)
      .attr("stroke", this.getStroke)
      .attr("stroke-width", 2)
      .on("dblclick", this.dblclick)
      .on("mouseover", this.mouseover)
      .on("mouseout", this.mouseout)

    this.gnode.append("text")
      .attr("dx", "1em")
      .attr("dy", "0.3em")
      .text(function(d){ return (d.name) ? d.name : "" })

    // resize listener
    d3.select(window).on('resize', this.resize);

    // timeout so page doesn't lock while simulating
    setTimeout(function(){
      // simulate ticks while stuff isn't visible
      var n = nodegraph.graph.nodes.length;
      force.start();
      for (var i = n * n; i > 0; --i) force.tick();
      force.stop();

      // remove loading sign and make stuff visible
      loading.remove();
      nodegraph.gnode.attr('opacity', 1);
      nodegraph.link.attr('opacity', 1);
    }, 10);
  },
  setDim: function(){
    this.width = $(this.div).outerWidth(), this.height = $(this.div).outerWidth();
  },
  getFill: function(d){
    if(d.dns){
      return "rgb(197, 82, 65)";
    } else {
      return "rgb(133, 133, 133)";
    }
  },
  getStroke: function(d){
    if(d.dns){
      return "rgb(183, 39, 18)";
    } else {
      return "rgb(102, 102, 102)";
    }
  },
  // tick for d3 positioning
  tick: function(){
    nodegraph.link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
    nodegraph.gnode.attr("transform", function(d) {
       return 'translate(' + [d.x, d.y] + ')';
     });
  },
  // event listeners
  dblclick: function(d){
    d3.select(this).classed("fixed", d.fixed = false);
  },
  dragstart: function(d){
    d3.select(this).classed("fixed", d.fixed = true);
  },
  mouseover: function(d){
    console.log(d);
  },
  mouseout: function(d){
    console.log('mouseout');
  },
  resize: function(){
    nodegraph.setDim();

    // set SVG w/h
    nodegraph.svg
      .attr('width', nodegraph.width)
      .attr('height', nodegraph.height);

    // center root node
    nodegraph.graph.nodes[0].x = nodegraph.width/2;
    nodegraph.graph.nodes[0].cx = nodegraph.width/2;
    nodegraph.graph.nodes[0].px = nodegraph.width/2;
    nodegraph.graph.nodes[0].y = nodegraph.height/2;
    nodegraph.graph.nodes[0].cy = nodegraph.height/2;
    nodegraph.graph.nodes[0].py = nodegraph.height/2;

    // set force w/h
    nodegraph.force.size([nodegraph.width, nodegraph.height]).resume();
  }
}
