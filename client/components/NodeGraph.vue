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
        nodes: [],
        links: [],
        gnode: [],
        force: null,
        svg: null,
        pinned: [],
        div: "#graph-inner"
      }
    },
    computed: {
      graphData: function() {
        let range = 100
        return {
          nodes:d3.range(0, range).map(function(d){ return {label: "l"+d ,r:~~d3.randomUniform(8, 28)()}}),
          links:d3.range(0, range).map(function(){ return {source:~~d3.randomUniform(range)(), target:~~d3.randomUniform(range)()} })
        }
      }
    },
    watch: {
      width: function() {
        this.initialize();
        this.update();
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

        _this.drawChart(_this.data)
      },
      drawChart(data) {
          let _this = this;
          console.log('drawing shit');
          
          let simulation = d3.forceSimulation()
              .force("link", d3.forceLink().id(function(d) { return d.index }))
              .force("collide",d3.forceCollide( function(d){return d.r + 8 }).iterations(16) )
              .force("charge", d3.forceManyBody())
              .force("center", d3.forceCenter(_this.width / 2, _this.height / 2))
              .force("y", d3.forceY(0))
              .force("x", d3.forceX(0))
      
          let link = _this.svg.append("g")
              .attr("class", "links")
              .selectAll("line")
              .data(data.links)
              .enter()
              .append("line")
              .attr("stroke", "black")

          let node = _this.svg.append("g")
              .attr("class", "nodes")
              .selectAll("circle")
              .data(data.nodes)
              .enter().append("circle")
              .attr("fill", "red")
              .attr("stroke", "blue")
              .attr("r", function(d){  return d.r })
              .call(d3.drag()
                  .on("start", dragstarted)
                  .on("drag", dragged)
                  .on("end", dragended));    
          
          
          let ticked = function() {
              link
                  .attr("x1", function(d) { return d.source.x; })
                  .attr("y1", function(d) { return d.source.y; })
                  .attr("x2", function(d) { return d.target.x; })
                  .attr("y2", function(d) { return d.target.y; });
      
              node
                  .attr("cx", function(d) { return d.x; })
                  .attr("cy", function(d) { return d.y; });
          }  
          
          simulation
              .nodes(data.nodes)
              .on("tick", ticked);
      
          simulation.force("link")
              .links(data.links);    
          
          
          
          function dragstarted(d) {
              if (!d3.event.active) simulation.alphaTarget(0.3).restart();
              d.fx = d.x;
              d.fy = d.y;
          }
          
          function dragged(d) {
              d.fx = d3.event.x;
              d.fy = d3.event.y;
          }
          
          function dragended(d) {
              if (!d3.event.active) simulation.alphaTarget(0);
              d.fx = null;
              d.fy = null;
          } 
      },

      update() {
        console.log('Updating graph.');
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
