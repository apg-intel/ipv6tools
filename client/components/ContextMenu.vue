<template>
  <nav class="panel" id="contextmenu" tabindex="-1" v-if="show" :style="{top:top, left:left}">
    <p class="panel-heading">
      {{ip}}
    </p>
    <template v-for="module in modules">
      <a class="panel-block" v-for="action in module.actions" v-if="action.target" v-on:click.prevent="execute_action(module.modname, action.action)">
        {{action.title}}&nbsp;&nbsp;<small>{{module.modname}}</small>
      </a>
    </template>
    <div class="panel-block">
      <p class="control">
        <input class="input is-small" type="text" placeholder="Module Input (optional)" v-model="module_input">
      </p>
    </div>
  </nav>
</template>

<script>
  export default {
    props: {
      modules: Array,
      results: Object,
      menu_options: Object
    },
    data: function() {
      return {
        module_input: "",
        top: "0px",
        left: "0px"
      }
    },
    computed: {
      // dynamic props to avoid using this.menu_options every time
      show: function() {
        return this.menu_options.show;
      },
      ip: function() {
        return this.menu_options.ip;
      }
    },
    watch: {
      // watch menu_options for changes to show to display the contextmenu
      menu_options: function() {
        if(this.show) {
          this.openMenu();
        }
      }
    },
    methods: {
      // click handler
      execute_action: function(modname, action) {
        utils.socket.emit('mod_action', {modname: modname, target: this.results[this.ip], action: action, input: this.module_input});
        this.closeMenu();
      },
      // set the position of the menu
      setPosition: function() {
        this.$nextTick(function(){
          let maxTop = window.innerHeight - this.$el.offsetHeight - 25;
          let top = this.menu_options.y+"px";
          if (this.menu_options.y > maxTop) top = maxTop+"px";
          this.top = top;

          let maxLeft = window.innerWidth - this.$el.offsetWidth - 25;
          let left = this.menu_options.x+"px";
          if (this.menu_options.x > maxLeft) left = maxLeft+"px";
          this.left = left;
        });
      },
      // reset the input field and open and position the menu
      openMenu: function() {
        this.module_input = "";
        this.menu_options.show = true;
        this.setPosition();
      },
      // close the menu
      closeMenu: function() {
        this.menu_options.show = false;
      }
    }
  }
</script>

<style type="css">
#contextmenu {
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