<template>
  <nav class="panel" id="contextmenu" tabindex="-1" v-if="show" v-on:blur="closeMenu"  :style="{top:top, left:left}">
    <p class="panel-heading">
      {{ip}}
    </p>
    <template v-for="module in modules">
      <a class="panel-block" v-for="action in module.actions" v-if="action.target">
        {{action.title}}&nbsp;&nbsp;<small>{{module.modname}}</small>
      </a>
    </template>
  </nav>
</template>

<script>
  export default {
    props: {
      modules: Array,
      results: Object,
      menu_options: Object
    },
    computed: {
      top: function() {
        return this.menu_options.y;
      },
      left: function() {
        return this.menu_options.x;
      },
      show: function() {
        return this.menu_options.show;
      },
      ip: function() {
        return this.menu_options.ip;
      }
    },
    watch: {
      show: function() {
        if(this.show) {
          this.$nextTick(function() {
            this.$el.focus();
          });
        }
      }
    },
    methods: {
      openMenu: function() {
        console.log("Open menu.");
        this.menu_options.show = true;
      },
      closeMenu: function() {
        console.log("Close menu.");
        this.menu_options.show = false;
      }
    }
  }
</script>

<style type="css">
#contextmenu{
  background: white;
    position: absolute;
    z-index: 999999;
}

#contextmenu:focus {
  outline: none;
}

#contextmenu a > small {
  color: #999;
}
</style>