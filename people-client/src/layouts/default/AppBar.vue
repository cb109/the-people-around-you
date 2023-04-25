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
        <v-btn
          color="primary"
          prepend-icon="mdi-magnify"
          size="large"
          rounded
          @click="showSearchPersonDialog = !showSearchPersonDialog"
        >Search</v-btn>
      </v-app-bar-title>
    </v-app-bar>
    <EditPersonDrawer
      v-model="showEditPersonDrawer"
      @update="updatePerson"
      @show-avatar-dialog="showCropAvatarDialog = true"
    />
    <AddPersonDialog
      v-model="showAddPersonDialog"
      @create="createPerson"
    />
    <SearchPersonDialog
      v-model="showSearchPersonDialog"
      @jump="jumpToPerson"
    />
    <CropAvatarDialog
      v-model="showCropAvatarDialog"
      @cropped="uploadCroppedAvatar"
    />
  </div>
</template>

<script>
import { useAppStore } from '@/store/app';
const store = useAppStore();

import { httpPost } from '@/httpClient.js';
import AddPersonDialog from '@/components/AddPersonDialog.vue';
import CropAvatarDialog from '@/components/CropAvatarDialog.vue';
import EditPersonDrawer from '@/components/EditPersonDrawer.vue';
import SearchPersonDialog from '@/components/SearchPersonDialog.vue';

export default {
  components: {
    AddPersonDialog,
    CropAvatarDialog,
    EditPersonDrawer,
    SearchPersonDialog,
  },
  data() {
    return {
      store: store,
      showAddPersonDialog: false,
      showSearchPersonDialog: false,
      showCropAvatarDialog: false,
      keyDownEventListener: null,
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
  created() {
    const vm = this;
    if (this.keyDownEventListener) {
      this.removeEventListener('keydown', this.keyDownEventListener);
    }
    this.keyDownEventListener = document.addEventListener('keydown', function(e) {
      // Ctrl + F
      if (e.ctrlKey && e.code == 'KeyF') {
        e.preventDefault();
        vm.showSearchPersonDialog = true;
      }
    });
  },
  methods: {
    uploadCroppedAvatar(croppedImageUrl) {
      const payload = {
        avatar: croppedImageUrl
      };

      const personId = this.store.editedPerson.id;
      httpPost('/api/persons/' + personId + '/avatar', payload)
        .then((response) => response.json())
        .then((person) => {
          this.store.setEditedPerson(null);
          this.store.updatePerson(person);
          this.store.setEditedPerson(person);
        })
        .finally(() => {
          this.showCropAvatarDialog = false;
        });
    },
    jumpToPerson(person) {
      this.store.jumpToPerson(person);
    },
    createPerson(opts) {
      const payload = {
        name: opts.name,
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
        name: opts.name,
        details: opts.details,
        date_of_birth: opts.dateOfBirth || '',
        date_of_death: opts.dateOfDeath || '',
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
