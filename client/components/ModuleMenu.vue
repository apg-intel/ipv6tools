<template>
  <aside class="menu hero is-fullheight" id="sidebar">
    <div>
      <div class="main">
        <p class="menu-label">
          Modules
        </p>
        <template v-for="module in modules">
          <ul class="menu-list" v-if="hasGlobalActions(module.actions)">
            <li>
              <a :class="{'is-active': isExpanded(module.modname)}" v-on:click="toggleModule(module.modname)">{{module.modname}}</a>
              <ul v-if="isExpanded(module.modname)">
                <li v-for="action in module.actions" :action="action" v-if="!action.target">
                  <a href="#" v-on:click.prevent="execute_action(module.modname, action.action, null)">{{action.title}}</a>
                </li>
              </ul>
            </li>
          </ul>
        </template>
      </div>
    </div>
  </aside>
</template>

<script>
  export default {
    props: {
      'modules': Array
    },
    data: function() {
      return {
        expanded: []
      }
    },
    methods: {
      // check if collapsible menu is open
      isExpanded: function(name){
        return this.expanded.indexOf(name) >= 0
      },
      // check if it has non-targeted actions
      hasGlobalActions: function(actions){
        var hasGlobals = false
        for(var x in actions){
          if(!actions[x].target){
            hasGlobals = true
          }
        }
        return hasGlobals
      },
      // toggle the expanded menus
      toggleModule: function(name){
        if(this.isExpanded(name)){
          this.expanded = this.expanded.filter(function (item) {
              return item != name;
          });
        } else {
          this.expanded.push(name)
        }
      },
      // click handler
      execute_action: function(modname, action, target){
        // _this.logMessage('Modules loaded.')
        utils.socket.emit('mod_action', {modname: modname, target: target, action: action});
      }
    }
  }
</script>

<style type="css">
  #sidebar{
    background: #232B2D;
    min-height: 86.9vh;
  }

  #sidebar .main {
    padding: 10px;
    color: #6F7B7E;
  }

  #sidebar .main a {
    color: #6F7B7E;
  }

   #sidebar .main a.is-active {
    background-color: whitesmoke;
    border-color: transparent;
    color: #363636;
  }
</style>
