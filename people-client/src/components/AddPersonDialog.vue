<template>
  <v-dialog
    v-model="show"
    max-width="640"
  >
    <v-card>
      <v-toolbar
        color="transparent"
        title="Create Person"
      >
        <v-btn icon @click="show = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text>
        <v-row>
          <v-col>
            <v-text-field
              ref="firstnameInput"
              variant="underlined"
              v-model="firstName"
              color="primary"
              label="First Name"
              @keyup.enter="emitCreate()"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              variant="underlined"
              v-model="lastName"
              color="primary"
              label="Last Name"
              @keyup.enter="emitCreate()"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn
          :disabled="!formIsValid"
          block
          rounded="pill"
          color="primary"
          @click="emitCreate()"
        >Create Person</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    }
  },
  emits: [
    'create',
    'update:modelValue',
  ],
  data() {
    return {
      firstName: '',
      lastName: '',
    };
  },
  computed: {
    show: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      },
    },
    formIsValid() {
      return (
        (this.firstName ||'').trim() != '' &&
        (this.lastName ||'').trim() != ''
      );
    },
  },
  watch: {
    show: function(show) {
      if (show) {
        this.$nextTick(() => {
          this.$refs.firstnameInput.focus();
        });
      } else {
        this.reset();
      }
    }
  },
  methods : {
    reset() {
      this.firstName = '';
      this.lastName = '';
    },
    emitCreate() {
      if (!this.formIsValid) {
        return;
      }
      this.$emit('create', {
        firstName: this.firstName,
        lastName: this.lastName,
      });
    },
  },
}
</script>
