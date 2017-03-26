<template>
    <nav class="nav has-shadow">
        <div class="nav-left">
            <a class="nav-item">
                <h4 class="title is-4">IPv6Tools</h4>
            </a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click="setActive" data-tab="table" :class="{'is-active': isActive('table')}">Table</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click="setActive" data-tab="json" :class="{'is-active': isActive('json')}">JSON</a>
            <a href="#" class="nav-item is-tab is-hidden-mobile" v-on:click="setActive" data-tab="graph" :class="{'is-active': isActive('graph')}">Graph</a>
        </div>
        <span class="nav-toggle">
            <span></span>
            <span></span>
            <span></span>
        </span>
        <div class="nav-right nav-menu">
            <span class="nav-item">
                <a class="button is-primary" id="start-stop-scan" v-on:click="startStopScan" :class="{'scan-active': scanning}">
                    <span class="icon">
                        <i class="fa" :class="{'fa-spin': scanning, 'fa-circle-o-notch': scanning, 'fa-circle-o': !scanning}"></i>
                    </span>
                    <span v-if="scanning">Scanning</span>
                    <span v-else>Scan</span>
                </a>
            </span>
        </div>
    </nav>
</template>

<script>
    export default {
        props: [
            'scanning',
            'active'
        ],
        methods: {
            setActive: function(e) {
                this.$emit('setActive', e.target.dataset['tab']);
            },
            isActive: function(name) {
                return this.active === name;
            },
            startStopScan: function() {
                if(this.scanning) {
                    this.$emit('stop')
                } else {
                    this.$emit('start')
                }
            }
        }
    }
</script>

<style type="css">
    .scan-active:hover {
        background-color: #ff3860!important;
    }
    .scan-active:hover span {
        display: none;
    }
    .scan-active:hover:before {
        content: 'Stop Scanning';
    }
</style>