<script>
import Card from '@/components/Card/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import Button from '@/components/Button/index.vue';
import DashButton from '@/components/Button/index.vue';
import nfc from '@/nfc';
import {useToast} from 'vue-toastification';
import levenshtein from '@/util/levenshtein';
import BikeSuggestion from '@/components/ComboboxTextInput/BikeSuggestion.vue';
import ComboboxColourPicker from '@/components/ComboBoxColourPicker/ComboboxColourPicker.vue';
import ColourSetSuggestion from '@/components/ComboBoxColourPicker/ColourSetSuggestion.vue';
import TextInput from '@/components/TextInput/index.vue';
import colourSuggestionSort from '@/util/colourSuggestionSort';
import Checkbox from '@/components/Checkbox/index.vue';

const toast = useToast();

export default {
  name: 'BikeSearchCard',
  components: {
    Checkbox,
    TextInput, ColourSetSuggestion,
    ComboboxColourPicker,
    DashButton,
    Button,
    ComboboxTextInput,
    Card,
    BikeSuggestion,
  },
  props: {
    modelValue: {
      type: Array,
      required: true,
    },
  },
  emits: ['updateSearch'],
  data() {
    return {
      isInReadMode: false,
      bikeSuggestions: [],
      make: null,
      model: null,
      colours: null,
      serialNumber: null,
      decals: null,
      includeRental: true,
      includeSale: true,
      makeSuggestions: [],
      modelSuggestions: [],
      coloursSuggestions: [],
      serialNumberSuggestions: [],
      filtered_bike_suggestions: [],
      filtered_make_suggestions: [],
      filtered_model_suggestions: [],
      filtered_colours_suggestions: [],
      filtered_serial_number_suggestions: [],
    };
  },
  created() {
    this.fetchBikeMakeSuggestions = debounce(this.fetchBikeMakeSuggestions, 500, {leading: true, trailing: true});
    this.fetchBikeModelSuggestions = debounce(this.fetchBikeModelSuggestions, 500, {leading: true, trailing: true});
    this.fetchSerialNumberSuggestions = debounce(this.fetchSerialNumberSuggestions, 500, {leading: true, trailing: true});
    this.fetchColoursSuggestions = debounce(this.fetchColoursSuggestions, 500, {leading: true, trailing: true});
    this.fetchBikes = debounce(this.fetchBikes, 1000, {leading: false, trailing: true});
    this.run_filter = debounce(this.run_filter, 200, {leading: true, trailing: true});
  },
  methods: {
    fetchBikeMakeSuggestions() {
      requests.getBikeMakeSuggestions(this.make.toLowerCase(), 4).then((response) => {
        this.makeSuggestions = response.data;
      });
      this.handleInput();
    },
    fetchBikeModelSuggestions() {
      requests.getBikeModelSuggestions(this.model.toLowerCase(), 4).then((response) => {
        this.modelSuggestions = response.data;
      });
      this.handleInput();
    },
    fetchSerialNumberSuggestions() {
      requests.getBikeSerialNumberSuggestions(this.serialNumber.toLowerCase(), 4).then((response) => {
        this.serialNumberSuggestions = response.data;
      });
      this.handleInput();
    },
    fetchColoursSuggestions() {
      if (this.colours && this.colours.length > 0) {
        requests.getBikeColoursSuggestions(this.colours.map((c) => c.hex).join('|'), 2).then((response) => {
          this.coloursSuggestions = response.data;
        });
      }
      this.handleInput();
    },
    selectMake(event, i) {
      if (i !== -1) {
        this.make = this.filtered_make_suggestions[i];
      }
    },
    selectModel(event, i) {
      if (i !== -1) {
        this.model = this.filtered_model_suggestions[i];
      }
    },
    selectSerialNumber(event, i) {
      if (i !== -1) {
        this.serialNumber = this.filtered_serial_number_suggestions[i];
      }
    },
    selectColours(event, i) {
      if (i !== -1) {
        this.colours.splice(0, this.colours.length, ...this.filtered_colours_suggestions[i]);
      }
    },
    fetchBikes() {
      if ((
        (this.make ? this.make.length : 0) +
        (this.model ? this.model.length : 0) +
        (this.colours ? 3 : 0) +
        (this.serialNumber ? this.serialNumber.length : 0)
      ) > 2) {
        const dispositions = [];
        if (this.includeRental) dispositions.push('rental');
        if (this.includeSale) dispositions.push('sale');

        requests.findBikes(
          this.make,
          this.model,
          this.colour,
          this.colours ? this.colours.map((colour) => colour.hex) : null,
          this.serialNumber,
          dispositions,
          4).then((response) => {
          this.bikeSuggestions = response.data;
          this.run_filter();
        });
      }
    },

    run_filter() {
      const bike = {
        make: this.make ? this.make : '',
        model: this.model ? this.model : '',
        colours: this.colours ? this.colours : [],
        serialNumber: this.serialNumber ? this.serialNumber : '',
      };
      levenshtein.filterSortObject(
        this.bikeSuggestions
          .filter((b) =>
            (this.includeRental && b.disposition === 'rental') ||
            (!this.includeSale && b.disposition === 'sale')),
        bike,
        4).then((result) => {
        this.filtered_bike_suggestions = result;
        this.$emit('update:modelValue', this.filtered_bike_suggestions);
      });
    },
    handleInput() {
      this.$emit('updateSearch', {
        make: this.make,
        model: this.model,
        colours: this.colours,
        serialNumber: this.serialNumber,
      });
      this.run_filter();
      this.fetchBikes();
    },
    resetComboBoxes() {
      this.selectedBike = {
        make: '',
        model: '',
        colour: '',
        serialNumber: '',
        decals: '',
        id: '',
      };
      this.filtered_bike_suggestions = [];
    },
    filterAndSortColourSuggestions() {
      this.filtered_colours_suggestions = this.coloursSuggestions
        .toSorted((a, b) => colourSuggestionSort.colourSuggestionSort(a, b, this.colours)).slice(0, 6);
    },
    coloursChanged() {
      this.fetchColoursSuggestions();
      this.handleInput();
      this.filterAndSortColourSuggestions();
    },
  },
  watch: {
    make() {
      this.fetchBikeMakeSuggestions();
      this.handleInput();
      levenshtein.filterSort(this.makeSuggestions, this.make, 4).then((result) => {
        this.filtered_make_suggestions = result.slice(0, 6);
      });
    },
    model() {
      this.fetchBikeModelSuggestions();
      this.handleInput();
      levenshtein.filterSort(this.modelSuggestions, this.model, 4).then((result) => {
        this.filtered_model_suggestions = result.slice(0, 6);
      });
    },
    coloursSuggestions() {
      this.filterAndSortColourSuggestions();
    },
    serialNumber() {
      this.fetchSerialNumberSuggestions();
      this.handleInput();
      levenshtein.filterSort(this.serialNumberSuggestions, this.serialNumber, 4).then((result) => {
        this.filtered_serial_number_suggestions = result.slice(0, 6);
      });
    },
    includeRental() {
      this.handleInput();
    },
    includeSale() {
      this.handleInput();
    },
  },
};
</script>

<template>
  <Card title="Search Bikes">
    <div class="grid grid-cols-2 gap-5">
      <div class="col-span-2">
        <ComboboxTextInput
          :allow-new="false"
          :field-model-value="make"
          :suggestions="filtered_make_suggestions"
          :selected-callback="selectMake"
          label="Make"
          type="text"
          placeholder="Make"
          name="make"
          v-model="make"
        />
      </div>

      <div class="col-span-2">
        <ComboboxTextInput
          :allow-new="false"
          :field-model-value="model"
          :suggestions="filtered_model_suggestions"
          :selected-callback="selectModel"
          label="Model"
          type="text"
          placeholder="Model"
          name="model"
          v-model="model"
        />
      </div>

      <div class="col-span-2">
        <ComboboxColourPicker
          :suggestions="filtered_colours_suggestions"
          :selected-callback="selectColours"
          :allow-new=true
          label="Colours"
          name="colours"
          v-model="colours"
          @click.prevent="() => {}"
          @update:modelValue="coloursChanged"
        >
          <template #suggestion="{ suggestion, active }">
            <ColourSetSuggestion
              :suggestion="suggestion"
              :active="active"/>
          </template>
        </ComboboxColourPicker>
      </div>

      <div class="col-span-2">
        <TextInput
          label="Decals"
          type="text"
          placeholder="Decals"
          name="decals"
          v-model="decals"
        />
      </div>

      <div class="col-span-2">
        <ComboboxTextInput
          :field-model-value="serialNumber"
          :suggestions="filtered_serial_number_suggestions"
          :selected-callback="selectSerialNumber"
          label="Serial Number"
          type="text"
          placeholder="Serial Number"
          name="serialnumber"
          v-model="serialNumber"
        />
      </div>
      <div class="col">
        <Checkbox
          label="Include Rental"
          v-model="includeRental"
          activeClass="ring-primary-500 bg-primary-500"
        />
      </div>
      <div class="col">
        <Checkbox
          label="Include Sale"
          v-model="includeSale"
          activeClass="ring-primary-500 bg-primary-500"
        />
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>
