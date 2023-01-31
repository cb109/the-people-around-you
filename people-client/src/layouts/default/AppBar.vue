<template>
  <v-app-bar flat class="transparent">
    <v-app-bar-title>
      <v-btn
        disabled
        variant="flat"
        color="primary"
        prepend-icon="mdi-plus"
        size="large"
        rounded
      >Add Person</v-btn>
    </v-app-bar-title>
  </v-app-bar>
</template>

<script setup>
  //
</script>


<style>
.transparent {
  /* background-color: rgba(255, 255, 255, 0.25) !important; */
  background-color: transparent !important;
}
.v-main {
  padding-top: none !important;
  --v-layout-top: 0px !important;
}
</style>
