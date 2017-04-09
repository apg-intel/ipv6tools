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
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="table" :class="{'is-active': isActive('table')}">Table</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="json" :class="{'is-active': isActive('json')}">JSON</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click.prevent="setActive" data-tab="graph" :class="{'is-active': isActive('graph')}">Graph</a>
        </div>
    </nav>
</template>

<script>
    export default {
        props: [
            'active'
        ],
        methods: {
            setActive: function(e) {
                this.$emit('setActive', e.target.dataset['tab']);
            },
            isActive: function(name) {
                return this.active === name;
            }
        }
    }
</script>