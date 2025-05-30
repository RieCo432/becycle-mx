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

const toast = useToast();

export default {
  name: 'findBike',
  components: {
    DashButton,
    Button,
    ComboboxTextInput,
    Card,
  },
  data() {
    return {
      isInReadMode: false,
      bikeSuggestions: [],
      selectedBike: {
        make: null,
        model: null,
        colour: null,
        serialNumber: null,
        decals: null,
        id: null,
      },
      filtered_bike_suggestions: [],
    };
  },
  created() {
    this.fetchBikes = debounce(this.fetchBikes, 500, {leading: false, trailing: true});
    this.run_filter = debounce(this.run_filter, 200, {leading: true, trailing: true});
  },
  methods: {
    fetchBikes() {
      if ((
        (this.selectedBike.make ? this.selectedBike.make.length : 0) +
          (this.selectedBike.model ? this.selectedBike.model.length : 0) +
          (this.selectedBike.colour ? this.selectedBike.colour.length : 0) +
          (this.selectedBike.serialNumber ? this.selectedBike.serialNumber.length : 0)
      ) > 2) {
        requests.findBikes(
          this.selectedBike.make,
          this.selectedBike.model,
          this.selectedBike.colour,
          this.selectedBike.serialNumber,
          4).then((response) => {
          this.bikeSuggestions = response.data;
          this.run_filter();
        });
      }
    },
    selectBike(event, i) {
      this.selectedBike = this.filtered_bike_suggestions[i];
    },
    verifyBikeDetails(rfidTagSerialNumber) {
      requests.getBikeByRfidTagSerialNumber(rfidTagSerialNumber)
        .then((response) => {
          const bike = response.data;
          let allSame = true;
          allSame &= bike.make === this.selectedBike.make;
          allSame &= bike.model === this.selectedBike.model;
          allSame &= bike.colour === this.selectedBike.colour;
          allSame &= bike.decals === this.selectedBike.decals;
          allSame &= bike.serialNumber === this.selectedBike.serialNumber;
          allSame &= bike.id === this.selectedBike.id;
          if (!allSame) {
            toast.warning('Some of the bike details do not match with the recorded details', {timeout: 4000});
          }
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 1000});
        });
    },
    readBikeDetailsFromNfcTag() {
      this.isInReadMode = true;
      nfc.readBikeDetailsFromNfcTag()
        .then((response) => {
          if (response.bike) {
            const bike = response.bike;
            toast.success('Details read!', {timeout: 1000});
            this.selectedBike = bike;
            this.verifyBikeDetails(response.rfidTagSerialNumber);
          } else {
            toast.error('Some error occurred!', {timeout: 1000});
          }
        })
        .catch((err) => {
          toast.error(err.message, {timeout: 1000});
        })
        .finally(() => {
          this.isInReadMode = false;
        });
    },
    run_filter() {
      const bike = {
        make: this.selectedBike.make ? this.selectedBike.make : '',
        model: this.selectedBike.model ? this.selectedBike.model : '',
        colour: this.selectedBike.colour ? this.selectedBike.colour : '',
        serialNumber: this.selectedBike.serialNumber ? this.selectedBike.serialNumber : '',
      };
      levenshtein.filterSortObject(this.bikeSuggestions, bike, 4).then((result) => {
        this.filtered_bike_suggestions = result;
      });
    },
    handleInput() {
      this.fetchBikes();
      this.run_filter();
    },
  },
  computed: {
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
                label="Make"
                type="text"
                placeholder="Raleigh"
                name="make"
                v-model="selectedBike.make"
                @input="handleInput"
            />
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.model"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
                label="Model"
                type="text"
                placeholder="Chloe"
                name="model"
                v-model="selectedBike.model"
                @input="handleInput"
            />
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.colour"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
                label="Colour"
                type="text"
                placeholder="Pink"
                name="colour"
                v-model="selectedBike.colour"
                @input="handleInput"
            />
          </div>

          <div class="col-span-12 lg:col-span-6">
            <ComboboxTextInput
                :field-model-value="selectedBike.serialNumber"
                :suggestions="filteredBikeSuggestionsLegible"
                :selected-callback="selectBike"
                :allow-new=false
                label="Serial Number"
                type="text"
                placeholder="ABCD 1234"
                name="serialNumber"
                v-model="selectedBike.serialNumber"
                @input="handleInput"
            />
          </div>

          <div class="col-span-6 mt-10">
            <Button
                v-if="selectedBike.id !== null"
                text="Go To Bike"
                class="btn-dark"
                @click="$router.push({path: `/bikes/${selectedBike.id}`})"
            />
            <span v-else class="text-red-500">No bike selected!</span>
          </div>
          <div class="col-span-6 mt-10">
            <DashButton @click="readBikeDetailsFromNfcTag" :is-disabled="isInReadMode">Read From NFC Tag</DashButton>
          </div>

        </div>

      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
