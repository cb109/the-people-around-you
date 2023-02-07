<template>
  <v-dialog v-model="show">
    <v-card>
      <v-card-text>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</v-card-text>
      <v-card-actions>
        <v-btn
          color="primary"
          block
          @click="show = false"
        >Close Dialog</v-btn>
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
  emits: ['update:modelValue'],
  computed: {
    show: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      },
    },
  },
}
</script>
