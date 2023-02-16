<template>
  <v-navigation-drawer
    v-model="show"
    permanent
    location="right"
    :style="{'min-width': 480 + 'px'}"
    class="elevation-10"
  >
    <v-list>
      <v-list-item
        v-if="editedPerson"
      >
        <template v-slot:prepend>
          <div class="pa-2">
            <v-btn
              icon
              flat
              style="position: absolute; top: 0px; left: 8px;"
              @click="close()"
            >
              <v-icon size="large">mdi-close</v-icon>
            </v-btn>
          </div>
        </template>
      </v-list-item>
      <v-row
        justify="center"
        style="position: relative"
      >
        <v-avatar
          v-if="editedPerson"
          size="300"
          class="ma-2 mb-5"
        >
          <v-img
            :src="editedPerson.avatar"
            contain
            :width="300"
          ></v-img>
        </v-avatar>
        <v-btn
          variant="plain"
          size="small"
          rounded="pill"
          style="position: absolute; bottom: 16px; right: 64px;"
          @click="$emit('show-avatar-dialog')"
        >Change</v-btn>
      </v-row>
      <v-list-item class="pt-2 mt-5">
        <v-row>
          <v-col>
            <v-text-field
              ref="firstnameInput"
              variant="underlined"
              v-model="firstName"
              color="primary"
              label="First Name"
              @keyup.enter="emitUpdate()"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              variant="underlined"
              v-model="lastName"
              color="primary"
              label="Last Name"
              @keyup.enter="emitUpdate()"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-list-item>
      <v-slide-x-reverse-transition>
        <v-list-item v-if="dirty">
          <div style="display: flex; justify-content: flex-end">
            <v-btn
              rounded="pill"
              class="my-2"
              color="success"
              @click="emitUpdate()"
            >
              Save Changes
            </v-btn>
          </div>
        </v-list-item>
      </v-slide-x-reverse-transition>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { useAppStore } from '@/store/app';
const store = useAppStore();

export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
    minWidth: {
      type: Number,
      default: 480,
    }
  },
  emits: [
    'update:modelValue',
    'update',
    'show-avatar-dialog',
  ],
  data() {
    return {
      store: store,
      firstName: '',
      lastName: '',
    };
  },
  computed: {
    dirty() {
      return (
        !!this.editedPerson && (
          this.firstName != this.editedPerson.first_name ||
          this.lastName != this.editedPerson.last_name
        )
      );
    },
    formIsValid() {
      return (
        !!this.editedPerson &&
        (this.firstName ||'').trim() != '' &&
        (this.lastName ||'').trim() != ''
      );
    },
    editedPerson() {
      return this.store.editedPerson;
    },
    editedPersonName() {
      if (!this.editedPerson) {
        return '';
      }
      return this.store.editedPerson.first_name + ' ' + this.editedPerson.last_name;
    },
    show: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      },
    },
  },
  watch: {
    editedPerson: function(person) {
      if (person) {
        this.firstName = person.first_name;
        this.lastName = person.last_name;
      }
    },
  },
  methods: {
    close() {
      this.$emit('update:modelValue', false);
    },
    emitUpdate() {
      if (!this.formIsValid) {
        return;
      }
      this.$emit('update', {
        personId: this.editedPerson.id,
        firstName: this.firstName,
        lastName: this.lastName,
      });
    },
  },
}
</script>
