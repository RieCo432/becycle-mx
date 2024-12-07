<script>
import Card from '@/components/Card/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import Button from '@/components/Button/index.vue';

export default {
  name: 'findBike',
  components: {
    Button,
    ComboboxTextInput, Textinput,
    Card,
  },
  data() {
    return {
      bikeSuggestions: [],
      selectedBike: {
        make: null,
        model: null,
        colour: null,
        serialNumber: null,
        decals: null,
        id: null,
      },
    };
  },
  created() {
    this.fetchBikes = debounce(this.fetchBikes, 500, {leading: true, trailing: true});
  },
  methods: {
    fetchBikes() {
      requests.findBikes(
          this.selectedBike.make,
          this.selectedBike.model,
          this.selectedBike.colour,
          this.selectedBike.serialNumber).then((response) => {
        this.bikeSuggestions = response.data;
      });
    },
    selectBike(event, i) {
      this.selectedBike = this.filtered_bike_suggestions[i];
    },
  },
  computed: {
    filtered_bike_suggestions() {
      return this.bikeSuggestions.filter((bike) => (
        (!this.selectedBike.make || bike.make.startsWith(this.selectedBike.make.toLowerCase())) &&
        (!this.selectedBike.model || bike.model.startsWith(this.selectedBike.model.toLowerCase())) &&
        (!this.selectedBike.colour || bike.colour.startsWith(this.selectedBike.colour.toLowerCase())) &&
        (!this.selectedBike.serialNumber || bike.serialNumber.startsWith(this.selectedBike.serialNumber.toLowerCase()))
      ));
    },
    filteredBikeSuggestionsLegible() {
      return this.filtered_bike_suggestions.map((bike) => (`${bike.make} ${bike.model} ${bike.colour} ${bike.serialNumber}`));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 lg:col-span-8">
      <Card title="Find Bike">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.make"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
            >
              <Textinput
                  label="Make"
                  type="text"
                  placeholder="Raleigh"
                  name="make"
                  v-model="selectedBike.make"
                  @input="fetchBikes"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.model"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
            >
              <Textinput
                  label="Model"
                  type="text"
                  placeholder="Chloe"
                  name="model"
                  v-model="selectedBike.model"
                  @input="fetchBikes"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.colour"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
            >
              <Textinput
                  label="Colour"
                  type="text"
                  placeholder="Pink"
                  name="colour"
                  v-model="selectedBike.colour"
                  @input="fetchBikes"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.serialNumber"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
            >
              <Textinput
                  label="Serial Number"
                  type="text"
                  placeholder="ABCD 1234"
                  name="serialNumber"
                  v-model="selectedBike.serialNumber"
                  @input="fetchBikes"
              />
            </ComboboxTextInput>
          </div>

          <div class="col-span-3 mt-10">
            <Button
                text="Confirm"
                class="btn-dark"
                @click="$router.push({path: `/bikes/${selectedBike.id}`})"
            />
          </div>

        </div>

      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
