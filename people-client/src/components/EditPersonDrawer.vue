<template>
  <v-navigation-drawer
    v-model="show"
    permanent
    location="right"
    :style="{'min-width': 560 + 'px'}"
    class="elevation-10"
  >
    <v-list v-if="editedPerson">
      <v-list-item>
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
        <!-- Name -->
        <v-row>
          <v-col>
            <v-text-field
              ref="nameInput"
              variant="outlined"
              v-model="name"
              color="primary"
              label="Name"
              class="pt-2"
              hide-details
              @keyup.enter="emitUpdate()"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <!-- Date of Birth -->
          <v-col>
            <v-text-field
              variant="outlined"
              type="date"
              v-model="dateOfBirth"
              color="primary"
              label="Date of Birth"
              prepend-inner-icon="mdi-asterisk"
              clearable
              @keyup.enter="emitUpdate()"
              :hint="editedPerson.age ? `${editedPerson.age} years old` : ''"
              :persistent-hint="!!editedPerson.age"
            ></v-text-field>
          </v-col>
          <!-- Date of Death -->
          <v-col>
            <v-text-field
              v-if="showDeceasedInput"
              variant="outlined"
              type="date"
              :value="editedPerson.date_of_death"
              color="primary"
              label="Deceased"
              prepend-inner-icon="mdi-flower-tulip-outline"
              clearable
            ></v-text-field>
            <div
              v-else
              style="
                display: flex;
                height: calc(100% - 22px);
                align-items: center;
              "
            >
              <v-btn
                size="small"
                variant="plain"
                rounded="pill"
                prepend-icon="mdi-flower-tulip-outline"
                @click="showDeceasedInput = true"
              >
                Mark deceased
              </v-btn>
            </div>
          </v-col>
        </v-row>
        <!-- Details -->
        <v-row>
          <v-col>
            <v-textarea
              variant="outlined"
              v-model="details"
              color="primary"
              label="Details"
              @keyup.enter="emitUpdate()"
            ></v-textarea>
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
      showDeceasedInput: false,

      name: '',
      details: '',
      dateOfBirth: null,
      dateOfDeath: null,
    };
  },
  computed: {
    dirty() {
      return (
        !!this.editedPerson && (
          this.name != this.editedPerson.name ||
          this.details != this.editedPerson.details ||
          this.dateOfBirth != this.editedPerson.date_of_birth ||
          this.dateOfDeath != this.editedPerson.date_of_death
        )
      );
    },
    formIsValid() {
      return (
        !!this.editedPerson &&
        (this.name ||'').trim() != ''
      );
    },
    editedPerson() {
      return this.store.editedPerson;
    },
    editedPersonName() {
      if (!this.editedPerson) {
        return '';
      }
      return this.store.editedPerson.name;
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
        this.showDeceasedInput = !!person.date_of_death;

        this.name = person.name;
        this.details = person.details;
        this.dateOfBirth = person.date_of_birth;
        this.dateOfDeath = person.date_of_death;
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
        name: this.name,
        details: this.details,
        dateOfBirth: this.dateOfBirth,
        dateOfDeath: this.dateOfDeath,
      });
    },
  },
}
</script>
