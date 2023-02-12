import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    persons: [],
  }),
  actions: {
    setPersons(persons) {
      this.persons = persons;
    },
    addPerson(person) {
      this.persons.push(person);
    },
  },
});
