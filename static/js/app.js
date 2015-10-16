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
  node: [],

  init: function(){
    // set width and height
    this.width = $(nodegraph.div).outerWidth();
    this.height = $(window).height() - $(nodegraph.div).offset().top;
    this.graph.nodes.unshift({
      "x": this.width/2,
      "y": this.height/2,
      "fixed": true,
      "index": 0
    });

    var force = d3.layout.force()
      .size([nodegraph.width, nodegraph.height])
      .charge(-400)
      .linkDistance(40)
      .on('tick', nodegraph.tick)
      .nodes(nodegraph.graph.nodes)
      .links(nodegraph.graph.links);

    var drag = force.drag()
      .on('dragstart', nodegraph.dragstart)

    var svg = d3.select(nodegraph.div).append("svg")
      .attr("width", nodegraph.width)
      .attr("height", nodegraph.height);

    var loading = svg.append("text")
      .attr("x", nodegraph.width / 2)
      .attr("y", nodegraph.height / 2)
      .attr("dy", ".35em")
      .style("text-anchor", "middle")
      .text("Loading. One moment please…");

    nodegraph.link = svg.selectAll(".link")
      .data(nodegraph.graph.links)
      .enter().append("line")
        .attr('opacity', 0)
        .attr("class", "link")
        .attr("stroke-width", 1)
        .attr("stroke", "#000");
    nodegraph.node = svg.selectAll(".node")
      .data(nodegraph.graph.nodes)
      .enter().append("circle")
        .attr('opacity', 0)
        .attr("class", "node")
        .attr("r", 12)
        .on("dblclick", nodegraph.dblclick)
        .on("mouseover", nodegraph.mouseover)
        .on("mouseout", nodegraph.mouseout)
        .call(drag);

    setTimeout(function(){
      // simulate ticks while stuff isn't visible
      var n = nodegraph.graph.nodes.length;
      force.start();
      for (var i = n * n; i > 0; --i) force.tick();
      force.stop();

      // remove loading sign and make stuff visible
      loading.remove();
      nodegraph.node.attr('opacity', 1);
      nodegraph.link.attr('opacity', 1);
    }, 10);


  },
  tick: function(){
    nodegraph.link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
    nodegraph.node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
  },
  dblclick: function(d){
    d3.select(this).classed("fixed", d.fixed = false);
  },
  dragstart: function(d){
    d3.select(this).classed("fixed", d.fixed = true);
  },
  mouseover: function(d){
    console.log('mousein');
  },
  mouseout: function(d){
    console.log('mouseout');
  },
  addNode: function(entry){
    console.log(entry);
  }
}
