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
      results: Object
    },
    data: function() {
      return {
        width: 0,
        height: 0,
        radius: 12,
        node: null,
        link: null,
        drag: null,
        svg: null,
        pinned: [],
        updateTimeout: null,
        div: "#graph-inner"
      }
    },
    computed: {
      graphData: function() {
        console.log(this.results);
        let links = [];
        let nodes = [];
        // add root node
        nodes.push({
          x: this.width / 2,
          y: this.height / 2,
          fixed: true,
          index: 0,
          value: 3,
          root: true,
          id: "root"
        });
        for(var k in this.results) {
          nodes.push({
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
        this.update();
      },
      graphData: function() {
        console.log("Updated data", this.graphData);
        let _this = this;
        clearTimeout(_this.updateTimeout);
        _this.updateTimeout = setTimeout(function(){
          _this.update();
        }, 1000);
      }
    },
    mounted: function() {
      // window.addEventListener('resize', this.onResize);
      this.onResize();
    },
    methods: {
      initialize() {
        console.log('Initializing graph.');
        let _this = this;

        _this.svg = d3.select("#graph-inner").html('').append("svg")
        _this.svg.attr("width", _this.width).attr("height", _this.height)
        _this.drawChart(_this.graphData)
      },
      drawChart(data) {
          let _this = this;
          console.log('drawing shit');
          
          _this.simulation = d3.forceSimulation()
              .force("link", d3.forceLink().id(function(d) { return d.index }).strength(1))
              // .force("collide",d3.forceCollide( function(d){return d.r + 8 }).iterations(16) )
              .force("charge", d3.forceManyBody())
              .force("center", d3.forceCenter(_this.width / 2, _this.height / 2))
              .force("y", d3.forceY())
              .force("x", d3.forceX())
              .on("tick", _this.ticked);

          _this.drag = d3.drag()
              .on("start", _this.dragstarted)
              .on("drag", _this.dragged)
              .on("end", _this.dragended);
      
          _this.link = _this.svg.append("g")
              .attr("class", "links")
              .selectAll("line")

          _this.node = _this.svg.append("g")
              .attr("class", "nodes")
              .selectAll("circle")
              .enter().append("circle")
          
          _this.update();
      },

      update() {
        let _this = this;
        console.log('Updating graph.');
        let data = _this.graphData;

        _this.node = _this.node.data(data.nodes, function(d) {return d.id; });
        _this.node.exit().remove();
        _this.node = _this.node.enter()
          .append("circle")
          .attr("class", function(d) {
            return (d.fixed) ? "node root_node" : "node";
          })
          .attr("fill", "red")
          .attr("stroke", "blue")
          .attr("stroke-width", 2)
          .attr("r", function(d){ return d.value * 10; })
          .call(_this.drag)
          .merge(_this.node);

        _this.link = _this.link.data(data.links, function(d) { return d.source.id + "-" + d.target.id});
        _this.link.exit().remove();
        _this.link = _this.link.enter()
          .append("line")
          .attr("stroke", "black")
          .merge(_this.link);

        _this.simulation.nodes(data.nodes);
        _this.simulation.force("link").links(data.links);
        _this.simulation.alpha(1).restart();
      },
      ticked() {
        this.link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        
        this.node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });

      },
      dragstarted(d) {
        if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      },
      dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
      },
      dragended(d) {
        if (!d3.event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      },
      onResize() {
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
  }

  #graph-inner {
    flex: 1;
  }
</style>
