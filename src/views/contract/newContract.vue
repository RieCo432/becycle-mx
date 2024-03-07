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
              ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500 dark:bg-slate-900 dark:ring-slate-900'
              : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
          }`"
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
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
                  class="absolute top-full text-base md:leading-6 mt-3 transition duration-150 md:opacity-100 opacity-0 group-hover:opacity-100"
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
                <div class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-2 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Enter the Lendee's Information
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="emailAddress"
                        :suggestions="filtered_email_suggestions"
                        :selected-callback="selectEmail">
                      <Textinput label="Email" type="email" placeholder="Type your email"
                                 name="emailAddress"
                                 v-model="emailAddress"
                                 :error="emailAddressError"
                                 @input="fetchEmailSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <Textinput
                        label="Confirm Email"
                        type="email"
                        placeholder="Confirm your email"
                        name="confirmEmailAddress"
                        v-model="confirmEmailAddress"
                        :error="confirmEmailAddressError"
                    />
                  </div>

                  <div class="col-span-1">
                    <Textinput
                        label="First name"
                        type="text"
                        placeholder="First name"
                        name="firstname"
                        v-model="firstName"
                        :error="firstNameError"
                    />
                  </div>

                  <div class="col-span-1">
                    <Textinput
                        label="Last name"
                        type="text"
                        placeholder="Last name"
                        name="lastname"
                        v-model="lastName"
                        :error="lastNameError"
                    />
                  </div>
                </div>
              </div>
              <div v-if="stepNumber === 1">
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Enter the bike's details
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="make"
                        :suggestions="filtered_make_suggestions"
                        :selected-callback="selectMake">
                      <Textinput
                          label="Make"
                          type="text"
                          placeholder="Make"
                          name="make"
                          v-model="make"
                          :error="makeError"
                          @input="fetchBikeMakeSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="model"
                        :suggestions="filtered_model_suggestions"
                        :selected-callback="selectModel">
                      <Textinput
                          label="Model"
                          type="text"
                          placeholder="Model"
                          name="model"
                          v-model="model"
                          :error="modelError"
                          @input="fetchBikeModelSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="colour"
                        :suggestions="filtered_colour_suggestions"
                        :selected-callback="selectColour">
                      <Textinput
                          label="Colour"
                          type="text"
                          placeholder="Colour"
                          name="colour"
                          v-model="colour"
                          :error="colourError"
                          @input="fetchColourSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <Textinput
                        label="Decals"
                        type="text"
                        placeholder="Decals"
                        name="decals"
                        v-model="decals"
                        :error="decalsError"
                    />
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="serialNumber"
                        :suggestions="filtered_serial_number_suggestions"
                        :selected-callback="selectSerialNumber">
                      <Textinput
                          label="Serial Number"
                          type="text"
                          placeholder="Serial Number"
                          name="serialnumber"
                          v-model="serialNumber"
                          :error="serialNumberError"
                          @input="fetchSerialNumberSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-start-1">
                    <Checkbox
                        label="Photo of bike taken?"
                        name="bikePhotoTaken"
                        v-model="bikePhotoTaken"
                        :error="bikePhotoTakenError"/>
                    <ErrorMessage name="bikePhotoTaken" :error="bikePhotoTakenError" class="text-danger-500"/>
                  </div>

                  <div class="col-span-1">
                    <Checkbox
                        label="Sticker on bike?"
                        name="stickerOnBike"
                        v-model="stickerOnBike"
                        :error="stickerOnBikeError"/>
                    <ErrorMessage name="stickerOnBike" :error="stickerOnBikeError" class="text-danger-500"/>
                  </div>
                </div>
              </div>
              <div v-if="stepNumber === 2">
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
              <div v-if="stepNumber === 3">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Deposit Collection
                    </h4>
                  </div>


                  <Textinput
                      label="Deposit Amount (&pound;)"
                      type="number"
                      placeholder="40"
                      name="depositAmountCollected"
                      v-model="depositAmountCollected"
                      :error="depositAmountCollectedError"
                  />

                  <Select
                      :options="depositBearers"
                      label="Deposit Collector"
                      v-model="depositCollectingUser"
                      name="depositCollectingUser"
                      :error="depositCollectingUserError"
                  />

                  <Textinput
                      label="Deposit Collector Password"
                      type="password"
                      placeholder="Password"
                      name="depositCollectingPassword"
                      v-model="depositCollectingPassword"
                      :error="depositCollectingPasswordError"
                      hasicon/>
                </div>
              </div>

              <div v-if="stepNumber === 4">
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Main Mechanic
                    </h4>
                  </div>

                  <Select
                      :options="activeUsers"
                      label="Working Volunteer"
                      v-model="workingUser"
                      name="workingUser"
                      :error="workingUserError"
                  />

                  <Textinput
                      label="Working User Password or Pin"
                      type="password"
                      placeholder="Password or Pin"
                      name="workingUserPasswordOrPin"
                      v-model="workingPasswordOrPin"
                      :error="workingPasswordOrPinError"
                      hasicon/>
                </div>
              </div>


              <div v-if="stepNumber === 5">
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Checking Volunteer
                    </h4>
                  </div>

                  <Select
                      :options="rentalCheckers"
                      label="Safety Checking User"
                      v-model="checkingUser"
                      name="checkingUser"
                      :error="checkingUserError"
                  />

                  <Textinput
                      label="Checking User Password or Pin"
                      type="password"
                      placeholder="Password Or Pin"
                      name="checkingPasswordOrPin"
                      v-model="checkingPasswordOrPin"
                      :error="checkingPasswordOrPinError"
                      hasicon/>
                </div>
              </div>

              <div v-if="stepNumber === 6">
                <div class="grid lg:grid-cols-2 grid-cols-1 gap-5">
                  <div class="col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">Please check all the details!</h4>
                    <table class="w-full text-base text-slate-800 dark:text-slate-300 border border-collapse border-slate-500 bg-slate-700">
                      <thead>
                        <th colspan="2" class="border border-slate-500">Lendee Details</th>
                      </thead>
                      <tr>
                        <td class="border border-slate-500">Name</td>
                        <td class="border border-slate-500">{{firstName}} {{lastName}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Email Address</td>
                        <td class="border border-slate-500">{{emailAddress}}</td>
                      </tr>
                      <thead>
                        <th colspan="2" class="border border-slate-500">Bike Details</th>
                      </thead>
                      <tr>
                        <td class="border border-slate-500">Make</td>
                        <td class="border border-slate-500">{{make}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Model</td>
                        <td class="border border-slate-500">{{model}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Colour</td>
                        <td class="border border-slate-500">{{colour}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Decals</td>
                        <td class="border border-slate-500">{{decals}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Serial Number</td>
                        <td class="border border-slate-500">{{serialNumber}}</td>
                      </tr>
                      <thead>
                      <th colspan="2" class="border border-slate-500">Additional Details</th>
                      </thead>
                      <tr>
                        <td class="border border-slate-500">Lease Start</td>
                        <td class="border border-slate-500">{{new Date().toDateString()}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Lease End</td>
                        <td class="border border-slate-500">{{datePlusSixMonths().toDateString()}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Deposit</td>
                        <td class="border border-slate-500">&#163;{{depositAmountCollected}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Contract Type</td>
                        <td class="border border-slate-500">{{type}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Bike Condition</td>
                        <td class="border border-slate-500">{{condition}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Notes</td>
                        <td class="border border-slate-500">{{notes}}</td>
                      </tr>
                    </table>
                  </div>
                  <div class="col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">Terms of Loan</h4>
                    <p class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Bicycle (Bike) Release Form: Terms of Loan) The agreed deposit is made and kept as a retainer against the value
                      of the bike and released back to You (Keeper) upon the return of the borrowed bike – in satisfactory condition.
                      BeCYCLE Workshop reserves the right to deduct money from the deposit if and when any damage or excessive
                      wear and tear occurs to the bike – and/or the bike was kept by You over the agreed rental period. The bike, when
                      loaned is the full and sole responsibility of You (Keeper) therefore You are entrusted with the burden of
                      ownership, maintenance, and upkeep. It is completely at your own risk that the bike is maintained and operated
                      within reasonable use – to ensure Your personal safety.
                    </p>
                  </div>
                  <div class="col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">Agreement</h4>
                    <Checkbox
                        label="I confirm all details are correct and I agree to the terms of the loan!"
                        name="everythingCorrect"
                        v-model="everythingCorrect"
                        :error="everythingCorrectError"/>
                    <ErrorMessage name="everythingCorrect" :error="everythingCorrectError" class="text-danger-500"/>
                  </div>
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
import InputGroup from '@/components/InputGroup';
import Textarea from '@/components/Textarea';
import Textinput from '@/components/Textinput';
import Radio from '@/components/Radio/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';
import {ErrorMessage, Field, useField, useForm} from 'vee-validate';
import {computed, ref} from 'vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Select from '@/components/Select';
import Checkbox from '@/components/Switch/index.vue';
import {useRouter} from 'vue-router';


export default {
  name: 'newContract',
  components: {
    Checkbox,
    VueSelect,
    ErrorMessage,
    Field,
    Card,
    Button,
    Icon,
    Textinput,
    InputGroup,
    Textarea,
    ComboboxTextInput,
    Radio,
    Select,
  },

  setup() {
    const steps = [
      {
        id: 1,
        title: 'Client Details',
      },
      {
        id: 2,
        title: 'Bike Details',
      },
      {
        id: 3,
        title: 'Contract Details',
      },
      {
        id: 4,
        title: 'Deposit',
      },
      {
        id: 5,
        title: 'Mechanic',
      },
      {
        id: 6,
        title: 'Safety Check',
      },
      {
        id: 7,
        title: 'Summary',
      },
    ];

    const contractTypes = ref(['standard', 'child']);
    requests.getContractTypes().then((response) => (contractTypes.value = response.data));

    const bikeConditions = ref(['fair', 'good']);
    requests.getBikeConditions().then((response) => (bikeConditions.value = response.data));

    const toast = useToast();
    const stepNumber = ref(0);

    const clientId = ref('');
    const bikeId = ref('');

    const router = useRouter();

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
      make: yup.string().required(' Make is required'),
      model: yup.string().required(' Model is required '),
      colour: yup.string().required(' Colour is required'),
      decals: yup.string(),
      serialNumber: yup.string().required(' Serial Number is required '),
      bikePhotoTaken: yup.boolean().oneOf([true], 'Must take a photo of the bike').required('Must take a photo of the bike'),
      stickerOnBike: yup.boolean().oneOf([true], 'Must put a Becycle sticker on bike').required('Must put a Becycle sticker on bike'),
    });

    const contractSchema = yup.object().shape({
      type: yup.string().required(' Type is required'),
      condition: yup.string().required(' Condition is required '),
      notes: yup.string(),
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
      checkingUser: yup.string().required(' Checking Username is required ').notOneOf([yup.ref('workingUser')], 'Checking volunteer must be different from working volunteer'),
      checkingPasswordOrPin: yup.string().required(' Password or Pin is required '),
    });

    const reviewSchema = yup.object().shape({
      everythingCorrect: yup.boolean().oneOf([true], 'This check is required').required('This check is required!'),
    });


    // find current step schema
    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return clientSchema;
        case 1:
          return bikeSchema;
        case 2:
          return contractSchema;
        case 3:
          return depositCollectionSchema;
        case 4:
          return workingUserSchema;
        case 5:
          return checkingUserSchema;
        case 6:
          return reviewSchema;
        default:
          return clientSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: emailAddress, errorMessage: emailAddressError} = useField('emailAddress');
    const {value: confirmEmailAddress, errorMessage: confirmEmailAddressError} = useField('confirmEmailAddress');
    const {value: firstName, errorMessage: firstNameError} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError} = useField('lastName');

    const {value: make, errorMessage: makeError} = useField('make');
    const {value: model, errorMessage: modelError} = useField('model');
    const {value: colour, errorMessage: colourError} = useField('colour');
    const {value: decals, errorMessage: decalsError} = useField('decals');
    const {value: serialNumber, errorMessage: serialNumberError} = useField('serialNumber');
    const {value: bikePhotoTaken, errorMessage: bikePhotoTakenError} = useField('bikePhotoTaken');
    const {value: stickerOnBike, errorMessage: stickerOnBikeError} = useField('stickerOnBike');

    const {value: type, errorMessage: typeError} = useField('type');
    const {value: condition, errorMessage: conditionError} = useField('condition');
    const {value: notes, errorMessage: notesError} = useField('notes');

    const {value: depositAmountCollected, errorMessage: depositAmountCollectedError} = useField('depositAmountCollected');
    const {value: depositCollectingUser, errorMessage: depositCollectingUserError} = useField('depositCollectingUser');
    const {value: depositCollectingPassword, errorMessage: depositCollectingPasswordError, setErrors: depositCollectingPasswordSetErrors} = useField('depositCollectingPassword');

    const {value: workingUser, errorMessage: workingUserError} = useField('workingUser');
    const {value: workingPasswordOrPin, errorMessage: workingPasswordOrPinError, setErrors: workingPasswordOrPinSetErrors} = useField('workingPasswordOrPin');

    const {value: checkingUser, errorMessage: checkingUserError} = useField('checkingUser');
    const {value: checkingPasswordOrPin, errorMessage: checkingPasswordOrPinError, setErrors: checkingPasswordOrPinSetErrors} = useField('checkingPasswordOrPin');

    const {value: everythingCorrect, errorMessage: everythingCorrectError} = useField('everythingCorrect');

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        requests.postNewContract(clientId.value, bikeId.value, depositAmountCollected.value, condition.value, type.value, notes.value, workingUser.value, workingPasswordOrPin.value, checkingUser.value, checkingPasswordOrPin.value, depositCollectingUser.value, depositCollectingPassword.value).then((response) => {
          toast.success('Contract Recorded!', {timeout: 1000});
          router.push({path: `/contracts/${response.data.id}`});
        });
      } else {
        if (stepNumber.value === 0) {
          // Client details processing
          requests.getClientByEmail(emailAddress.value).then((response) => {
            clientId.value = response.data[0]['id'];
            stepNumber.value++;
          }).catch((error) => {
            if (error.response.status === 404) {
              requests.postNewClient({
                firstName: firstName.value,
                lastName: lastName.value,
                emailAddress: emailAddress.value,
              }).then((response) => {
                toast.success('New Client Created!', {timeout: 1000});
                clientId.value = response.data['id'];
                stepNumber.value++;
              });
            }
          });
        } else if (stepNumber.value === 1) {
          // Bike details processing
          requests.findBike(make.value, model.value, colour.value, decals.value, serialNumber.value)
              .then((response) => {
                bikeId.value = response.data['id'];
                stepNumber.value++;
              }).catch((error) => {
                if (error.response.status === 404) {
                  requests.postNewBike(make.value, model.value, colour.value, decals.value, serialNumber.value)
                      .then((response) => {
                        toast.success('New Bike Created!', {timeout: 1000});
                        bikeId.value = response.data['id'];
                        stepNumber.value++;
                      });
                }
              });
        } else if (stepNumber.value === 2) {
          // Nothing to process
          stepNumber.value++;
        } else if (stepNumber.value === 3) {
          // Check password of deposit collector
          requests.checkUserPassword(depositCollectingUser.value, depositCollectingPassword.value).then((response) => {
            if (response.data) {
              stepNumber.value++;
            } else {
              depositCollectingPasswordSetErrors('Wrong Password!');
            }
          });
        } else if (stepNumber.value === 4) {
          // check password or pin of working volunteer
          requests.checkUserPasswordOrPin(workingUser.value, workingPasswordOrPin.value).then((response) => {
            if (response.data) {
              stepNumber.value++;
            } else {
              workingPasswordOrPinSetErrors('Wrong Password or Pin!');
            }
          });
        } else if (stepNumber.value === 5) {
          // check password or pin of checking volunteer
          requests.checkUserPasswordOrPin(checkingUser.value, checkingPasswordOrPin.value).then((response) => {
            if (response.data) {
              stepNumber.value++;
            } else {
              checkingPasswordOrPinSetErrors('Wrong Password or Pin!');
            }
          });
        }
      }
    });

    const prev = () => {
      stepNumber.value--;
    };

    return {
      emailAddress,
      emailAddressError,
      confirmEmailAddress,
      confirmEmailAddressError,
      firstName,
      firstNameError,
      lastName,
      lastNameError,
      clientId,

      make,
      makeError,
      model,
      modelError,
      colour,
      colourError,
      decals,
      decalsError,
      serialNumber,
      serialNumberError,
      bikePhotoTaken,
      bikePhotoTakenError,
      stickerOnBike,
      stickerOnBikeError,

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

      everythingCorrect,
      everythingCorrectError,


      submit,
      steps,
      stepNumber,
      prev,
    };
  },
  data() {
    return {
      emailTyped: '',
      email_suggestions: [],
      make_suggestions: [],
      model_suggestions: [],
      colour_suggestions: [],
      serial_number_suggestions: [],
      depositBearers: [],
      rentalCheckers: [],
      activeUsers: [],
    };
  },
  created() {
    this.fetchEmailSuggestions = debounce(this.fetchEmailSuggestions, 500, {leading: true, trailing: true});
    this.fetchBikeMakeSuggestions = debounce(this.fetchBikeMakeSuggestions, 500, {leading: true, trailing: true});
    this.fetchBikeModelSuggestions = debounce(this.fetchBikeModelSuggestions, 500, {leading: true, trailing: true});
    this.fetchSerialNumberSuggestions = debounce(this.fetchSerialNumberSuggestions, 500, {leading: true, trailing: true});
    this.fetchColourSuggestions = debounce(this.fetchColourSuggestions, 500, {leading: true, trailing: true});
  },
  methods: {
    datePlusSixMonths() {
      const date = new Date();
      return new Date(date.setMonth(date.getMonth() + 6));
    },
    fetchEmailSuggestions() {
      requests.getEmailAddressSuggestions(this.emailAddress.toLowerCase()).then((response) => {
        this.email_suggestions = response.data;
      });
    },
    fetchBikeMakeSuggestions() {
      requests.getBikeMakeSuggestions(this.make.toLowerCase()).then((response) => {
        this.make_suggestions = response.data;
      });
    },
    fetchBikeModelSuggestions() {
      requests.getBikeModelSuggestions(this.model.toLowerCase()).then((response) => {
        this.model_suggestions = response.data;
      });
    },
    fetchSerialNumberSuggestions() {
      requests.getBikeSerialNumberSuggestions(this.serialNumber.toLowerCase()).then((response) => {
        this.serial_number_suggestions = response.data;
      });
    },
    fetchColourSuggestions() {
      requests.getBikeColourSuggestions(this.colour.toLowerCase()).then((response) => {
        this.colour_suggestions = response.data;
      });
    },
    selectEmail(event) {
      this.emailAddress = event.target.innerText;
      requests.getClientByEmail(this.emailAddress).then((response) => {
        this.clientId = response.data[0]['id'];
        this.confirmEmailAddress = response.data[0]['emailAddress'];
        this.firstName = response.data[0]['firstName'];
        this.lastName = response.data[0]['lastName'];
      });
    },
    selectMake(event) {
      this.make = event.target.innerText;
    },
    selectModel(event) {
      this.model = event.target.innerText;
    },
    selectSerialNumber(event) {
      this.serialNumber = event.target.innerText;
    },
    selectColour(event) {
      this.colour = event.target.innerText;
    },
  },
  computed: {
    filtered_email_suggestions() {
      return this.email_suggestions.filter((suggestion) => (suggestion.startsWith(this.emailAddress.toLowerCase()))).slice(0, 4);
    },
    filtered_make_suggestions() {
      return this.make_suggestions.filter((suggestion) => (suggestion.startsWith(this.make.toLowerCase()))).slice(0, 4);
    },
    filtered_model_suggestions() {
      return this.model_suggestions.filter((suggestion) => (suggestion.startsWith(this.model.toLowerCase()))).slice(0, 4);
    },
    filtered_serial_number_suggestions() {
      return this.serial_number_suggestions.filter((suggestion) => (suggestion.startsWith(this.serialNumber.toLowerCase()))).slice(0, 4);
    },
    filtered_colour_suggestions() {
      return this.colour_suggestions.filter((suggestion) => (suggestion.startsWith(this.colour.toLowerCase()))).slice(0, 4);
    },
  },
  mounted() {
    requests.getDepositBearers().then((response) => (this.depositBearers = response.data.map((user) =>
      ({
        label: user.username,
        value: user.username,
      }),
    )));
    requests.getActiveUsers().then((response) => (this.activeUsers = response.data.map((user) =>
      ({
        label: user.username,
        value: user.username,
      }),
    )));
    requests.getRentalCheckers().then((response) => (this.rentalCheckers = response.data.map((user) =>
      ({
        label: user.username,
        value: user.username,
      }),
    )));
  },
};
</script>
<style lang="scss" scoped></style>
