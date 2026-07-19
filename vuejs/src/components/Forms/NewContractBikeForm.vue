<script setup>

import Radio from '@/components/Radio/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import Checkbox from '@/components/Checkbox/index.vue';
import DashButton from '@/components/Button/index.vue';
import ComboboxColourPicker from '@/components/ComboBoxColourPicker/ComboboxColourPicker.vue';
import ColourSetSuggestion from '@/components/ComboBoxColourPicker/ColourSetSuggestion.vue';
import BikeOverviewCard from '@/components/Card/BikeOverviewCard.vue';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {onMounted, ref, watch} from 'vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {debounce} from 'lodash-es';
import requests from '@/requests';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';
import levenshtein from '@/util/levenshtein';
import colourSuggestionSort from '@/util/colourSuggestionSort';
import {useRoute} from 'vue-router';

const toast = useToast();
const route = useRoute();

const emit = defineEmits(['goBack', 'update:draft']);
const props = defineProps({
  draft: {
    type: Object,
    required: true,
  },
});

const bikeToBeLinked = ref(null);

const makeSuggestions = ref([]);
const modelSuggestions = ref([]);
const coloursSuggestions = ref([]);
const serialNumberSuggestions = ref([]);

const filteredMakeSuggestions = ref([]);
const filteredModelSuggestions = ref([]);
const filteredSerialNumberSuggestions = ref([]);
const filteredColoursSuggestions = ref([]);

const processingSubmit = ref(false);
function checkCurrentlyProcessing() {
  if (processingSubmit.value) {
    toast.warning('Please wait for the previous action to complete');
    return true;
  }
  return false;
}

const bikeSchema = yup.object().shape({
  makeNotInList: yup.boolean(),
  make: yup.string().required(' Make is required').when('makeNotInList', {
    is: true,
    then: (schema) => schema,
    otherwise: (schema) => schema.oneOf(makeSuggestions.value, 'Please choose a value from the list, or add a new make.'),
  }),
  model: yup.string().required(' Model is required ').when('modelNotInList', {
    is: true,
    then: (schema) => schema,
    otherwise: (schema) => schema.oneOf(modelSuggestions.value, 'Please choose a value from the list, or add a new model.'),
  }),
  colours: yup.array().required('Colour is required').max(3, 'Maximum of 3 colours.').min(1, 'Minimum of 1 colour.'),
  decals: yup.string().nullable(),
  serialNumber: yup.string().required(' Serial Number is required '),
  bikePhotoTaken: yup.boolean().oneOf([true], 'Must take a photo of the bike').required('Must take a photo of the bike'),
  stickerOnBike: yup.boolean()
    .oneOf([true], `Must put a ${import.meta.env.VITE_COMMON_NAME} sticker on bike`)
    .required(`Must put a ${import.meta.env.VITE_COMMON_NAME} sticker on bike`),
  matchWithBikeId: yup.string().required(' Select one option.'),
});

const {handleSubmit} = useForm({
  validationSchema: bikeSchema,
  keepValuesOnUnmount: true,
});

const {value: make, errorMessage: makeError} = useField('make');
const {value: makeNotInList} = useField('makeNotInList');
const {value: model, errorMessage: modelError} = useField('model');
const {value: modelNotInList} = useField('modelNotInList');
const {value: colours, errorMessage: coloursError} = useField('colours');
const {value: decals, errorMessage: decalsError} = useField('decals');
const {value: serialNumber, errorMessage: serialNumberError} = useField('serialNumber');
const {value: bikePhotoTaken, errorMessage: bikePhotoTakenError} = useField('bikePhotoTaken');
const {value: stickerOnBike, errorMessage: stickerOnBikeError} = useField('stickerOnBike');
const {value: matchWithBikeId, errorMessage: matchWithBikeIdError} = useField('matchWithBikeId');
makeNotInList.value = false;
modelNotInList.value = false;


function setDraftBike(bike) {
  requests.putDraftContractBike(props.draft.id, bike.id)
    .then((response) => {
      emit('update:draft', response.data);
      toast.success('Bike Updated!', {timeout: 5000});
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    })
    .finally(() => {
      processingSubmit.value = false;
    });
}

const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;

  if (matchWithBikeId.value === 'new') {
    requests.postNewBike(make.value, model.value, colours.value, decals.value, serialNumber.value, 'rental')
      .then((response) => {
        toast.success('New Bike Created!', {timeout: 1000});
        setDraftBike(response.data);
      })
      .catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
  } else {
    requests.getBike(matchWithBikeId.value)
      .then((response) => {
        setDraftBike(response.data);
      })
      .catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
  }
});

function filterAndSortColourSuggestions() {
  filteredColoursSuggestions.value = coloursSuggestions.value
    .toSorted((a, b) => colourSuggestionSort
      .colourSuggestionSort(a, b, colours.value))
    .slice(0, 6);
}


onMounted(() => {
  if (props.draft.bike) {
    console.log('mounted', props.draft.bike);
    make.value = props.draft.bike.make;
    makeNotInList.value = !makeSuggestions.value.includes(make.value);
    model.value = props.draft.bike.model;
    modelNotInList.value = !modelSuggestions.value.includes(model.value);
    colours.value = props.draft.bike.colours ?? [];
    decals.value = props.draft.bike.decals;
    serialNumber.value = props.draft.bike.serialNumber;
    bikePhotoTaken.value = props.draft.bikeId != null;
    stickerOnBike.value = props.draft.bikeId != null;
    bikeToBeLinked.value = props.draft.bike;
    matchWithBikeId.value = props.draft.bikeId;

    fetchMakeSuggestions();
    fetchModelSuggestions();
    fetchSerialNumberSuggestions();
    fetchColoursSuggestions();
  }
});

watch(props.draft, async (newValue) => {
  if (newValue.bike) {
    console.log('watch draft', newValue.bike);
    make.value = newValue.bike.make;
    model.value = newValue.bike.model;
    colours.value = newValue.bike.colours ?? [];
    decals.value = newValue.bike.decals;
    serialNumber.value = newValue.bike.serialNumber;
    bikePhotoTaken.value = newValue.bikeId != null;
    stickerOnBike.value = newValue.bikeId != null;
    bikeToBeLinked.value = newValue.bike;
    matchWithBikeId.value = newValue.bike.id;

    fetchMakeSuggestions();
    fetchModelSuggestions();
    fetchSerialNumberSuggestions();
    fetchColoursSuggestions();
  }
});

watch(make, async (newValue) => {
  tryMatchingBike();
  levenshtein.filterSort(makeSuggestions.value, make.value, 4)
    .then((result) => {
      filteredMakeSuggestions.value = result.slice(0, 6);
    });
});

watch(model, async (newValue) => {
  tryMatchingBike();
  levenshtein.filterSort(modelSuggestions.value, model.value, 4)
    .then((result) => {
      filteredModelSuggestions.value = result.slice(0, 6);
    });
});

watch(serialNumber, async (newValue) => {
  tryMatchingBike();
  levenshtein.filterSort(serialNumberSuggestions.value, serialNumber.value, 4)
    .then((result) => {
      filteredSerialNumberSuggestions.value = result.slice(0, 6);
    });
});

watch(colours, async (newValue) => {
  tryMatchingBike();
  filterAndSortColourSuggestions();
});


function tryMatchingBike() {
  if (make.value &&
    make.value !== '' &&
    model.value &&
    model.value !== '' &&
    colours.value &&
    colours.value.length > 0 &&
    serialNumber.value &&
    serialNumber.value !== '') {
    requests.findBike(make.value, model.value, colours.value.map((c) => c.hex).join('|'), serialNumber.value)
      .then((response) => {
        bikeToBeLinked.value = response.data;
      })
      .catch((error) => {
        if (error.response.status === 404) {
          bikeToBeLinked.value = null;
        }
      });
  }
}

function fetchMakeSuggestions() {
  if (make.value && make.value !== '') {
    requests.getBikeMakeSuggestions(make.value.toLowerCase(), 4)
      .then((response) => {
        makeSuggestions.value = response.data;
      });
  }
}
const fetchMakeSuggestionsDebounced = debounce(fetchMakeSuggestions, 500, {leading: true, trailing: true});

function fetchModelSuggestions() {
  if (model.value && model.value !== '') {
    requests.getBikeModelSuggestions(model.value.toLowerCase(), 4)
      .then((response) => {
        modelSuggestions.value = response.data;
      });
  }
}
const fetchModelSuggestionsDebounced = debounce(fetchModelSuggestions, 500, {leading: true, trailing: true});


function fetchSerialNumberSuggestions() {
  if (serialNumber.value && serialNumber.value !== '') {
    requests.getBikeSerialNumberSuggestions(serialNumber.value.toLowerCase(), 4)
      .then((response) => {
        serialNumberSuggestions.value = response.data;
      });
  }
}
const fetchSerialNumberSuggestionsDebounced = debounce(fetchSerialNumberSuggestions, 500, {leading: true, trailing: true});

function fetchColoursSuggestions() {
  if (colours.value && colours.value.length > 0) {
    requests.getBikeColoursSuggestions(colours.value.map((c) => c.hex)
      .join('|'), 2).then((response) => {
      coloursSuggestions.value = response.data;
    });
  }
}
const fetchColoursSuggestionsDebounced = debounce(fetchColoursSuggestions, 500, {leading: true, trailing: true});


function getEmptyBike() {
  return {
    make: null,
    model: null,
    colours: [],
    serialNumber: null,
    decals: null,
  };
}

function selectMake(event, i) {
  const draft = props.draft;
  if (draft.bike == null) draft.bike = getEmptyBike();
  if (i !== -1) {
    draft.bike.make = filteredMakeSuggestions.value[i];
  } else {
    draft.bike.make = make.value;
  }
  emit('update:draft', props.draft);
}

function selectModel(event, i) {
  const draft = props.draft;
  if (draft.bike == null) draft.bike = getEmptyBike();
  if (i !== -1) {
    draft.bike.model = filteredModelSuggestions.value[i];
  } else {
    draft.bike.model = model.value;
  }
  emit('update:draft', props.draft);
}

function selectSerialNumber(event, i) {
  const draft = props.draft;
  if (draft.bike == null) draft.bike = getEmptyBike();
  if (i !== -1) {
    draft.bike.serialNumber = filteredSerialNumberSuggestions.value[i];
  } else {
    draft.bike.serialNumber = serialNumber.value;
  }
  emit('update:draft', props.draft);
}

function selectColours(event, i) {
  const draft = props.draft;
  if (draft.bike == null) draft.bike = getEmptyBike();
  if (i !== -1) {
    draft.bike.colours = filteredColoursSuggestions.value[i];
  } else {
    draft.bike.colours = colours.value;
  }
  emit('update:draft', props.draft);
}

if (route.query.bikeId) {
  requests.getBike(route.query.bikeId)
    .then((response) => {
      const draft = props.draft;
      draft.bike = response.data;
      bikeToBeLinked.value = response.data;
      emit('update:draft', draft);
      makeSuggestions.value.push(response.data.make);
      modelSuggestions.value.push(response.data.model);
      matchWithBikeId.value = response.data.id;
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    });
}

function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}


</script>

<template>
  <form @submit.prevent="submit" @keydown.enter="() => {}">
    <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
      <div class="col-span-full row-start-1">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Enter the bike's details
        </h4>
      </div>
      <div class="col-span-4 xl:col-span-3 xl:row-start-2">
        <ComboboxTextInput
          :allow-new="makeNotInList"
          :field-model-value="make"
          :suggestions="filteredMakeSuggestions"
          :selected-callback="selectMake"
          label="Make"
          type="text"
          placeholder="Make"
          name="make"
          v-model="make"
          :error="makeError"
          @input="fetchMakeSuggestionsDebounced"
        />
      </div>
      <div class="col-span-2 xl:col-span-1 xl:row-start-2">
        <label
          class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
          Add New
        </label>
        <DashButton
          :class="`btn-sm ${makeNotInList
                            ? 'bg-success-500 dark:bg-success-500'
                            : 'bg-primary-500 dark:bg-primary-500'} w-full`"
          :icon="makeNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
          @click.prevent="() => {makeNotInList = !makeNotInList}"
        />
      </div>
      <div class="col-span-4 xl:col-span-3 xl:row-start-2">
        <ComboboxTextInput
          :allow-new="modelNotInList"
          :field-model-value="model"
          :suggestions="filteredModelSuggestions"
          :selected-callback="selectModel"
          label="Model"
          type="text"
          placeholder="Model"
          name="model"
          v-model="model"
          :error="modelError"
          @input="fetchModelSuggestionsDebounced"
        />
      </div>
      <div class="col-span-2 xl:col-span-1 xl:row-start-2">
        <label
          class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
          Add New
        </label>
        <DashButton
          :class="`btn-sm ${modelNotInList
                            ? 'bg-success-500 dark:bg-success-500'
                            : 'bg-primary-500 dark:bg-primary-500'} w-full`"
          :icon="modelNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
          @click.prevent="() => {modelNotInList = !modelNotInList}"
        />
      </div>
      <div class="col-span-6 xl:col-span-4 xl:row-span-4 xl:row-start-3 col-start-1">
        <ComboboxColourPicker
          :suggestions="filteredColoursSuggestions"
          :selected-callback="selectColours"
          :allow-new=true
          :error="coloursError"
          label="Colours"
          name="colours"
          @update:modelValue="(newValue) => {fetchColoursSuggestionsDebounced(); }"
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
      <div class="col-span-6 xl:col-span-4 xl:col-start-5 xl:row-start-3">
        <TextInput
          label="Decals"
          type="text"
          placeholder="Decals"
          name="decals"
          v-model="decals"
          :error="decalsError"
        />
      </div>
      <div class="col-span-6 xl:col-span-4 xl:col-start-5 xl:row-start-4">
        <ComboboxTextInput
          :field-model-value="serialNumber"
          :suggestions="filteredSerialNumberSuggestions"
          :selected-callback="selectSerialNumber"
          label="Serial Number"
          type="text"
          placeholder="Serial Number"
          name="serialnumber"
          v-model="serialNumber"
          :error="serialNumberError"
          @input="fetchSerialNumberSuggestionsDebounced"
        />
      </div>
      <div class="col-span-6 xl:col-span-4 xl:row-span-5 xl:col-start-9 xl:row-start-2">
        <BikeOverviewCard
          :bike="bikeToBeLinked"
          :bike-search="{
                            make: make,
                            model: model,
                            decals: decals,
                            colours: colours,
                            serialNumber: serialNumber
                          }"/>
      </div>
      <div class="col-span-6 xl:col-span-4 xl:col-start-9 xl:row-start-7">
        <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Use this bike or create new?</h5>
        <Radio
          v-if="bikeToBeLinked"
          label="Use this bike"
          class="mb-5"
          name="matchWithBikeId"
          v-model="matchWithBikeId"
          :value="bikeToBeLinked.id"
        />
        <Radio
          label="Create New Bike"
          class="mb-5"
          name="matchWithBikeId"
          v-model="matchWithBikeId"
          value="new"
        />
        <ErrorMessage name="matchWithBikeId" :error="matchWithBikeIdError" class="text-danger-500"/>
      </div>
      <div class="col-span-6 xl:col-span-2 xl:col-start-5 xl:row-start-5">
        <Checkbox
          label="Photo of bike taken?"
          name="bikePhotoTaken"
          activeClass="ring-primary-500 bg-primary-500"
          v-model="bikePhotoTaken"
          :error="bikePhotoTakenError"/>
        <ErrorMessage name="bikePhotoTaken" :error="bikePhotoTakenError" class="text-danger-500"/>
      </div>
      <div class="col-span-6 xl:col-span-2 xl:col-start-7 xl:row-start-5">
        <Checkbox
          label="Sticker on bike?"
          name="stickerOnBike"
          activeClass="ring-primary-500 bg-primary-500"
          v-model="stickerOnBike"
          :error="stickerOnBikeError"/>
        <ErrorMessage name="stickerOnBike" :error="stickerOnBikeError" class="text-danger-500"/>
      </div>
      <div class="col-span-full">
        <FormStepNavigation
          :processing-submit="processingSubmit"
          :submit="submit"
          :goBack="goBack"/>
      </div>
    </div>
  </form>
</template>

<style scoped lang="scss">

</style>
