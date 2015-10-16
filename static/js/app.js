console.log('initialized')

var nodegraph = {
  div: '#nodegraph',
  width: 500,
  height: 500,
  graph: {
    nodes: [],
    links: []
  },
  link: null,
  node: null,

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
      .on('tick', nodegraph.tick);

    var drag = force.drag()
      .on('dragstart', nodegraph.dragstart)

    var svg = d3.select(nodegraph.div).append("svg")
      .attr("width", nodegraph.width)
      .attr("height", nodegraph.height);

    var link = svg.selectAll(".link"),
      node = svg.selectAll(".node");

    force
      .nodes(nodegraph.graph.nodes)
      .links(nodegraph.graph.links)
      .start();
    nodegraph.link = link.data(nodegraph.graph.links)
      .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", 1)
        .attr("stroke", "#000");
    nodegraph.node = node.data(nodegraph.graph.nodes)
      .enter().append("circle")
        .attr("class", "node")
        .attr("r", 12)
        .on("dblclick", nodegraph.dblclick)
        .call(drag);

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
  addNode: function(entry){
    console.log(entry);
  }
}
