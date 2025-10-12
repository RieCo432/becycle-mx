<script>
import Card from '@/components/Card/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import Button from '@/components/Button/index.vue';
import levenshtein from '@/util/levenshtein';

export default {
  name: 'findClient',
  components: {
    Button,
    ComboboxTextInput,
    Card,
  },
  data() {
    return {
      clientSuggestions: [],
      selectedClient: {
        firstName: '',
        lastName: '',
        emailAddress: '',
        id: null,
      },
      filtered_client_suggestions: [],
    };
  },
  created() {
    this.fetchClients = debounce(this.fetchClients, 500, {leading: false, trailing: true});
    this.run_filter = debounce(this.run_filter, 200, {leading: false, trailing: true});
  },
  methods: {
    fetchClients() {
      if ((
          (this.selectedClient.firstName ? this.selectedClient.firstName.length : 0) +
          (this.selectedClient.lastName ? this.selectedClient.lastName.length : 0) +
          (this.selectedClient.emailAddress ? this.selectedClient.emailAddress.length : 0)
      ) > 2) {
        requests.findClient(this.selectedClient.firstName.toLowerCase(), this.selectedClient.lastName.toLowerCase(),
          this.selectedClient.emailAddress.toLowerCase(), 5).then((response) => {
          this.clientSuggestions = response.data;
          this.run_filter();
        });
      }
    },
    selectClient(event, i) {
      // TODO: remove these
      console.log('selected filtered suggestions', this.filtered_client_suggestions);
      console.log('selected index', i);
      this.selectedClient = this.filtered_client_suggestions[i];
    },
    async run_filter() {
      const client = {
        firstName: this.selectedClient.firstName ? this.selectedClient.firstName : '',
        lastName: this.selectedClient.lastName ? this.selectedClient.lastName : '',
        emailAddress: this.selectedClient.emailAddress ? this.selectedClient.emailAddress : '',
      };
      levenshtein.filterSortObject(this.clientSuggestions, client, 4).then((result) => {
        this.filtered_client_suggestions = result;
      });
    },
    handleInput() {
      this.fetchClients();
      this.run_filter();
    },
    resetComboBoxes() {
      this.selectedClient = {
        firstName: '',
        lastName: '',
        emailAddress: '',
        id: null,
      };
      this.filtered_client_suggestions = [];
    },
  },
  computed: {
    filteredClientSuggestionsLegible() {
      return this.filtered_client_suggestions.map((client) => (`${client.firstName} ${client.lastName} ${client.emailAddress}`));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 lg:col-span-8 lg:col-start-3">
      <Card title="Find Client">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedClient.firstName"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
                label="First Name"
                type="text"
                placeholder="First Name"
                name="firstName"
                v-model="selectedClient.firstName"
                @input="handleInput"
                @emptied="resetComboBoxes"
            />
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedClient.lastName"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
                label="Last Name"
                type="text"
                placeholder="Last Name"
                name="lastName"
                v-model="selectedClient.lastName"
                @input="handleInput"
                @emptied="resetComboBoxes"
            />
          </div>

          <div class="col-span-12">
            <ComboboxTextInput
                :field-model-value="selectedClient.emailAddress"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
                label="Email Address"
                type="text"
                placeholder="Email Address"
                name="emailAddress"
                v-model="selectedClient.emailAddress"
                @input="handleInput"
                @emptied="resetComboBoxes"
            />
          </div>

          <div class="col-span-3 mt-10">
            <Button
                v-if="selectedClient.id !== null"
                text="Go To Client"
                class="btn-dark"
                @click="$router.push({path: `/clients/${selectedClient.id}`})"
            />
            <span v-else class="text-red-500">No client selected!</span>
          </div>

        </div>

      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
