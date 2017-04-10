<template>
    <div>
      <div class="notification is-danger">
        Node Graph Not Yet Implemented.
      </div>
      <h1 class="title is-5">Raw Results</h1>
      <pre><code class="json">{{results}}</code></pre>
    </div>
</template>

<script>
  export default {
    props: {
      'results': Object
    }
  }
</script>