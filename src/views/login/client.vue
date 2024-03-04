<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-6 col-span-12">
      <Card title="Client Login">
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
              <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                <div class="lg:col-span-3 md:col-span-2 col-span-1">
                  <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                    Email Address
                  </h4>
                </div>
                <Textinput
                    label="Email Address"
                    type="email"
                    placeholder="your.email@example.com"
                    name="emailAddress"
                    v-model="emailAddress"
                    :error="emailAddressError"
                />
              </div>
            </div>

            <div v-if="stepNumber === 1 && !exisitingClient">
              <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                <div class="md:col-span-2 col-span-1">
                  <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                    Your Details
                  </h4>
                </div>
                <Textinput
                    label="First Name"
                    type="text"
                    placeholder="John"
                    name="firstName"
                    v-model="firstName"
                    :error="firstNameError"/>

                <Textinput
                    label="Last Name"
                    type="text"
                    placeholder="Smith"
                    name="lastName"
                    v-model="lastName"
                    :error="lastNameError"/>
              </div>
            </div>
            <div v-if="stepNumber === 2 || (stepNumber === 1 && exisitingClient)">
              <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                <div class="lg:col-span-3 md:col-span-2 col-span-1">
                  <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                    One Time Code
                  </h4>
                </div>
                <div class="col-span-1">
                  <Textinput
                      :label="`Enter the 6-digit code sent to ${emailAddress}`"
                      type="integer"
                      placeholder="123456"
                      name="code"
                      v-model="code"
                      :error="codeError"/>

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
      </Card>
    </div>
  </div>
</template>

<script>

import Card from '@/components/Card/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import requests from '@/requests';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useToast} from 'vue-toastification';
import {computed, ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import Button from '@/components/Button/index.vue';
import {useRouter, useRoute} from 'vue-router';
import Icon from '@/components/Icon';

const credentialsStore = useCredentialsStore();

export default {
  setup() {
    const steps = [
      {
        id: 1,
        title: 'Email Address',
      },
      {
        id: 2,
        title: 'Details',
      },
      {
        id: 3,
        title: 'Code',
      },
    ];

    const toast = useToast();
    const stepNumber = ref(0);
    const clientId = ref('');
    const exisitingClient = ref(false);
    const router = useRouter();
    const route = useRoute();

    const emailSchema = yup.object().shape({
      emailAddress: yup.string().email().required(' Email is required. '),
    });

    const detailsSchema = yup.object().shape({
      firstName: yup.string().required(' First name is required. '),
      lastName: yup.string().required(' Last name is required '),
    });

    const codeSchema = yup.object().shape({
      code: yup.number().positive().integer().lessThan(1000000).required(' Code is required '),
    });


    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return emailSchema;
        case 1:
          return exisitingClient.value ? codeSchema : detailsSchema;
        case 2:
          return codeSchema;
        default:
          return emailSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const handleContinue = () => {
      if (route.query.hasOwnProperty('nextUrl')) {
        router.push(route.query.nextUrl);
      } else {
        router.push('/me');
      }
    };

    const {value: emailAddress, errorMessage: emailAddressError} = useField('emailAddress');

    const {value: firstName, errorMessage: firstNameError} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError} = useField('lastName');

    const {value: code, errorMessage: codeError, setErrors: setCodeError} = useField('code');


    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        if (exisitingClient.value) {
          requests.getClientToken(clientId.value, code.value).then((response) => {
            credentialsStore.login(response.data['access_token'], 'client');
            requests.getClientMe().then((response) => (credentialsStore.setName(response.data['firstName'] + ' ' + response.data['lastName'])));
            handleContinue();
          }).catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
            setCodeError('Wrong code!');
          });
        } else {
          requests.postTempClientVerificationCode(clientId.value, code.value).then((response) => {
            credentialsStore.login(response.data['access_token'], 'client');
            requests.getClientMe().then((response) => (credentialsStore.setName(response.data['firstName'] + ' ' + response.data['lastName'])));
            handleContinue();
          }).catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
            setCodeError('Wrong code!');
          });
        }
      } else {
        // request login code.
        // If successful, go to step 2 to enter code
        // if error 404, go to step 1 to enter first and last name
        if (stepNumber.value === 0) {
          requests.getClientLoginCode(emailAddress.value).then((response) => {
            // remove details step
            if (steps.length === 3) steps.splice(1, 1);
            exisitingClient.value = true;
            clientId.value = response.data.id;
          }).catch((error) => {
            if (error.response.status === 404) {
              // reset any previously set flags and make sure details step is present
              exisitingClient.value = false;
              clientId.value = null;
              if (steps.length === 2) {
                steps.splice(1, 0, {
                  id: 2,
                  title: 'Details',
                });
              }
            }
          }).finally(() => {
            stepNumber.value++;
          });
        } else if (stepNumber.value === 1 && !exisitingClient.value) {
          // create the new client using supplied first and last name
          requests.postNewTempClient(firstName.value, lastName.value, emailAddress.value).then((response) => {
            clientId.value = response.data.id;
            stepNumber.value++;
          }).catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
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

      firstName,
      firstNameError,
      lastName,
      lastNameError,

      code,
      codeError,
      setCodeError,

      exisitingClient,
      submit,
      steps,
      stepNumber,
      prev,
    };
  },
  data() {
    return {

    };
  },
  components: {
    Button,
    Card,
    Textinput,
    Icon,
  },
};

</script>


<style scoped lang="scss">

</style>
