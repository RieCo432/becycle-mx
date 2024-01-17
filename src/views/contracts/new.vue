<template>
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
        <form @submit.prevent="submit">
          <div v-if="stepNumber === 0">
            <div class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-2 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Enter the Lendee's Information
                </h4>
              </div>
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

              <Textinput
                label="Confirm Email"
                type="email"
                placeholder="Confirm your email"
                name="confirmEmailAddress"
                v-model="confirmEmailAddress"
                :error="confirmEmailAddressError"
              />
              <Textinput
                label="First name"
                type="text"
                placeholder="First name"
                name="firstname"
                v-model="firstName"
                :error="firstNameError"
              />
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
          <div v-if="stepNumber === 1">
            <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
              <div class="md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Enter the bike's details
                </h4>
              </div>

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

              <Textinput
                label="Colour"
                type="text"
                placeholder="Colour"
                name="colour"
                v-model="colour"
                :error="colourError"
              />

              <Textinput
                label="Decals"
                type="text"
                placeholder="Decals"
                name="decals"
                v-model="decals"
                :error="decalsError"
              />

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
          </div>
          <div v-if="stepNumber === 2">
            <div class="grid grid-cols-1 gap-5">
              <div class="">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Enter Your Address
                </h4>
              </div>
              <Textarea
                label="Address"
                type="text"
                placeholder="Write Address"
                name="address"
                v-model="address"
                :error="addressError"
              />
            </div>
          </div>
          <div v-if="stepNumber === 3">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Enter Your Address
                </h4>
              </div>
              <Textinput
                label="Facebook"
                type="text"
                placeholder="https://www.facebook.com/profile"
                name="fburl"
                v-model="fburl"
                :error="fbError"
              />
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
</template>
<script>
import Card from '@/components/Card';
import Button from '@/components/Button';
import Icon from '@/components/Icon';
import InputGroup from '@/components/InputGroup';
import Textarea from '@/components/Textarea';
import Textinput from '@/components/Textinput';
import {useField, useForm} from 'vee-validate';
import {computed, ref} from 'vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';


export default {
  components: {
    Card,
    Button,
    Icon,
    Textinput,
    InputGroup,
    Textarea,
    ComboboxTextInput,
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
        title: 'Mechanics',
      },
      {
        id: 5,
        title: 'Deposit',
      },
      {
        id: 6,
        title: 'Review',
      },
    ];
    const toast = useToast();
    const stepNumber = ref(0);

    const clientId = ref('');

    // step by step yup schema
    const clientSchema = yup.object().shape({
      firstName: yup.string().required('First name is required'),
      lastName: yup.string().required('First name is required'),
      emailAddress: yup
          .string()
          .email('Email is not valid')
          .required('Email is required'),
      confirmEmailAddress: yup
          .string()
          .email('Email is not valid')
          .required('Confirm Email is required')
          .oneOf([yup.ref('emailAddress'), null], 'Email Addresses must match'),
    });

    const bikeId = ref('');

    const bikeSchema = yup.object().shape({
      make: yup.string().required(' Make is required'),
      model: yup.string().required(' Model is required '),
      colour: yup.string().required(' Colour is required'),
      decals: yup.string(),
      serialNumber: yup.string().required(' Serial Number is required '),
    });

    const addressSchema = yup.object().shape({
      address: yup.string().required(' Address is required'),
    });
    const url =
      /^((ftp|http|https):\/\/)?(www.)?(?!.*(ftp|http|https|www.))[a-zA-Z0-9_-]+(\.[a-zA-Z]+)+((\/)[\w#]+)*(\/\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?$/gm;

    const socialSchema = yup.object().shape({
      fburl: yup
          .string()
          .required('Facebook url is required')
          .matches(url, 'Facebook url is not valid'),
    });

    // find current step schema
    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return clientSchema;
        case 1:
          return bikeSchema;
        case 2:
          return addressSchema;
        case 3:
          return socialSchema;
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

    const {value: phone, errorMessage: phoneError} = useField('phone');
    const {value: password, errorMessage: passwordError} =
      useField('password');
    const {value: confirmpass, errorMessage: confirmpassError} =
      useField('confirmpass');

    const {value: address, errorMessage: addressError} = useField('address');
    const {value: fburl, errorMessage: fbError} = useField('fburl');

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;

        toast.success -
          500('Form Submited', {
            timeout: 2000,
          });
      } else {
        if (stepNumber.value === 0) {
          requests.getClientByEmail(emailAddress.value).then((response) => {
            if (response.data.length === 0) {
              requests.postNewClient({
                firstName: firstName.value,
                lastName: lastName.value,
                emailAddress: emailAddress.value,
              }).then((response) => clientId.value = response['id']);
            } else {
              clientId.value = response.data[0]['id'];
            }
          });
        }
        stepNumber.value++;
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

      phone,
      phoneError,
      password,
      passwordError,
      confirmpass,
      confirmpassError,
      address,
      addressError,

      submit,
      steps,
      stepNumber,
      prev,
      fburl,
      fbError,
    };
  },
  data() {
    return {
      emailTyped: '',
      email_suggestions: [],
      make_suggestions: [],
      model_suggestions: [],
      serial_number_suggestions: [],
    };
  },
  created() {
    this.fetchEmailSuggestions = debounce(this.fetchEmailSuggestions, 500);
    this.fetchBikeMakeSuggestions = debounce(this.fetchBikeMakeSuggestions, 500);
    this.fetchBikeModelSuggestions = debounce(this.fetchBikeModelSuggestions, 500);
    this.fetchSerialNumberSuggestions = debounce(this.fetchSerialNumberSuggestions, 500);
  },
  methods: {
    fetchEmailSuggestions() {
      requests.getEmailAddressSuggestions(this.emailAddress).then((response) => {
        this.email_suggestions = response.data;
      });
    },
    fetchBikeMakeSuggestions() {
      requests.getBikeMakeSuggestions(this.make).then((response) => {
        this.make_suggestions = response.data;
      });
    },
    fetchBikeModelSuggestions() {
      requests.getBikeModelSuggestions(this.model).then((response) => {
        this.model_suggestions = response.data;
      });
    },
    fetchSerialNumberSuggestions() {
      requests.getBikeSerialNumberSuggestions(this.serialNumber).then((response) => {
        this.serial_number_suggestions = response.data;
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
  },
  computed: {
    filtered_email_suggestions() {
      return this.email_suggestions.filter((suggestion) => (suggestion.startsWith(this.emailAddress))).slice(0, 4);
    },
    filtered_make_suggestions() {
      return this.make_suggestions.filter((suggestion) => (suggestion.startsWith(this.make))).slice(0, 4);
    },
    filtered_model_suggestions() {
      return this.model_suggestions.filter((suggestion) => (suggestion.startsWith(this.model))).slice(0, 4);
    },
    filtered_serial_number_suggestions() {
      return this.serial_number_suggestions.filter((suggestion) => (suggestion.startsWith(this.serialNumber))).slice(0, 4);
    },
  },
};
</script>
<style lang="scss" scoped></style>
