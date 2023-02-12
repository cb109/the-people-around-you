<template>
  <div>
    <v-app-bar flat class="transparent">
      <v-app-bar-title>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          size="large"
          rounded
          @click="showAddPersonDialog = !showAddPersonDialog"
        >Add Person</v-btn>
      </v-app-bar-title>
    </v-app-bar>
    <AddPersonDialog v-model="showAddPersonDialog" @create="createPerson"/>
    <!-- <v-navigation-drawer
        v-model="showAddPersonDialog"
        temporary
        location="left"
        style="min-width: 480px;"
      >
      <v-list>
        <v-list-item>1</v-list-item>
        <v-list-item>2</v-list-item>
        <v-list-item>3</v-list-item>
      </v-list>
    </v-navigation-drawer> -->
  </div>
</template>

<script>
  import { useAppStore } from '@/store/app';
  const store = useAppStore();

  import { httpPost } from '@/httpClient.js';
  import AddPersonDialog from '@/components/AddPersonDialog.vue';

  export default {
    components: {
      AddPersonDialog,
    },
    data() {
      return {
        store: store,
        showAddPersonDialog: false,
      };
    },
    methods: {
      createPerson(opts) {
        const payload = {
          first_name: opts.firstName,
          last_name: opts.lastName,
        };
        this.showAddPersonDialog = false;
        httpPost('/api/persons/create', payload)
          .then((response) => response.json())
          .then((person) => {
            this.store.addPerson(person);
            // TODO: Select person
          });
      },
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
