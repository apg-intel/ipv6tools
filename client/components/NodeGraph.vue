<template>
    <div>
      <svg :width="width" :height="height" style="background: red;">
        
      </svg>
    </div>
</template>

<script>
  import * as d3 from 'd3';

  console.log(d3)
  console.log('asdf')
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
        links: []
      }
    },
    mounted: function() {
      window.addEventListener('resize', this.onResize);
      this.onResize();
    },
    methods: {
      onResize() {
        let style = getComputedStyle(this.$el)
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
