import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    persons: [],
    editedPerson: null,
  }),
  actions: {
    setPersons(persons) {
      this.persons = persons;
    },
    addPerson(person) {
      this.persons.push(person);
    },
    updatePerson(person) {
      console.log('updatePerson', person);
      for (let i = 0; i < this.persons.length; i++) {
        if (this.persons[i].id == person.id) {
          this.persons[i] = person;
          break;
        }
      }
    },
    setEditedPerson(person) {
      this.editedPerson = person;
    },
  },
});
