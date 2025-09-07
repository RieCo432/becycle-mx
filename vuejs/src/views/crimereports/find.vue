<script lang="ts">
import {defineComponent} from 'vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import Button from '@/components/Button/index.vue';
import {debounce} from 'lodash-es';
import requests from '@/requests/index';
import levenshtein from '@/util/levenshtein';


export default defineComponent({
  name: 'find.vue',
  components: {Button, Card, ComboboxTextInput},
  data() {
    return {
      crimeReportSuggestions: [],
      selectedCrimeReport: {
        crimeNumber: null,
        contractId: null,
        contract: {
          bike: {
            make: null,
            model: null,
            colour: null,
          },
          client: {
            firstName: null,
            lastName: null,
            emailAddress: null,
          },
        },
        id: null,
      },
      filtered_crime_report_suggestions: [],
    };
  },
  created() {
    this.fetchCrimeReports = debounce(this.fetchCrimeReports, 500, {leading: false, trailing: true});
    this.run_filter = debounce(this.run_filter, 200, {leading: true, trailing: true});
  },
  methods: {
    fetchCrimeReports() {
      if ((this.selectedCrimeReport.crimeNumber ? this.selectedCrimeReport.crimeNumber.length : 0) > 2) {
        requests.findCrimeReport(
          this.selectedCrimeReport.crimeNumber.toLowerCase().replace('-', '').replace(' ', ''))
          .then((response) => {
            this.crimeReportSuggestions = response.data;
            this.run_filter();
          });
      }
    },
    selectCrimeReport(event, i) {
      this.selectedCrimeReport = this.filtered_crime_report_suggestions[i];
    },
    run_filter() {
      const crimeReport = {
        crimeNumber: this.selectedCrimeReport.crimeNumber ?
          this.selectedCrimeReport.crimeNumber
            .toLowerCase()
            .replace(' ', '')
            .replace('-', '') :
          '',
      };
      levenshtein.filterSortObject(this.crimeReportSuggestions, crimeReport, 4).then((result) => {
        this.filtered_crime_report_suggestions = result;
      });
    },
    handleInput() {
      this.fetchCrimeReports();
      this.run_filter();
    },
    resetComboBoxes() {
      this.selectedCrimeReport = {
        crimeNumber: '',
        id: '',
      };
      this.filtered_crime_report_suggestions = [];
    },
  },
  computed: {
    filteredCrimeReportSuggestionsLegible() {
      return this.filtered_crime_report_suggestions.map((r) =>
        (`${r.crimeNumber}; Client: ${r.contract.client.firstName} ${r.contract.client.lastName}; Bike: ${r.contract.bike.make} ${r.contract.bike.model} ${r.contract.bike.colour}`),
      );
    },
  },
});
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 lg:col-span-6 lg:col-start-4">
      <Card title="Find Bike">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <ComboboxTextInput
                :field-model-value="selectedCrimeReport.crimeNumber"
                :suggestions="filteredCrimeReportSuggestionsLegible"
                :selected-callback="selectCrimeReport"
                :allow-new=false
                label="Crime Number"
                type="text"
                placeholder="PS-20250911-1234"
                name="crimeNumber"
                v-model="selectedCrimeReport.crimeNumber"
                @input="handleInput"
                @emptied="resetComboBoxes"
            />
          </div>

          <div class="col-span-6 mt-10">
            <Button
                v-if="selectedCrimeReport.id !== null"
                text="Go To Contract"
                class="btn-dark"
                @click="$router.push({path: `/contracts/${selectedCrimeReport.contractId}`})"
            />
            <span v-else class="text-red-500">No crime report selected!</span>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
