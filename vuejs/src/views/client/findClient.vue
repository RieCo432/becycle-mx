<script>
import Card from '@/components/Card/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import Button from '@/components/Button/index.vue';

export default {
  name: 'findClient',
  components: {
    Button,
    ComboboxTextInput, Textinput,
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
    };
  },
  created() {
    this.fetchClients = debounce(this.fetchClients, 500, {leading: true, trailing: true});
  },
  methods: {
    fetchClients() {
      requests.findClient(this.selectedClient.firstName.toLowerCase(), this.selectedClient.lastName.toLowerCase(),
        this.selectedClient.emailAddress.toLowerCase()).then((response) => {
        this.clientSuggestions = response.data;
      });
    },
    selectClient(event, i) {
      this.selectedClient = this.filtered_client_suggestions[i];
    },
  },
  computed: {
    filtered_client_suggestions() {
      return this.clientSuggestions.filter((client) => (
        (client.firstName.startsWith(this.selectedClient.firstName.toLowerCase()) && (this.selectedClient.firstName.toLowerCase())) ||
          (client.lastName.startsWith(this.selectedClient.lastName.toLowerCase()) && (this.selectedClient.lastName.toLowerCase())) ||
          (client.emailAddress.startsWith(
            this.selectedClient.emailAddress.toLowerCase()) &&
              (this.selectedClient.emailAddress.toLowerCase()))
      ));
    },
    filteredClientSuggestionsLegible() {
      return this.filtered_client_suggestions.map((client) => (`${client.firstName} ${client.lastName} ${client.emailAddress}`));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 lg:col-span-8">
      <Card title="Find Client">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedClient.firstName"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
            >
              <Textinput
                  label="First Name"
                  type="text"
                  placeholder="First Name"
                  name="firstName"
                  v-model="selectedClient.firstName"
                  @input="fetchClients"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedClient.lastName"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
            >
              <Textinput
                  label="Last Name"
                  type="text"
                  placeholder="Last Name"
                  name="lastName"
                  v-model="selectedClient.lastName"
                  @input="fetchClients"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-12">
            <ComboboxTextInput
                :field-model-value="selectedClient.emailAddress"
                :suggestions="filteredClientSuggestionsLegible"
                :selected-callback="selectClient"
                :allow-new=false
            >
              <Textinput
                  label="Email Address"
                  type="text"
                  placeholder="Email Address"
                  name="emailAddress"
                  v-model="selectedClient.emailAddress"
                  @input="fetchClients"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-3 mt-10">
            <Button
              text="Confirm"
              class="btn-dark"
              @click="$router.push({path: `/clients/${selectedClient.id}`})"
            />
          </div>

        </div>

      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
