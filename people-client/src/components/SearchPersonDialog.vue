<template>
  <v-dialog
    v-model="show"
    max-width="640"
  >
    <v-card>
      <v-toolbar
        color="transparent"
        title="Search Person"
      >
        <v-btn icon @click="show = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text>
        <v-text-field
          ref="searchInput"
          variant="underlined"
          v-model="searchText"
          color="primary"
          label="Search by Name"
          @update:modelValue="debouncedListPersonsForSearchTerms()"
        ></v-text-field>
      </v-card-text>
      <v-card-actions v-show="persons.length > 0">
        <v-list
          lines="one"
          style="width: 100%"
        >
          <template
            v-for="(person, personIndex) in persons"
            :key="person.id"
          >
            <span title="Jump to this person">
              <v-list-item
                class="my-2"
                @click="jumpToPerson(person)"
              >
                <template v-slot:prepend>
                  <v-avatar size="72" :image="person.avatar"></v-avatar>
                </template>
                <v-list-item-title class="text-h6">{{ person.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-h7">{{ person.date_of_birth }}</v-list-item-subtitle>
              </v-list-item>
            </span>
            <v-divider v-show="personIndex < persons.length - 1"></v-divider>
          </template>
        </v-list>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import debounce from 'lodash.debounce';

import { httpGet } from '@/httpClient.js';

export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    }
  },
  emits: [
    'jump',
    'update:modelValue',
  ],
  data() {
    return {
      searchText: '',
      persons: [],
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
  },
  watch: {
    show: function(show) {
      if (show) {
        this.$nextTick(() => {
          this.searchText = '';
          this.$refs.searchInput.focus();
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
    listPersonsForSearchTerms() {
      if (!this.searchText) {
        this.persons = [];
        return;
      }
      const query = {search: this.searchText};
      httpGet('/api/persons/', query).then((response) => {
        response.json().then((persons) => {
          this.persons = persons;
        });
      });
    },
    debouncedListPersonsForSearchTerms: debounce(function() {
      this.listPersonsForSearchTerms();
    }, 300),
    jumpToPerson(person) {
      this.$emit('jump', person);
      this.$emit('update:modelValue', false);
    }
  },
}
</script>
