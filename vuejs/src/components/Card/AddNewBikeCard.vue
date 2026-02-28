<script>
import Card from '@/components/Card/index.vue';
import ColourSetSuggestion from '@/components/ComboBoxColourPicker/ColourSetSuggestion.vue';
import DashButton from '@/components/Button/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import ComboboxColourPicker from '@/components/ComboBoxColourPicker/ComboboxColourPicker.vue';
import * as yup from 'yup';
import {ref} from 'vue';
import {useField, useForm} from 'vee-validate';
import {debounce} from 'lodash-es';
import requests from '@/requests';
import levenshtein from '@/util/levenshtein';
import Button from '@/components/Button/index.vue';
import colourSuggestionSort from '@/util/colourSuggestionSort';
import Select from '@/components/Select/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'AddNewBikeCard',
  components: {Select, Button, ComboboxColourPicker, TextInput, ComboboxTextInput, DashButton, ColourSetSuggestion, Card},
  emits: ['bikeAdded'],
  setup(props, context) {
    const makeSuggestions = ref([]);
    const modelSuggestions = ref([]);
    const coloursSuggestions = ref([]);
    const serialNumberSuggestions = ref([]);
    const dispositions = ref([
      {
        value: 'rental',
        label: 'Rental',
      }, {
        value: 'sale',
        label: 'Sale',
      },
    ]);

    const addBikeSchema = yup.object().shape({
      makeNotInList: yup.boolean(),
      make: yup
        .string()
        .required(' Make is required')
        .when('makeNotInList', {
          is: true,
          then: (schema) => schema,
          otherwise: (schema) => schema.oneOf(makeSuggestions.value, 'Please choose a value from the list, or add a new make.'),
        }),
      model: yup
        .string()
        .required(' Model is required ')
        .when('modelNotInList', {
          is: true,
          then: (schema) => schema,
          otherwise: (schema) => schema.oneOf(modelSuggestions.value, 'Please choose a value from the list, or add a new model.'),
        }),
      colours: yup
        .array()
        .required('Colour is required')
        .max(3, 'Maximum of 3 colours.')
        .min(1, 'Minimum of 1 colour.'),
      decals: yup.string().nullable(),
      serialNumber: yup.string().required(' Serial Number is required '),
      disposition: yup
        .string()
        .required(' Disposition is required ')
        .oneOf(dispositions.value.map((d) => d.value), 'Please choose a value from the list.'),
      roughValue: yup
        .number()
        .min(0, 'Rough Value must be positive')
        .nullable()
        .transform((value) => Number.isNaN(value) ? null : value ),
    });

    const {handleSubmit} = useForm({
      validationSchema: addBikeSchema,
      keepValuesOnUnmount: true,
    });

    const {value: make, errorMessage: makeError} = useField('make');
    const {value: makeNotInList} = useField('makeNotInList');
    const {value: model, errorMessage: modelError} = useField('model');
    const {value: modelNotInList} = useField('modelNotInList');
    const {value: colours, errorMessage: coloursError} = useField('colours');
    const {value: decals, errorMessage: decalsError} = useField('decals');
    const {value: serialNumber, errorMessage: serialNumberError} = useField('serialNumber');
    const {value: disposition, errorMessage: dispositionError} = useField('disposition');
    const {value: roughValue, errorMessage: roughValueError} = useField('roughValue');
    makeNotInList.value = false;
    modelNotInList.value = false;

    const submit = handleSubmit(() => {
      requests.postNewBike(
        make.value,
        model.value,
        colours.value,
        decals.value,
        serialNumber.value,
        disposition.value )
        .then((response) => {
          toast.success('New Bike Created!', {timeout: 2000});
          context.emit('bikeAdded', response.data);
        });
    });

    return {
      make,
      makeError,
      makeNotInList,
      model,
      modelError,
      modelNotInList,
      colours,
      coloursError,
      decals,
      decalsError,
      serialNumber,
      serialNumberError,
      disposition,
      dispositionError,
      roughValue,
      roughValueError,
      makeSuggestions,
      modelSuggestions,
      coloursSuggestions,
      serialNumberSuggestions,
      dispositions,

      submit,
    };
  },
  data() {
    return {
      filtered_make_suggestions: [],
      filtered_model_suggestions: [],
      filtered_colours_suggestions: [],
      filtered_serial_number_suggestions: [],
    };
  },
  created() {
    this.fetchBikeMakeSuggestions = debounce(this.fetchBikeMakeSuggestions, 500, {
      leading: true,
      trailing: true,
    });
    this.fetchBikeModelSuggestions = debounce(this.fetchBikeModelSuggestions, 500, {
      leading: true,
      trailing: true,
    });
    this.fetchSerialNumberSuggestions = debounce(this.fetchSerialNumberSuggestions, 500, {
      leading: true,
      trailing: true,
    });
    this.fetchColoursSuggestions = debounce(this.fetchColoursSuggestions, 500, {
      leading: true,
      trailing: true,
    });
  },
  methods: {
    fetchBikeMakeSuggestions() {
      requests.getBikeMakeSuggestions(this.make.toLowerCase(), 4).then((response) => {
        this.makeSuggestions = response.data;
      });
    },
    fetchBikeModelSuggestions() {
      requests.getBikeModelSuggestions(this.model.toLowerCase(), 4).then((response) => {
        this.modelSuggestions = response.data;
      });
    },
    fetchSerialNumberSuggestions() {
      requests.getBikeSerialNumberSuggestions(this.serialNumber.toLowerCase(), 4).then((response) => {
        this.serialNumberSuggestions = response.data;
      });
    },
    fetchColoursSuggestions() {
      if (this.colours && this.colours.length > 0) {
        requests.getBikeColoursSuggestions(this.colours.map((c) => c.hex).join('|'), 2).then((response) => {
          this.coloursSuggestions = response.data;
        });
      }
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
    filterAndSortColourSuggestions() {
      this.filtered_colours_suggestions = this.coloursSuggestions
        .toSorted((a, b) => colourSuggestionSort.colourSuggestionSort(a, b, this.colours)).slice(0, 6);
    },
  },
  watch: {
    make() {
      levenshtein.filterSort(this.makeSuggestions, this.make, 4).then((result) => {
        this.filtered_make_suggestions = result.slice(0, 6);
      });
    },
    model() {
      levenshtein.filterSort(this.modelSuggestions, this.model, 4).then((result) => {
        this.filtered_model_suggestions = result.slice(0, 6);
      });
    },
    colours() {
      this.filterAndSortColourSuggestions();
    },
    coloursSuggestions() {
      this.filterAndSortColourSuggestions();
    },
    serialNumber() {
      levenshtein.filterSort(this.serialNumberSuggestions, this.serialNumber, 4).then((result) => {
        this.filtered_serial_number_suggestions = result.slice(0, 6);
      });
    },
  },
};
</script>

<template>
  <Card title="Add Bike">
    <form @submit.prevent="submit" @keydown.enter="submit">
      <div class="grid grid-cols-6 gap-5">
        <div class="col-span-4">
          <ComboboxTextInput
            :allow-new="makeNotInList"
            :field-model-value="make"
            :suggestions="filtered_make_suggestions"
            :selected-callback="selectMake"
            label="Make"
            type="text"
            placeholder="Make"
            name="make"
            v-model="make"
            :error="makeError"
            @input="fetchBikeMakeSuggestions"
          />
        </div>
        <div class="col-span-2">
          <label
            class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
            Add New
          </label>
          <DashButton
            :class="`btn-sm ${makeNotInList ? 'bg-success-500 dark:bg-success-500' : 'bg-primary-500 dark:bg-primary-500'} w-full`"
            :icon="makeNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
            @click.prevent="() => {makeNotInList = !makeNotInList}"
          />
        </div>

        <div class="col-span-4">
          <ComboboxTextInput
            :allow-new="modelNotInList"
            :field-model-value="model"
            :suggestions="filtered_model_suggestions"
            :selected-callback="selectModel"
            label="Model"
            type="text"
            placeholder="Model"
            name="model"
            v-model="model"
            :error="modelError"
            @input="fetchBikeModelSuggestions"
          />
        </div>

        <div class="col-span-2">
          <label
            class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
            Add New
          </label>
          <DashButton
            :class="`btn-sm ${modelNotInList ? 'bg-success-500 dark:bg-success-500' : 'bg-primary-500 dark:bg-primary-500'} w-full`"
            :icon="modelNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
            @click.prevent="() => {modelNotInList = !modelNotInList}"
          />
        </div>


        <!-- TODO: colour suggestions should be shown as coloured dots -->
        <div class="col-span-6">
          <ComboboxColourPicker
            :suggestions="filtered_colours_suggestions"
            :selected-callback="selectColours"
            :allow-new=true
            :error="coloursError"
            label="Colours"
            name="colours"
            @update:modelValue="(newValue) => {fetchColoursSuggestions(); }"
            v-model="colours"
            @click.prevent="() => {}"
          >
            <template #suggestion="{ suggestion, active }">
              <ColourSetSuggestion
                :suggestion="suggestion"
                :active="active"/>
            </template>
          </ComboboxColourPicker>
        </div>

        <div class="col-span-6">
          <TextInput
            label="Decals"
            type="text"
            placeholder="Decals"
            name="decals"
            v-model="decals"
            :error="decalsError"
          />
        </div>

        <div class="col-span-6">
          <ComboboxTextInput
            :field-model-value="serialNumber"
            :suggestions="filtered_serial_number_suggestions"
            :selected-callback="selectSerialNumber"
            label="Serial Number"
            type="text"
            placeholder="Serial Number"
            name="serialnumber"
            v-model="serialNumber"
            :error="serialNumberError"
            @input="fetchSerialNumberSuggestions"
          />
        </div>

        <div class="col-span-6">
          <Select
            :options="dispositions"
            label="Disposition"
            v-model="disposition"
            name="tagId"
            :error="dispositionError"
          />
        </div>

        <div class="col-span-6">
          <TextInput
            label="Rough Value (£)"
            type="text"
            placeholder="40.00"
            name="roughValue"
            v-model="roughValue"
            :error="roughValueError"
          />
        </div>

        <div class="col-span-6">
          <Button
            text="Submit"
            btnClass="btn-dark"
          />
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
