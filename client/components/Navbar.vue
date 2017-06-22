<template>
    <nav class="nav has-shadow">
        <div class="nav-left">
            <a class="nav-item">
                <h4 class="title is-4">IPv6Tools</h4>
            </a>
        </div>
        <span class="nav-toggle">
            <span></span>
            <span></span>
            <span></span>
        </span>
        <div class="nav-right nav-menu">
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="results" :class="{'is-active': isActive('results')}">Results</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="table" :class="{'is-active': isActive('table')}">Table</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="console" :class="{'is-active': isActive('console')}">Console</a>
            <a href="#" class="nav-item" title="Change Layout" style="display: none;">
                <span class="icon">
                    <i class="fa fa-cog"></i>
                </span>

            </a>
        </div>
    </nav>
</template>

<script>
    export default {
        props: [
            'active'
        ],
        methods: {
            // set the active menu button
            setActive: function(e) {
                this.$emit('setActive', e.target.dataset['tab']);
            },
            // check if menu button is active
            isActive: function(name) {
                return this.active === name;
            }
        }
    }
</script>
