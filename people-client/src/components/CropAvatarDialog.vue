<template>
  <v-dialog
    v-model="show"
    max-width="640"
    persistent
  >
    <v-card>
      <v-toolbar
        color="transparent"
        title="Upload Avatar"
      >
        <v-btn
          icon
          @click="show = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text>
        <v-file-input
          v-model="imageModel"
          accept="image/*"
          label="Browse image file"
          variant="outlined"
          clearable
        ></v-file-input>
        <cropper
          v-if="imageURL"
          :src="imageURL"
          :stencil-component="$options.components.CircleStencil"
          class="cropper"
          @change="onCropperChange"
        />
      </v-card-text>
      <v-card-actions>
        <v-btn
          :disabled="!formIsValid"
          block
          rounded="pill"
          color="primary"
          @click="emitCropped()"
        >Upload</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { Cropper, CircleStencil } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import 'vue-advanced-cropper/dist/theme.compact.css';

export default {
  components: {
    Cropper,
    CircleStencil,  // sic!
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    }
  },
  emits: [
    'update:modelValue',
    'cropped',
  ],
  data() {
    return {
      imageModel: null,
      croppedImageBlob: null,
      croppedImageURL: null,
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
      return !!this.imageModel;
    },
    imageURL() {
      if (!this.imageModel) {
        return null;
      }
      const image = this.imageModel[0];
      if (!image) {
        return null;
      }
      return URL.createObjectURL(image);
    },
  },
  watch: {
    show: function(show) {
      if (!show) {
        this.reset();
      }
    }
  },
  methods : {
    reset() {
      this.imageModel = null;
      this.croppedImageBlob = null;
      this.croppedImageURL = null;
    },
    // https://advanced-cropper.github.io/vue-advanced-cropper/guides/recipes.html#getting-the-result
    onCropperChange({coordinates, canvas}) {
      canvas.toBlob((blob) => {

        const image = this.imageModel[0];
        blob.name = image.name;

        this.croppedImageBlob = blob;
      });
      this.croppedImageURL = canvas.toDataURL();
    },
    emitCropped() {
      this.$emit('cropped', this.croppedImageBlob);
    },
  },
}
</script>

<style scoped>
.cropper {
  max-width: 600px;
  max-height: 600px;
  object-fit: contain;
  background: red,
}
</style>
