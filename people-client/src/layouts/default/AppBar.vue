<template>
  <div>
    <v-app-bar flat class="transparent">
      <v-app-bar-title>
        <v-btn
          variant="flat"
          color="primary"
          prepend-icon="mdi-plus"
          size="large"
          rounded
          @click="showAddPersonDialog = !showAddPersonDialog"
        >Add Person</v-btn>
      </v-app-bar-title>
    </v-app-bar>
    <AddPersonDialog v-model="showAddPersonDialog" />
  </div>
</template>

<script>
  import AddPersonDialog from '@/components/AddPersonDialog.vue'

  export default {
    components: {
      AddPersonDialog,
    },
    data() {
      return {
        showAddPersonDialog: false,
      };
    },
  }
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
