<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="New Contract">
        <div>
          <div class="flex z-[5] items-center relative justify-center md:mx-8">
            <div
                class="relative z-[1] items-center item flex flex-start flex-1 last:flex-none group"
                v-for="(item, i) in steps"
                :key="i"
            >
              <div
                  :class="`   ${
            stepNumber >= i
              ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500 ' +
                'dark:bg-slate-900 dark:ring-slate-900'
              : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 ' +
                'dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
          }`"
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col
                         items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
              >
                <span v-if="stepNumber <= i"> {{ i + 1 }}</span>
                <span v-else class="text-3xl">
            <Icon icon="bx:check-double" />
          </span>
              </div>

              <div
                  class="absolute top-1/2 h-[2px] w-full"
                  :class="
            stepNumber >= i
              ? 'bg-slate-900 dark:bg-slate-900'
              : 'bg-[#E0EAFF] dark:bg-slate-700'
          "
              ></div>
              <div
                  class="absolute top-full text-base md:leading-6 mt-3 transition duration-150
                         md:opacity-100 opacity-0 group-hover:opacity-100"
                  :class="
            stepNumber >= i
              ? ' text-slate-900 dark:text-slate-300'
              : 'text-slate-500 dark:text-slate-300 dark:text-opacity-40'
          "
              >
                <span class="w-max">{{ item.title }}</span>
              </div>
            </div>
          </div>

          <div
              class="content-box mt-14 border-t border-slate-100 dark:border-slate-700 -mx-6 px-6 pt-6"
          >
            <form @submit.prevent="submit" @keydown.enter="submit">
              <div v-if="stepNumber === 0">
                <div class="grid grid-cols-1 2xl:grid-cols-2 gap-5">
                  <div class="col-span-1">
                    <h4 class="text-slate-800 dark:text-slate-300 mb-6">
                      Create a New Contract or choose a draft to continue.
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <DashButton @click="startNewDraft">Create New</DashButton>
                  </div>
                  <template v-for="draft in contractDrafts" :key="draft.id">
                    <div class="col-span-1">
                      <ContractDraftCard
                          :draft="draft"
                          :continue-draft-function="continueDraft"
                          />
                    </div>
                  </template>
                </div>
              </div>
              <div v-if="stepNumber === 1">
                <div class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-2 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Enter the Lendee's Information
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="emailAddress"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient"
                        label="Email" type="email" placeholder="Type your email"
                        name="emailAddress"
                        v-model="emailAddress"
                        :error="emailAddressError"
                        @input="fetchClientSuggestions"
                        @emptied="resetClientComboBoxes"
                    />
                  </div>

                  <div class="col-span-1">
                    <TextInput
                        label="Confirm Email"
                        type="email"
                        placeholder="Confirm your email"
                        name="confirmEmailAddress"
                        v-model="confirmEmailAddress"
                        :error="confirmEmailAddressError"
                    />
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="firstName"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient"
                        label="First name"
                        type="text"
                        placeholder="First name"
                        name="firstname"
                        v-model="firstName"
                        :error="firstNameError"
                        @input="fetchClientSuggestions"
                        @emptied="resetClientComboBoxes"
                    />
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="lastName"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient"
                        label="Last name"
                        type="text"
                        placeholder="Last name"
                        name="lastname"
                        v-model="lastName"
                        :error="lastNameError"
                        @input="fetchClientSuggestions"
                        @emptied="resetClientComboBoxes"
                    />
                  </div>
                </div>
              </div>
              <div v-if="stepNumber === 2">
                <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
                  <div class="col-span-full row-start-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Enter the bike's details
                    </h4>
                  </div>
<!--                  <div class="col-span-full">-->
<!--                    <DashButton class="block-btn" @click="readBikeDetailsFromNfcTag" :is-disabled="isNfcActive">-->
<!--                      Read From NFC Tag-->
<!--                    </DashButton>-->
<!--                  </div>-->
                  <div class="col-span-4 xl:col-span-3 xl:row-start-2">
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
                  <div class="col-span-2 xl:col-span-1 xl:row-start-2">
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

                  <div class="col-span-4 xl:col-span-3 xl:row-start-2">
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

                  <div class="col-span-2 xl:col-span-1 xl:row-start-2">
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
                  <div class="col-span-6 xl:col-span-4 xl:row-span-4 xl:row-start-3 col-start-1">
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


<!--                  <div class="col-span-full">-->
<!--                    <DashButton class="block-btn" @click="writeBikeDetailsToNfcTag" :is-disabled="isNfcActive">-->
<!--                      Write To NFC Tag-->
<!--                    </DashButton>-->
<!--                  </div>-->

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
                </div>
              </div>
              <div v-if="stepNumber === 3">
                <div class="grid lg:grid-cols-6 md:grid-cols-4 grid-cols-2 gap-5">
                  <div class="lg:col-span-6 md:col-span-4 col-span-2">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Additional Contract Information
                    </h4>
                  </div>

                  <div class="col-span-1">
                    <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Contract Type</h5>
                    <Radio
                        v-for="(contractType, i) in contractTypes"
                        :key="i"
                        :label="contractType"
                        class="mb-5"
                        name="contracttype"
                        v-model="type"
                        :value="contractType"
                    />
                    <ErrorMessage name="type" :error="typeError" class="text-danger-500"/>
                  </div>

                  <div class="col-span-1">
                    <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Bike Condition</h5>
                    <Radio
                        v-for="(bikeCondition, i) in bikeConditions"
                        :key="i"
                        :label="bikeCondition"
                        class="mb-5"
                        name="bikecondition"
                        v-model="condition"
                        :value="bikeCondition"
                    />
                    <ErrorMessage name="condition" :error="conditionError" class="text-danger-500"/>
                  </div>

                  <div class="md:col-span-4 col-span-2">
                <Textarea
                    label="Notes"
                    type="text"
                    placeholder="anything noteworth"
                    name="notes"
                    v-model="notes"
                    :error="notesError"
                />
                  </div>
                </div>
              </div>
              <div v-if="stepNumber === 4">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Deposit Collection
                    </h4>
                  </div>


                  <TextInput
                      label="Deposit Amount (&pound;)"
                      type="number"
                      placeholder="40"
                      name="depositAmountCollected"
                      v-model="depositAmountCollected"
                      :error="depositAmountCollectedError"
                  />

                  <ComboboxTextInput
                      :field-model-value="depositCollectingUser"
                      :suggestions="filtered_deposit_collecting_user_suggestions"
                      :selected-callback="selectDepositCollectingUser"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Deposit Collector"
                      type="text"
                      placeholder="workshop"
                      name="depositCollectingUser"
                      v-model="depositCollectingUser"
                      :error="depositCollectingUserError"
                      @change="() => {}"
                  />

                  <TextInput
                      label="Deposit Collector Password"
                      type="password"
                      placeholder="Password"
                      name="depositCollectingPassword"
                      v-model="depositCollectingPassword"
                      :error="depositCollectingPasswordError"
                      hasicon/>
                </div>
              </div>

              <div v-if="stepNumber === 5">
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Main Mechanic
                    </h4>
                  </div>

                  <ComboboxTextInput
                      :field-model-value="workingUser"
                      :suggestions="filtered_working_user_suggestions"
                      :selected-callback="selectWorkingUser"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Working Volunteer"
                      type="text"
                      placeholder="workshop"
                      name="workingUser"
                      v-model="workingUser"
                      :error="workingUserError"
                      @change="() => {}"
                  />

                  <TextInput
                      label="Working User Password or Pin"
                      type="password"
                      placeholder="Password or Pin"
                      name="workingUserPasswordOrPin"
                      v-model="workingPasswordOrPin"
                      :error="workingPasswordOrPinError"
                      hasicon/>
                </div>
              </div>
              <div v-if="stepNumber === 6">
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">

                  <div class="col-span-full grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Front Wheel?"
                          name="mCheckFrontWheelHub"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckFrontWheelHub"
                          :error="mCheckFrontWheelHubError"/>
                      <ErrorMessage name="mCheckFrontWheelHub" :error="mCheckFrontWheelHubError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Front Tire?"
                          name="mCheckFrontWheelTire"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckFrontWheelTire"
                          :error="mCheckFrontWheelTireError"/>
                      <ErrorMessage name="mCheckFrontWheelTire" :error="mCheckFrontWheelTireError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Rear Wheel?"
                          name="mCheckRearWheelHub"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckRearWheelHub"
                          :error="mCheckRearWheelHubError"/>
                      <ErrorMessage name="mCheckRearWheelHub" :error="mCheckRearWheelHubError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Rear Tire?"
                          name="mCheckRearWheelTire"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckRearWheelTire"
                          :error="mCheckRearWheelTireError"/>
                      <ErrorMessage name="mCheckRearWheelTire" :error="mCheckRearWheelTireError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Bottom Bracket?"
                          name="mCheckBottomBracket"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckBottomBracket"
                          :error="mCheckBottomBracketError"/>
                      <ErrorMessage name="mCheckBottomBracket" :error="mCheckBottomBracketError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Front Brake?"
                          name="mCheckFrontBrake"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckFrontBrake"
                          :error="mCheckFrontBrakeError"/>
                      <ErrorMessage name="mCheckFrontBrake" :error="mCheckFrontBrakeError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Rear Brake?"
                          name="mCheckRearBrake"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckRearBrake"
                          :error="mCheckRearBrakeError"/>
                      <ErrorMessage name="mCheckRearBrake" :error="mCheckRearBrakeError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Seat Post?"
                          name="mCheckSeatPost"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckSeatPost"
                          :error="mCheckSeatPostError"/>
                      <ErrorMessage name="mCheckSeatPost" :error="mCheckSeatPostError" class="text-danger-500"/>
                    </div>
                    <div class="col-span-1">
                      <Checkbox
                          label="M Check: Headset?"
                          name="mCheckHeadset"
                          activeClass="ring-primary-500 bg-primary-500"
                          v-model="mCheckHeadset"
                          :error="mCheckHeadsetError"/>
                      <ErrorMessage name="mCheckHeadset" :error="mCheckHeadsetError" class="text-danger-500"/>
                    </div>
                  </div>
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Checking Volunteer
                    </h4>
                  </div>

                  <ComboboxTextInput
                      :field-model-value="checkingUser"
                      :suggestions="filtered_checking_user_suggestions"
                      :selected-callback="selectCheckingUser"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Safety Checking User"
                      type="text"
                      placeholder="workshop"
                      name="checkingUser"
                      v-model="checkingUser"
                      :error="checkingUserError"
                      @change="() => {}"
                  />

                  <TextInput
                      label="Checking User Password or Pin"
                      type="password"
                      placeholder="Password Or Pin"
                      name="checkingPasswordOrPin"
                      v-model="checkingPasswordOrPin"
                      :error="checkingPasswordOrPinError"
                      hasicon/>
                </div>
              </div>
              <div
                  class="mt-10"
                  :class="stepNumber > 0 ? 'flex justify-between' : ' text-right'"
              >
                <Button
                    @click.prevent="prev()"
                    text="prev"
                    btnClass="btn-dark"
                    v-if="this.stepNumber !== 0"
                />
                <Button
                    v-if="stepNumber !== 0"
                    :text="stepNumber !== this.steps.length - 1 ? 'next' : 'submit'"
                    btnClass="btn-dark"
                />
              </div>
            </form>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
<script>
import Card from '@/components/Card';
import Button from '@/components/Button';
import Icon from '@/components/Icon';
import Textarea from '@/components/Textarea';
import TextInput from '@/components/TextInput';
import Radio from '@/components/Radio/index.vue';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {computed, nextTick, ref} from 'vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Checkbox from '@/components/Checkbox/index.vue';
import {useRouter} from 'vue-router';
import DashButton from '@/components/Button/index.vue';
// import nfc from '@/nfc';
import levenshtein from '@/util/levenshtein';
import ComboboxColourPicker from '@/components/ComboBoxColourPicker/ComboboxColourPicker.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import ColourSetSuggestion from '@/components/ComboBoxColourPicker/ColourSetSuggestion.vue';
import colourSuggestionSort from '@/util/colourSuggestionSort';
import ContractDraftCard from '@/components/Card/ContractDraftCard.vue';
import BikeOverviewCard from '@/components/Card/BikeOverviewCard.vue';

const toast = useToast();
const OFFICIAL_NAME = import.meta.env.VITE_OFFICIAL_NAME;

export default {
  name: 'newContract',
  components: {
    BikeOverviewCard,
    ContractDraftCard,
    ColourSetSuggestion,
    Tooltip,
    ComboboxColourPicker,
    DashButton,
    Checkbox,
    ErrorMessage,
    Card,
    Button,
    Icon,
    TextInput,
    Textarea,
    ComboboxTextInput,
    Radio,
  },
  setup() {
    const steps = [
      {
        id: 1,
        title: 'Start',
      },
      {
        id: 2,
        title: 'Client Details',
      },
      {
        id: 3,
        title: 'Bike Details',
      },
      {
        id: 4,
        title: 'Contract Details',
      },
      {
        id: 5,
        title: 'Deposit',
      },
      {
        id: 6,
        title: 'Mechanic',
      },
      {
        id: 7,
        title: 'Safety Check',
      },
    ];

    const contractTypes = ref([]);
    requests.getContractTypes().then((response) => (contractTypes.value = response.data.map((t) => (t.id))));

    const bikeConditions = ref([]);
    requests.getBikeConditions().then((response) => (bikeConditions.value = response.data));

    const contractDrafts = ref([]);
    const activeDraft = ref({});

    const toast = useToast();
    const stepNumber = ref(0);

    const clientId = ref('');
    const bikeId = ref('');

    const bikeToBeLinked = ref(null);

    const makeSuggestions = ref([]);
    const modelSuggestions = ref([]);
    const coloursSuggestions = ref([]);
    const serialNumberSuggestions = ref([]);

    const depositBearers = ref([]);
    const rentalCheckers = ref([]);
    const activeUsers = ref([]);

    const router = useRouter();

    const userSelectionOptionsStatic = ref(true);

    // step by step yup schema
    const clientSchema = yup.object().shape({
      firstName: yup.string().required('First name is required'),
      lastName: yup.string().required('Last name is required'),
      emailAddress: yup
        .string()
        .email('Email is not valid')
        .required('Email is required'),
      confirmEmailAddress: yup
        .string()
        .email('Email is not valid')
        .required('Confirm Email is required')
        .oneOf([yup.ref('emailAddress')], 'Email Addresses must match'),
    });

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

    const contractSchema = yup.object().shape({
      type: yup.string().required(' Type is required'),
      condition: yup.string().required(' Condition is required '),
      notes: yup.string().nullable(),
    });

    const depositCollectionSchema = yup.object().shape({
      depositAmountCollected: yup.number().min(0, 'Must not be negative').integer().required(' Deposit Amount is required '),
      depositCollectingUser: yup.string().required(' Deposit Collector Username is required '),
      depositCollectingPassword: yup.string().required(),
    });

    const workingUserSchema = yup.object().shape({
      workingUser: yup.string().required(' Main mechanic Username is required '),
      workingPasswordOrPin: yup.string().required(' Password or Pin is required '),
    });

    const checkingUserSchema = yup.object().shape({
      checkingUser: yup.string().required(' Checking Username is required ')
        .notOneOf([yup.ref('workingUser')], 'Checking volunteer must be different from working volunteer'),
      checkingPasswordOrPin: yup.string().required(' Password or Pin is required '),
      mCheckFrontWheelHub: yup.boolean().oneOf([true],
        'Is there no play in the front wheel and is it tightened correctly?')
        .required('Is there no play in the front wheel and is it tightened correctly?'),
      mCheckFrontWheelTire: yup.boolean().oneOf([true],
        'Is the front tire in good condition and seated correctly?')
        .required('Is the front tire in good condition and seated correctly?'),
      mCheckRearWheelHub: yup.boolean().oneOf([true],
        'Is there no play in the rear wheel and is it tightened correctly?')
        .required('Is there no play in the rear wheel and is it tightened correctly?'),
      mCheckRearWheelTire: yup.boolean().oneOf([true],
        'Is the rear tire in good condition and seated correctly?')
        .required('Is the rear tire in good condition and seated correctly?'),
      mCheckBottomBracket: yup.boolean().oneOf([true],
        'Is there no play in the bottom bracket and does it spin easily and smoothly?')
        .required('Is there no play in the bottom bracket and does it spin easily and smoothly?'),
      mCheckFrontBrake: yup.boolean().oneOf([true],
        'Is the front brake working fully?')
        .required('Is the front brake working fully?'),
      mCheckRearBrake: yup.boolean().oneOf([true], 'Is the rear brake working fully?')
        .required('Is the rear brake working fully?'),
      mCheckSeatPost: yup.boolean().oneOf([true],
        'Is the seat post set to correct height and properly tightened?')
        .required('Is the seat post set to correct height and properly tightened?'),
      mCheckHeadset: yup.boolean().oneOf([true],
        'Is there no play in the headset, does it steer easily and smoothly, and does it resist twisting?')
        .required('Is there no play in the headset, does it steer easily and smoothly, and does it resist twisting?'),
    });


    // find current step schema
    const currentSchema = computed(() => {
      switch (stepNumber.value) {
      case 1:
        return clientSchema;
      case 2:
        return bikeSchema;
      case 3:
        return contractSchema;
      case 4:
        return depositCollectionSchema;
      case 5:
        return workingUserSchema;
      case 6:
        return checkingUserSchema;
      default:
        return clientSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: emailAddress, errorMessage: emailAddressError, setValue: emailAddressSetValue} = useField('emailAddress');
    const {value: confirmEmailAddress, errorMessage: confirmEmailAddressError, setValue: confirmEmailAddressSetValue} =
        useField('confirmEmailAddress');
    const {value: firstName, errorMessage: firstNameError, setValue: firstNameSetValue} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError, setValue: lastNameSetValue} = useField('lastName');

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

    const {value: type, errorMessage: typeError} = useField('type');
    const {value: condition, errorMessage: conditionError} = useField('condition');
    const {value: notes, errorMessage: notesError} = useField('notes');

    const {value: depositAmountCollected, errorMessage: depositAmountCollectedError} = useField('depositAmountCollected');
    const {value: depositCollectingUser, errorMessage: depositCollectingUserError} = useField('depositCollectingUser');
    const {value: depositCollectingPassword, errorMessage: depositCollectingPasswordError,
      setErrors: depositCollectingPasswordSetErrors} = useField('depositCollectingPassword');

    const {value: workingUser, errorMessage: workingUserError} = useField('workingUser');
    const {value: workingPasswordOrPin, errorMessage: workingPasswordOrPinError,
      setErrors: workingPasswordOrPinSetErrors} = useField('workingPasswordOrPin');

    const {value: checkingUser, errorMessage: checkingUserError} = useField('checkingUser');
    const {value: checkingPasswordOrPin, errorMessage: checkingPasswordOrPinError,
      setErrors: checkingPasswordOrPinSetErrors} = useField('checkingPasswordOrPin');
    const {value: mCheckFrontWheelHub, errorMessage: mCheckFrontWheelHubError} = useField('mCheckFrontWheelHub');
    const {value: mCheckFrontWheelTire, errorMessage: mCheckFrontWheelTireError} = useField('mCheckFrontWheelTire');
    const {value: mCheckRearWheelHub, errorMessage: mCheckRearWheelHubError} = useField('mCheckRearWheelHub');
    const {value: mCheckRearWheelTire, errorMessage: mCheckRearWheelTireError} = useField('mCheckRearWheelTire');
    const {value: mCheckBottomBracket, errorMessage: mCheckBottomBracketError} = useField('mCheckBottomBracket');
    const {value: mCheckFrontBrake, errorMessage: mCheckFrontBrakeError} = useField('mCheckFrontBrake');
    const {value: mCheckRearBrake, errorMessage: mCheckRearBrakeError} = useField('mCheckRearBrake');
    const {value: mCheckSeatPost, errorMessage: mCheckSeatPostError} = useField('mCheckSeatPost');
    const {value: mCheckHeadset, errorMessage: mCheckHeadsetError} = useField('mCheckHeadset');

    depositCollectingUser.value = '';
    workingUser.value = '';
    checkingUser.value = '';

    function workingUserSelected() {
      workingPasswordOrPin.value = null;
      if (workingUser.value === depositCollectingUser.value) {
        workingPasswordOrPin.value = depositCollectingPassword.value;
      }
    }
    function checkingUserSelected() {
      checkingPasswordOrPin.value = null;
      if (checkingUser.value === depositCollectingUser.value) {
        checkingPasswordOrPin.value = depositCollectingPassword.value;
      }
    }

    function setClient() {
      if (clientId.value !== null && clientId.value !== '') {
        requests.putDraftContractClient(activeDraft.value.id, clientId.value)
          .then((response) => {
            stepNumber.value = 2;
            activeDraft.value = response.data;
            toast.success('Client Updated!', {timeout: 1000});
            if (bikeId.value !== null && bikeId.value !== '') {
              makeSuggestions.value.push(activeDraft.value.bike.make);
              modelSuggestions.value.push(activeDraft.value.bike.model);
              coloursSuggestions.value.push(activeDraft.value.bike.colours);
              serialNumberSuggestions.value.push(activeDraft.value.bike.serialNumber);

              nextTick().then(() => {
                make.value = activeDraft.value.bike.make;
                model.value = activeDraft.value.bike.model;
                colours.value = activeDraft.value.bike.colours;
                decals.value = activeDraft.value.bike.decals;
                serialNumber.value = activeDraft.value.bike.serialNumber;
                bikePhotoTaken.value = true;
                stickerOnBike.value = true;
              });
            }
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 5000});
          });
      }
    }

    function setBike() {
      if (bikeId.value !== null && bikeId.value !== '') {
        matchWithBikeId.value = bikeId.value;
        requests.putDraftContractBike(activeDraft.value.id, bikeId.value)
          .then((response) => {
            activeDraft.value = response.data;
            toast.success('Bike Updated!', {timeout: 1000});
            stepNumber.value = 3;
            type.value = activeDraft.value.contractType;
            condition.value = activeDraft.value.conditionOfBike;
            notes.value = activeDraft.value.notes;
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 5000});
          });
      }
    }

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

    const submit = handleSubmit(() => {
      // next step until last step. if last step then submit form
      if (stepNumber.value === 1) {
        // Client details processing
        requests.getClientByEmail(emailAddress.value)
          .then((response) => {
            clientId.value = response.data[0]['id'];
            setClient();
          })
          .catch((error) => {
            if (error.response.status === 404) {
              requests.postNewClient({
                firstName: firstName.value,
                lastName: lastName.value,
                emailAddress: emailAddress.value,
              }).then((response) => {
                toast.success('New Client Created!', {timeout: 1000});
                clientId.value = response.data['id'];
                setClient();
              });
            }
          });
      } else if (stepNumber.value === 2) {
        // Bike details processing
        if (matchWithBikeId.value === 'new') {
          requests.postNewBike(make.value, model.value, colours.value, decals.value, serialNumber.value)
            .then((response) => {
              toast.success('New Bike Created!', {timeout: 1000});
              bikeId.value = response.data['id'];
              setBike();
            });
        } else {
          bikeId.value = matchWithBikeId.value;
          setBike();
        }
      } else if (stepNumber.value === 3) {
        requests.putDraftContractDetails(activeDraft.value.id, type.value, condition.value, notes.value)
          .then((response) => {
            activeDraft.value = response.data;
            toast.success('Contract Details Updated!', {timeout: 1000});
            stepNumber.value = 4;
            requests.getDepositBearers().then((response) =>
              (depositBearers.value = response.data.map((user) => (user.username))));
            if (activeDraft.value.depositCollectingUser !== null && activeDraft.value.depositAmountCollected !== null) {
              stepNumber.value = 5;
            }
            if (activeDraft.value.workingUser !== null) {
              stepNumber.value = 6;
            }
            if (activeDraft.value.checkingUser !== null) {
              stepNumber.value = 7;
            }
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 5000});
          });
      } else if (stepNumber.value === 4) {
        // Check password of deposit collector
        requests.putDraftContractDeposit(
          activeDraft.value.id,
          depositAmountCollected.value,
          depositCollectingUser.value,
          depositCollectingPassword.value)
          .then((response) => {
            activeDraft.value = response.data;
            toast.success('Deposit Details Updated!', {timeout: 1000});
            stepNumber.value = 5;
            requests.getActiveUsers().then((response) => (activeUsers.value = response.data.map((user) => (user.username))));
            userSelectionOptionsStatic.value = true;
          })
          .catch((error) => {
            if (error.response.status === 400) {
              depositCollectingPasswordSetErrors('Wrong Password!');
            } else {
              toast.error(error.response.data.detail.description, {timeout: 5000});
            }
          });
      } else if (stepNumber.value === 5) {
        // check password or pin of working volunteer
        requests.putDraftContractWorkingUser(activeDraft.value.id, workingUser.value, workingPasswordOrPin.value)
          .then((response) => {
            activeDraft.value = response.data;
            toast.success('Working Volunteer Updated!', {timeout: 1000});
            stepNumber.value = 6;
            requests.getRentalCheckers().then((response) => (rentalCheckers.value = response.data.map((user) => (user.username))));
            userSelectionOptionsStatic.value = true;
          })
          .catch((error) => {
            if (error.response.status === 400) {
              workingPasswordOrPinSetErrors('Wrong Password!');
            } else {
              toast.error(error.response.data.detail.description, {timeout: 5000});
            }
          });
      } else if (stepNumber.value === 6) {
        // check password or pin of checking volunteer
        requests.putDraftContractCheckingUser(activeDraft.value.id, checkingUser.value, checkingPasswordOrPin.value)
          .then((response) => {
            activeDraft.value = response.data;
            toast.success('Checking Volunteer Updated!', {timeout: 1000});
            userSelectionOptionsStatic.value = true;
            requests.postSubmitDraftContract(activeDraft.value.id)
              .then((response) => {
                toast.success('Contract Recorded!', {timeout: 1000});
                router.push({path: `/contracts/${response.data.id}`});
              }).catch((error) => {
                toast.error(error.response.data.detail.description, {timeout: 5000});
              });
          })
          .catch((error) => {
            if (error.response.status === 400) {
              checkingPasswordOrPinSetErrors('Wrong Password!');
            } else {
              toast.error(error.response.data.detail.description, {timeout: 5000});
            }
          });
      }
    });

    const prev = () => {
      stepNumber.value--;
      if (stepNumber.value === 2) {
        tryMatchingBike();
      }
    };

    return {
      contractDrafts,
      activeDraft,
      emailAddress,
      emailAddressError,
      emailAddressSetValue,
      confirmEmailAddress,
      confirmEmailAddressError,
      confirmEmailAddressSetValue,
      firstName,
      firstNameError,
      firstNameSetValue,
      lastName,
      lastNameError,
      lastNameSetValue,
      clientId,

      depositBearers,
      activeUsers,
      rentalCheckers,

      makeSuggestions,
      make,
      makeError,
      makeNotInList,
      modelSuggestions,
      model,
      modelError,
      modelNotInList,
      colours,
      coloursError,
      coloursSuggestions,
      decals,
      decalsError,
      serialNumber,
      serialNumberError,
      serialNumberSuggestions,
      bikePhotoTaken,
      bikePhotoTakenError,
      stickerOnBike,
      stickerOnBikeError,
      bikeId,
      matchWithBikeId,
      matchWithBikeIdError,
      bikeToBeLinked,

      type,
      typeError,
      condition,
      conditionError,
      notes,
      notesError,

      contractTypes,
      bikeConditions,

      depositAmountCollected,
      depositAmountCollectedError,
      depositCollectingUser,
      depositCollectingUserError,
      depositCollectingPassword,
      depositCollectingPasswordError,

      workingUser,
      workingUserError,
      workingPasswordOrPin,
      workingPasswordOrPinError,

      checkingUser,
      checkingUserError,
      checkingPasswordOrPin,
      checkingPasswordOrPinError,
      mCheckFrontWheelHub,
      mCheckFrontWheelHubError,
      mCheckFrontWheelTire,
      mCheckFrontWheelTireError,
      mCheckRearWheelHub,
      mCheckRearWheelHubError,
      mCheckRearWheelTire,
      mCheckRearWheelTireError,
      mCheckBottomBracket,
      mCheckBottomBracketError,
      mCheckFrontBrake,
      mCheckFrontBrakeError,
      mCheckRearBrake,
      mCheckRearBrakeError,
      mCheckSeatPost,
      mCheckSeatPostError,
      mCheckHeadset,
      mCheckHeadsetError,

      workingUserSelected,
      checkingUserSelected,

      userSelectionOptionsStatic,

      submit,
      steps,
      stepNumber,
      prev,
      tryMatchingBike,
    };
  },
  data() {
    return {
      OFFICIAL_NAME: OFFICIAL_NAME,
      clientSuggestions: [],
      isNfcActive: false,
      filtered_client_suggestions: [],
      filtered_make_suggestions: [],
      filtered_model_suggestions: [],
      filtered_colours_suggestions: [],
      filtered_serial_number_suggestions: [],
    };
  },
  created() {
    this.fetchClientSuggestions = debounce(this.fetchClientSuggestions, 500, {leading: false, trailing: true});
    this.fetchBikeMakeSuggestions = debounce(this.fetchBikeMakeSuggestions, 500, {leading: true, trailing: true});
    this.fetchBikeModelSuggestions = debounce(this.fetchBikeModelSuggestions, 500, {leading: true, trailing: true});
    this.fetchSerialNumberSuggestions = debounce(this.fetchSerialNumberSuggestions, 500, {leading: true, trailing: true});
    this.fetchColoursSuggestions = debounce(this.fetchColoursSuggestions, 500, {leading: true, trailing: true});
    this.run_filter = debounce(this.run_filter, 200, {leading: false, trailing: true});
    requests.getContractDrafts()
      .then((response) => {
        this.contractDrafts = response.data;
      })
      .catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
    if (this.$route.query.bikeId) {
      requests.getBike(this.$route.query.bikeId)
        .then((response) => {
          this.bike = response.data;
          this.bikeId = response.data.id;
          this.make = response.data.make;
          this.model = response.data.model;
          this.colours = response.data.colours;
          this.decals = response.data.decals;
          this.serialNumber = response.data.serialNumber;
          this.startNewDraft();
          this.fetchBikeMakeSuggestions(this.make);
          this.fetchBikeModelSuggestions(this.model);
          this.fetchColoursSuggestions(this.colours);
          this.fetchSerialNumberSuggestions(this.serialNumber);
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
        });
    }
  },
  methods: {
    userSortingFunction(user1, user2) {
      if (user1.toLowerCase() > user2.toLowerCase()) return 1;
      if (user1.toLowerCase() < user2.toLowerCase()) return -1;
      return 0;
    },
    datePlusSixMonths() {
      const date = new Date();
      return new Date(date.setMonth(date.getMonth() + 6));
    },
    fetchClientSuggestions() {
      if ((
        (this.firstName ? this.firstName.length : 0) +
          (this.lastName ? this.lastName.length : 0) +
          (this.emailAddress ? this.emailAddress.length : 0)
      ) > 2) {
        requests.findClient(
          this.firstName ? this.firstName.toLowerCase() : '',
          this.lastName ? this.lastName.toLowerCase() : '',
          this.emailAddress ? this.emailAddress.toLowerCase() :'',
          5)
          .then((response) => {
            this.clientSuggestions = response.data;
            this.run_filter();
          });
      }
    },
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
    selectClient(event, i) {
      if (i !== -1) {
        const selectedClient = this.filtered_client_suggestions[i];
        this.clientId = selectedClient.id;
        this.emailAddress = selectedClient.emailAddress;
        this.confirmEmailAddress = selectedClient.emailAddress;
        this.firstName = selectedClient.firstName;
        this.lastName = selectedClient.lastName;
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
    selectDepositCollectingUser(event, i) {
      if (i !== -1) {
        this.depositCollectingUser = this.filtered_deposit_collecting_user_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectWorkingUser(event, i) {
      if (i !== -1) {
        this.workingUser = this.filtered_working_user_suggestions[i];
        this.userSelectionOptionsStatic = false;
        this.workingUserSelected();
      }
    },
    selectCheckingUser(event, i) {
      if (i !== -1) {
        this.checkingUser = this.filtered_checking_user_suggestions[i];
        this.userSelectionOptionsStatic = false;
        this.checkingUserSelected();
      }
    },
    // verifyBikeDetails(rfidTagSerialNumber) {
    //   requests.getBikeByRfidTagSerialNumber(rfidTagSerialNumber)
    //     .then((response) => {
    //       const bike = response.data;
    //       let allSame = true;
    //       allSame &= bike.make.toLowerCase() === this.make.toLowerCase();
    //       allSame &= bike.model.toLowerCase() === this.model.toLowerCase();
    //       allSame &= bike.colour.toLowerCase() === this.colour.toLowerCase();
    //       allSame &= (bike.decals ? bike.decals.toLowerCase() : '') === this.decals.toLowerCase();
    //       allSame &= bike.serialNumber.toLowerCase() === this.serialNumber.toLowerCase();
    //       allSame &= bike.id.toLowerCase() === this.bikeId.toLowerCase();
    //       if (!allSame) {
    //         toast.warning('Some of the bike details do not match with the recorded details', {timeout: 4000});
    //       }
    //     })
    //     .catch((error) => {
    //       toast.error(error.response.data.detail.description, {timeout: 1000});
    //     });
    // },
    // readBikeDetailsFromNfcTag() {
    //   this.isNfcActive = true;
    //   nfc.readBikeDetailsFromNfcTag().then((response) => {
    //     if (response.bike) {
    //       toast.success('Details read!', {timeout: 1000});
    //       const bike = response.bike;
    //       this.make = bike.make.toLowerCase();
    //       this.model = bike.model.toLowerCase();
    //       this.colour = bike.colour.toLowerCase();
    //       this.decals = bike.decals ? bike.decals.toLowerCase() : '';
    //       this.serialNumber = bike.serialNumber.toLowerCase();
    //       this.bikeId = bike.id.toLowerCase();
    //       this.verifyBikeDetails(response.rfidTagSerialNumber);
    //     } else {
    //       toast.error('Some error occurred!', {timeout: 1000});
    //     }
    //   })
    //     .catch((error) => {
    //       toast.error(error.message, {timeout: 1000});
    //     })
    //     .finally(() => {
    //       this.isNfcActive = false;
    //     });
    // },
    // ensureBikeExists() {
    //   return new Promise((resolve, reject) => {
    //     if (!this.bikeId || this.bikeId === '') {
    //       requests.postNewBike(this.make, this.model, this.colours, this.decals, this.serialNumber)
    //         .then((response) => {
    //           const bike = response.data;
    //           this.bikeId = bike.id;
    //           resolve(bike);
    //         }).catch((error) => {
    //           reject(error);
    //         });
    //     } else {
    //       const bike = {
    //         id: this.bikeId.toLowerCase(),
    //         make: this.make.toLowerCase(),
    //         model: this.model.toLowerCase(),
    //         colours: this.colours,
    //         decals: this.decals.toLowerCase(),
    //         serialNumber: this.serialNumber.toLowerCase(),
    //       };
    //       resolve(bike);
    //     }
    //   });
    // },
    // writeBikeDetailsToNfcTag() {
    //   this.ensureBikeExists()
    //     .then((bike) => {
    //       this.isNfcActive = true;
    //       nfc.writeBikeDetailsToNfcTag(bike)
    //         .then((serialNumber) => {
    //           bike.rfidTagSerialNumber = serialNumber;
    //           requests.patchBikeChangeDetails(bike.id, bike)
    //             .then(() => {
    //               toast.success('Details Written', {timeout: 1000});
    //             })
    //             .catch((error) => {
    //               toast.error(error.response.data.detail.description, {timeout: 1000});
    //             });
    //         })
    //         .catch((error) => {
    //           toast.error(error.message, {timeout: 1000});
    //         })
    //         .finally(() => {
    //           this.isNfcActive = false;
    //         });
    //     })
    //     .catch((error) => {
    //       toast.error(error.response.data.detail.description, {timeout: 1000});
    //     });
    // },
    async run_filter() {
      const client = {
        firstName: this.firstName ? this.firstName : '',
        lastName: this.lastName ? this.lastName : '',
        emailAddress: this.emailAddress ? this.emailAddress : '',
      };
      levenshtein.filterSortObject(this.clientSuggestions, client, 4).then((result) => {
        this.filtered_client_suggestions = result;
      });
    },
    continueDraft(draftId) {
      requests.getContractDraft(draftId)
        .then((response) => {
          this.activeDraft = response.data;

          this.clientId = this.activeDraft.clientId;
          this.bikeId = this.activeDraft.bikeId;
          this.matchWithBikeId = this.activeDraft.bikeId;

          this.stepNumber = 1;
          this.clientSuggestions.push(this.activeDraft.client);
          nextTick(() => {
            if (this.activeDraft.client !== null) {
              this.emailAddress = this.activeDraft.client.emailAddress;
              this.confirmEmailAddress = this.activeDraft.client.emailAddress;
              this.firstName = this.activeDraft.client.firstName;
              this.lastName = this.activeDraft.client.lastName;
            }
          });
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
        });
    },
    startNewDraft() {
      this.firstName = null;
      this.lastName = null;
      this.emailAddress = null;
      this.confirmEmailAddress = null;

      this.bikeId = null;
      this.make = null;
      this.model = null;
      this.colours = [];
      this.decals = null;
      this.serialNumber = null;
      this.bikePhotoTaken = false;
      this.stickerOnBike = false;
      this.matchWithBikeId = null;
      this.type = null;
      this.condition = null;
      this.notes = null;
      this.depositAmountCollected = null;
      this.depositCollectingUser = null;
      this.depositCollectingPassword = null;
      this.workingUser = null;
      this.workingUserPassword = null;
      this.checkingUser = null;
      this.checkingUserPassword = null;
      this.mCheckFrontWheelHub = false;
      this.mCheckFrontWheelTire = false;
      this.mCheckRearWheelHub = false;
      this.mCheckRearWheelTire = false;
      this.mCheckBottomBracket = false;
      this.mCheckFrontBrake = false;
      this.mCheckRearBrake = false;
      this.mCheckSeatPost = false;
      this.mCheckHeadset = false;
      this.everythingCorrect = false;
      this.activeDraft = null;
      this.stepNumber = 1;
      this.userSelectionOptionsStatic = true;
      this.clientSuggestions = [];
      this.filtered_client_suggestions = [];
      this.filtered_make_suggestions = [];
      this.filtered_model_suggestions = [];
      this.filtered_colours_suggestions = [];
      this.filtered_serial_number_suggestions = [];
      this.filtered_deposit_collecting_user_suggestions = [];
      this.filtered_working_user_suggestions = [];
      this.filtered_checking_user_suggestions = [];

      requests.postNewContractDraft()
        .then((response) => {
          this.activeDraft = response.data;
          this.stepNumber = 1;
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
        });
    },
    resetClientComboBoxes() {
      this.filtered_client_suggestions = [];
      this.firstName = '';
      this.lastName = '';
      this.emailAddress = '';
      this.confirmEmailAddress = '';
      this.clientId = '';
    },
    filterAndSortColourSuggestions() {
      this.filtered_colours_suggestions = this.coloursSuggestions
        .toSorted((a, b) => colourSuggestionSort.colourSuggestionSort(a, b, this.colours)).slice(0, 6);
    },
  },
  watch: {
    emailAddress() {
      this.run_filter();
    },
    firstName() {
      this.run_filter();
    },
    lastName() {
      this.run_filter();
    },
    make() {
      this.tryMatchingBike();
      levenshtein.filterSort(this.makeSuggestions, this.make, 4).then((result) => {
        this.filtered_make_suggestions = result.slice(0, 6);
      });
    },
    model() {
      this.tryMatchingBike();
      levenshtein.filterSort(this.modelSuggestions, this.model, 4).then((result) => {
        this.filtered_model_suggestions = result.slice(0, 6);
      });
    },
    colour() {
      levenshtein.filterSort(this.colourSuggestions, this.colour, 4).then((result) => {
        this.filtered_colour_suggestions = result.slice(0, 6);
      });
    },
    // TODO: could these watchers be combined?
    colours() {
      this.tryMatchingBike();
      this.filterAndSortColourSuggestions();
    },
    coloursSuggestions() {
      this.filterAndSortColourSuggestions();
    },
    serialNumber() {
      this.tryMatchingBike();
      levenshtein.filterSort(this.serialNumberSuggestions, this.serialNumber, 4).then((result) => {
        this.filtered_serial_number_suggestions = result.slice(0, 6);
      });
    },
  },
  computed: {
    filtered_deposit_collecting_user_suggestions() {
      return this.depositBearers
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith(this.depositCollectingUser.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_working_user_suggestions() {
      return this.activeUsers
        .filter((suggestion) =>
          suggestion
            .toLowerCase()
            .startsWith(this.workingUser.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_checking_user_suggestions() {
      return this.rentalCheckers
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith(this.checkingUser.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filteredClientSuggestionsLegible() {
      return this.filtered_client_suggestions.map((client) => (`${client.firstName} ${client.lastName} ${client.emailAddress}`));
    },
  },
};
</script>
<style lang="scss" scoped></style>
