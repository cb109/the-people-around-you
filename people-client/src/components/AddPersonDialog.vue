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
        <v-text-field
          ref="nameInput"
          variant="underlined"
          v-model="name"
          color="primary"
          label="Name"
          @keyup.enter="emitCreate()"
        ></v-text-field>
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
      name: '',
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
        (this.name ||'').trim() != ''
      );
    },
  },
  watch: {
    show: function(show) {
      if (show) {
        this.$nextTick(() => {
          this.$refs.nameInput.focus();
        });
      } else {
        this.reset();
      }
    }
  },
  methods : {
    reset() {
      this.name = '';
    },
    emitCreate() {
      if (!this.formIsValid) {
        return;
      }
      this.$emit('create', {
        name: this.name,
      });
    },
  },
}
</script>
