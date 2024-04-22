<script>
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm, ErrorMessage} from 'vee-validate';
import requests from '@/requests';
import Card from '@/components/Card';
import {ref, computed} from 'vue';
import {useRouter} from 'vue-router';
import Button from '@/components/Button/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import Select from '@/components/Select/index.vue';
import Icon from '@/components/Icon';

const toast = useToast();
export default {
  name: 'DepositExchanges',
  components: {
    Select,
    Textinput,
    Checkbox,
    Button,
    Card,
    ErrorMessage,
    Icon,
  },
  setup() {
    const steps = [
      {
        id: 1,
        title: 'Amount Excnaged',
      },
      {
        id: 2,
        title: 'From',
      },
      {
        id: 3,
        title: 'To',
      },
      {
        id: 4,
        title: 'Review',
      },
    ];
    const depositBearers = ref([]);
    const stepNumber = ref(0);
    const router = useRouter();

    requests.getDepositExchangeUsers().then((response) => depositBearers.value = response.data.map((user) => ({
      label: user.username,
      value: user.username,
    })));

    const amountSchema = yup.object().shape({
      amount: yup.number().integer('Must be an integer').positive('Must be positive').required('Is required'),
    });

    const fromUserSchema = yup.object().shape({
      fromUsername: yup.string().required('Is required'),
      fromPassword: yup.string().required('Is required'),
    });

    const toUserSchema = yup.object().shape({
      toUsername: yup.string().notOneOf([yup.ref('fromUsername')], 'Must be different from From Volunteer').required('Is required'),
      toPassword: yup.string().required('Is required'),
    });

    const reviewSchema = yup.object().shape({
      reviewed: yup.bool().required('Is required'),
    });

    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return amountSchema;
        case 1:
          return fromUserSchema;
        case 2:
          return toUserSchema;
        case 3:
          return reviewSchema;
        default:
          return amountSchema;
      };
    });

    const {handleSubmit: handleDepositExchangeSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: amount, errorMessage: amountError} = useField('amount');

    const {value: fromUsername, errorMessage: fromUsernameError} = useField('fromUsername');
    const {value: fromPassword, errorMessage: fromPasswordError, setErrors: setErrorsFromPassword} = useField('fromPassword');

    const {value: toUsername, errorMessage: toUsernameError} = useField('toUsername');
    const {value: toPassword, errorMessage: toPasswordError, setErrors: setErrorsToPassword} = useField('toPassword');

    const {value: reviewed, errorMessage: reviewedError} = useField('reviewed');

    const submitDepositExchange = handleDepositExchangeSubmit(() => {
      console.log('Next');
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        requests.postDepositExchange(amount.value, fromUsername.value, fromPassword.value, toUsername.value, toPassword.value).then((response) => {
          toast.success('Deposit Exchange Recorded', {timeout: 2000});
          router.push({path: '/accounting/deposits'});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      } else if (stepNumber.value === 0) {
        stepNumber.value++;
      } else if (stepNumber.value === 1) {
        requests.checkUserPassword(fromUsername.value, fromPassword.value).then((response) => {
          if (response.data) {
            stepNumber.value++;
          } else {
            setErrorsFromPassword('Wrong Password');
          }
        });
      } else if (stepNumber.value === 2) {
        requests.checkUserPassword(toUsername.value, toPassword.value).then((response) => {
          if (response.data) {
            stepNumber.value++;
          } else {
            setErrorsToPassword('Wrong Password');
          }
        });
      }
    });

    const prev = () => {
      stepNumber.value--;
    };

    return {
      steps,
      stepNumber,
      prev,
      amount,
      amountError,
      fromUsername,
      fromUsernameError,
      fromPassword,
      fromPasswordError,
      toUsername,
      toUsernameError,
      toPassword,
      toPasswordError,
      reviewed,
      reviewedError,
      submitDepositExchange,

      depositBearers,
    };
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Add Deposit Exchange">
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
            <form @submit.prevent="submitDepositExchange">
              <div v-if="stepNumber === 0">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Deposit Collection
                    </h4>
                  </div>
                  <Textinput
                      label="Amount (&pound;)"
                      type="text"
                      placeholder="200"
                      name="amount"
                      v-model="amount"
                      :error="amountError"
                  />
                </div>
              </div>

              <div v-if="stepNumber === 1">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      From Volunteer
                    </h4>
                  </div>
                  <Select
                      :options="depositBearers"
                      label="Username"
                      v-model="fromUsername"
                      name="fromUsername"
                      :error="fromUsernameError"
                  />

                  <Textinput
                      label="Password"
                      type="password"
                      placeholder="Password"
                      name="fromPassword"
                      v-model="fromPassword"
                      :error="fromPasswordError"
                      hasicon/>
                </div>
              </div>

              <div v-if="stepNumber === 2">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      To Volunteer
                    </h4>
                  </div>
                  <Select
                      :options="depositBearers"
                      label="Username"
                      v-model="toUsername"
                      name="toUsername"
                      :error="toUsernameError"
                  />

                  <Textinput
                      label="Password"
                      type="password"
                      placeholder="Password"
                      name="toPassword"
                      v-model="toPassword"
                      :error="toPasswordError"
                      hasicon/>
                </div>
              </div>

              <div v-if="stepNumber === 3">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Final Check
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Please check all the details!</h5>
                    <Checkbox
                        label="Reviewed"
                        name="reviewed"
                        v-model="reviewed"
                        :error="reviewedError"/>
                    <ErrorMessage name="reviewed" :error="reviewedError" class="text-danger-500"/>
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

<style scoped lang="scss">

</style>