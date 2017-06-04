<template>
    <div id="graph-outer">
      <div id="graph-inner">
      </div>
    </div>
</template>

<script>
  import * as d3 from 'd3';

  export default {
    props: {
      results: Object,
      contextmenu: Function
    },
    data: function() {
      return {
        width: 0,
        height: 0,
        rad_factor: 10,
        node: null,
        link: null,
        drag: null,
        svg: null,
        zoom: null,
        nodecount: 0,
        updateTimeout: null,
        div: "#graph-inner"
      }
    },
    computed: {
      graphData: function() {
        let links = [];
        let nodes = [];
        let root_offset = this.rad_factor*3/2;
        // add root node
        nodes.push({
          fx: (this.width / 2) - root_offset,
          fy: (this.height / 2) - root_offset,
          fixed: true,
          index: 0,
          value: 3,
          root: true,
          id: "root"
        });
        for(var k in this.results) {
          nodes.push({
            x: this.width / 2,
            y: this.height / 2,
            label: this.results[k].ip, 
            id: this.results[k].ip, 
            value: 1
          });
          links.push({
            source: 0, 
            target: nodes.length-1
          });
        }
        return {
          nodes: nodes,
          links: links
        }
      }
    },
    watch: {
      width: function() {
        this.initialize();
        // this.update();
      },
      graphData: function() {
        let _this = this;
        if(_this.graphData.nodes.length > _this.nodecount){
          _this.nodecount = _this.graphData.nodes.length;
          clearTimeout(_this.updateTimeout);
          _this.updateTimeout = setTimeout(function(){
            _this.update();
          }, 500);
        }
      }
    },
    mounted: function() {
      // window.addEventListener('resize', this.onResize);
      this.onResize();
    },
    methods: {
      initialize: function() {
        console.log('Initializing graph.');
        let _this = this;
        _this.zoom = d3.zoom()
          .on("zoom", _this.zoomed);

        d3.select("#graph-inner").html('').append("svg");
        _this.svg = d3.select("svg").call(_this.zoom).on("dblclick.zoom", null);
        _this.svg.attr("width", _this.width).attr("height", _this.height)
        _this.drawChart(_this.graphData)
      },
      drawChart: function(data) {
          let _this = this;
          
          _this.simulation = d3.forceSimulation()
              .force("link", d3.forceLink().id(function(d) { return d.index }).strength(0.6))
              .force("charge", 
                d3.forceManyBody()
                  .strength(function(d){ return d.value*-250 })
              )
              .force("center", d3.forceCenter(_this.width / 2, _this.height / 2))
              .force("y", d3.forceY())
              .force("x", d3.forceX())
              .on("tick", _this.ticked);

          _this.drag = d3.drag()
              .on("start", _this.dragstarted)
              .on("drag", _this.dragged)
              .on("end", _this.dragended)
      
          _this.link = _this.svg.append("g")
              .attr("class", "links")
              .selectAll("line")

          _this.node = _this.svg.append("g")
              .attr("class", "nodes")
              .selectAll("circle")
              .enter().append("circle")
      },

      update: function() {
        let _this = this;
        console.log('Updating graph.');
        let data = _this.graphData;
        _this.simulation.alpha(1).restart();

        _this.node = _this.node.data(data.nodes, function(d) {return d.id; });
        _this.node.exit().remove();
        _this.node = _this.node.enter()
          .append("circle")
          .attr("class", function(d) {
            return (d.fixed) ? "node root_node" : "node";
          })
          .attr("fill", _this.getFill)
          .attr("stroke", "whitesmoke")
          .attr("stroke-width", 2)
          .attr("r", function(d){ return d.value * _this.rad_factor; })
          .on("dblclick", _this.dblclick)
          .on("contextmenu", _this.rightclick)
          .call(_this.drag)
          .merge(_this.node);

        _this.node.append("title").text(function(d){ return d.label; })

        _this.link = _this.link.data(data.links, function(d) { return d.source.id + "-" + d.target.id});
        _this.link.exit().remove();
        _this.link = _this.link.enter()
          .append("line")
          .attr("stroke", "#999999")
          .merge(_this.link);

        _this.simulation.nodes(data.nodes);
        _this.simulation.force("link").links(data.links);
      },
      ticked: function() {
        this.link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        this.node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
      },
      dragstarted: function(d) {
        if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      },
      dragged: function(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
      },
      dragended: function(d) {
        if (!d3.event.active) this.simulation.alphaTarget(0);
      },
      dblclick: function(d) {
        this.simulation.alphaTarget(0.3).restart();
        d.fx = null;
        d.fy = null;
      },
      rightclick: function(d) {
        d3.event.preventDefault();
        this.contextmenu(d.id, d3.event.pageX, d3.event.pageY);
      },
      onResize: function() {
        let style = getComputedStyle(this.$el)
        window.el = this.$el
        // get the heights and widths
        let width = this.$el.offsetWidth
        let height = this.$el.offsetHeight
        // remove the padding
        width -= parseFloat(style.paddingLeft) + parseFloat(style.paddingRight)
        height -= parseFloat(style.paddingTop) + parseFloat(style.paddingBottom)
        // set dimensions
        this.width = width;
        this.height = height;
      },
      zoomed: function() {
        console.log("zoom zoom");
        this.node.attr("transform", d3.event.transform);
        this.link.attr("transform", d3.event.transform);
      },
      getFill: function(d) {
        if (d.root) {
          return "#00d1b2";
        } else if (d.dns_data || d.multicast_report) {
          return "rgb(197, 82, 65)";
        } else {
          return "rgb(170, 170, 170)";
        }
      }
    }
  }
</script>

<style type="text/css">
  #graph-outer {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 10px 10px 0 10px;
    background: whitesmoke;
  }

  #graph-inner {
    flex: 1;
  }

  circle.node {
    cursor: pointer;
  }
</style>
