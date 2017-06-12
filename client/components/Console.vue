<template>
  <div>
    <code id="module-console" class="column is-12">
      <div v-for="entry in console_output" v-if="entry">
        <span class="ts">{{entry.timestamp}}</span>
        <span class="modname" v-if="entry.module">{{entry.module}} | </span>
        <span class="msglog">{{entry.log}}</span>
      </div>
    </code>
  </div>
</template>

<script>
  export default {
    props: {
      results: Object,
      console_output: Array
    }
  }
</script>

<style type="css">
  /*
  * Modules
  */
  #module-console {
    /*background-color: #1d1f21;*/
    min-height: 200px;
  }

  #module-console > div .ts { color: #5f819d; }
  #module-console > div .modname { color: #a54242; }
  #module-console > div .msglog { color: #4a4a4a; }
  #module-console > div { color: #c5c8c6; }
  #module-buttons { margin-bottom: 10px; }
</style>