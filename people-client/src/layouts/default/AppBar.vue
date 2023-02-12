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

    <AddPersonDialog v-model="showAddPersonDialog" @create="createPerson" />
    <EditPersonDrawer v-model="showEditPersonDrawer" @update="updatePerson" />
  </div>
</template>

<script>
  import { useAppStore } from '@/store/app';
  const store = useAppStore();

  import { httpPost } from '@/httpClient.js';
  import AddPersonDialog from '@/components/AddPersonDialog.vue';
  import EditPersonDrawer from '@/components/EditPersonDrawer.vue';

  export default {
    components: {
      AddPersonDialog,
      EditPersonDrawer,
    },
    data() {
      return {
        store: store,
        showAddPersonDialog: false,
      };
    },
    computed: {
      showEditPersonDrawer: {
        get() {
          return this.store.editedPerson != null;
        },
        set(show) {
          if (!show) {
            this.store.setEditedPerson(null);
          }
        },
      },
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
          });
      },
      updatePerson(opts) {
        const payload = {
          first_name: opts.firstName,
          last_name: opts.lastName,
        };
        httpPost('/api/persons/' + opts.personId, payload)
          .then((response) => response.json())
          .then((person) => {
            this.store.setEditedPerson(null);
            this.store.updatePerson(person);
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
