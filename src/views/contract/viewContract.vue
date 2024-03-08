<script>
import Textinput from '@/components/Textinput/index.vue';
import DashButton from '@/components/Button/index.vue';
import Select from '@/components/Select/index.vue';
import Card from '@/components/Card/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import {useRoute} from 'vue-router';
import {computed, ref, toRef} from 'vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm, ErrorMessage} from 'vee-validate';
import requests from '@/requests';
import {useCredentialsStore} from '@/store/credentialsStore';
import ContractClientCardSkeleton from '@/components/Skeleton/ContractClientCardSkeleton.vue';
import ContractBikeCardSkeleton from '@/components/Skeleton/ContractBikeCardSkeleton.vue';
import ContractCardSkeleton from '@/components/Skeleton/ContractCardSkeleton.vue';
import Icon from '@/components/Icon';

const toast = useToast();

export default {
  name: 'viewContract',
  components: {
    Checkbox,
    Select,
    Card,
    DashButton,
    Textinput,
    ContractClientCardSkeleton,
    ContractBikeCardSkeleton,
    ContractCardSkeleton,
    ErrorMessage,
    Icon,
  },
  setup(props) {
    const route = useRoute();

    const credentialsStore = useCredentialsStore();
    const toast = useToast();
    const contractData = toRef(props, 'contract');
    const patchContractReturn = toRef(props, 'patchContractReturn');


    const steps = [
      {
        id: 1,
        title: 'Deposit Return',
      },
      {
        id: 2,
        title: 'Accepting Volunteer',
      },
      {
        id: 3,
        title: 'Review',
      },
    ];

    const stepNumber = ref(0);

    const depositReturningSchema = yup.object().shape({
      depositAmountReturned: yup.number().min(0, 'Must be positive').integer()
          .required(' Deposit Amount is required '),
      depositReturningUser: yup.string().required(' Deposit Returner Username is required '),
      depositReturningPassword: yup.string().required(),
    });

    const returnAcceptingUserSchema = yup.object().shape({
      returnAcceptingUser: yup.string().required(' Return Accepting Username is required '),
      returnAcceptingPasswordOrPin: yup.string().required(' Password or Pin is required '),
    });

    const reviewSchema = yup.object().shape({
      everythingCorrect: yup.boolean().oneOf([true], 'This check is required').required('This check is required!'),
    });


    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return depositReturningSchema;
        case 1:
          return returnAcceptingUserSchema;
        case 2:
          return reviewSchema;
        default:
          return depositReturningSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: depositAmountReturned, errorMessage: depositAmountReturnedError, setErrors: depositAmountReturnedSetErrors} = useField('depositAmountReturned');
    const {value: depositReturningUser, errorMessage: depositReturningUserError} = useField('depositReturningUser');
    const {value: depositReturningPassword, errorMessage: depositReturningPasswordError, setErrors: depositReturningPasswordSetErrors} = useField('depositReturningPassword');

    const {value: returnAcceptingUser, errorMessage: returnAcceptingUserError} = useField('returnAcceptingUser');
    const {value: returnAcceptingPasswordOrPin, errorMessage: returnAcceptingPasswordOrPinError, setErrors: returnAcceptingPasswordOrPinSetErrors} = useField('returnAcceptingPasswordOrPin');


    const {value: everythingCorrect, errorMessage: everythingCorrectError} = useField('everythingCorrect');


    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        patchContractReturn.value(depositAmountReturned.value, depositReturningUser.value, depositReturningPassword.value, returnAcceptingUser.value, returnAcceptingPasswordOrPin.value);
      } else {
        if (stepNumber.value === 0) {
          if (depositAmountReturned.value > contractData.value.depositAmountCollected) {
            depositAmountReturnedSetErrors('Must not be larger than the deposit collected!');
            return;
          }
          requests.checkUserPassword(depositReturningUser.value, depositReturningPassword.value).then((response) => {
            if (response.data) {
              stepNumber.value++;
            } else {
              depositReturningPasswordSetErrors('Wrong Password!');
            }
          });
        } else if (stepNumber.value === 1) {
          // handle return accepting user
          requests.checkUserPasswordOrPin(returnAcceptingUser.value, returnAcceptingPasswordOrPin.value).then((response) => {
            if (response.data) {
              stepNumber.value++;
            } else {
              returnAcceptingPasswordOrPinSetErrors('Wrong Password or Pin!');
            }
          });
        }
      }
    });

    const prev = () => {
      stepNumber.value--;
    };

    return {
      contractData,
      credentialsStore,
      depositAmountReturned,
      depositAmountReturnedError,
      depositReturningUser,
      depositReturningUserError,
      depositReturningPassword,
      depositReturningPasswordError,

      returnAcceptingUser,
      returnAcceptingUserError,
      returnAcceptingPasswordOrPin,
      returnAcceptingPasswordOrPinError,

      everythingCorrect,
      everythingCorrectError,

      submit,
      steps,
      stepNumber,
      prev,
    };
  },
  methods: {
    goToClient() {
      if (this.isUser) {
        this.$router.push({path: `/clients/${this.client.id}`});
      } else {
        this.$router.push({path: '/me'});
      }
    },
  },
  props: {
    client: {
      type: Object,
      required: true,
    },
    bike: {
      type: Object,
      required: true,
    },
    depositCollectingUsername: {
      type: String,
      required: true,
    },
    workingUsername: {
      type: String,
      required: true,
    },
    checkingUsername: {
      type: String,
      required: true,
    },
    contract: {
      type: Object,
      required: true,
    },
    depositReturnedByUsername: {
      type: String,
      required: false,
    },
    returnAcceptedByUsername: {
      type: String,
      required: false,
    },
    depositBearers: {
      type: Array,
      required: false,
      default: () => [],
    },
    activeUsers: {
      type: Array,
      required: false,
      default: () => [],
    },
    loadingContract: {
      type: Boolean,
      required: true,
    },
    loadingClient: {
      type: Boolean,
      required: true,
    },
    loadingBike: {
      type: Boolean,
      required: true,
    },
    patchContractReturn: {
      type: Function,
      default: () => {},
    },
    patchContractExtend: {
      type: Function,
      default: () => {},
    },
    isUser: {
      type: Boolean,
      required: true,
    },
    openEditClientDetailsModal: {
      type: Function,
      required: true,
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12 lg:col-span-4 gap-5">
          <Card title="Lendee">
            <ContractClientCardSkeleton v-if="loadingClient" count="1"></ContractClientCardSkeleton>
            <template v-else>
              <div class="grid grid-cols-12 h-full">
                <div class="col-span-12" >
                  <p class="text-slate-600 dark:text-slate-300">{{client.firstName}} {{client.lastName}}</p>
                  <p class="text-slate-600 dark:text-slate-300">{{client.emailAddress}}</p>
                </div>
                <div class="col-span-6 mt-auto">
                  <DashButton @click="goToClient">
                    View Client
                  </DashButton>
                </div>
                <div class="col-span-6 mt-auto">
                  <DashButton @click="openEditClientDetailsModal">
                    Edit Details
                  </DashButton>
                </div>
              </div>
            </template>
          </Card>
        </div>
        <div class="col-span-12 lg:col-span-4 gap-5">
          <Card title="Bike">
            <ContractBikeCardSkeleton v-if="loadingBike"></ContractBikeCardSkeleton>
            <template v-else>
              <p class="text-slate-600 dark:text-slate-300">{{bike.make}} {{bike.model}}</p>
              <p class="text-slate-600 dark:text-slate-300">{{bike.colour}} {{bike.decals}}</p>
              <p class="text-slate-600 dark:text-slate-300">{{bike.serialNumber}}</p>
            </template>
          </Card>
        </div>
        <div class="col-span-12 lg:col-span-4 gap-5">
          <Card title="Contract">
            <ContractCardSkeleton v-if="loadingContract"></ContractCardSkeleton>
            <template v-else>
              <div class="flex flex-col h-full">
                <div class="flex-1">
                  <p class="text-slate-600 dark:text-slate-300">From: {{new Date(Date.parse(contract.startDate)).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Until: {{new Date(Date.parse(contract.endDate)).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Notes: {{contract.notes}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Condition: {{contract.conditionOfBike}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Deposit: &#163;{{contract.depositAmountCollected}} to {{depositCollectingUsername}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Done by: {{workingUsername}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Checked by: {{checkingUsername}}</p>
                </div>
                <DashButton v-if="isUser" class="mt-5" @click="patchContractExtend">
                  Extend Contract
                </DashButton>
              </div>
            </template>
          </Card>
        </div>
        <div class="col-span-12 gap-5" v-if="((contract.returnedDate == null) && isUser) || (contract.returnedDate != null)">
          <Card title="Return">
            <div v-if="(contract.returnedDate == null) && isUser">
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
                <form @submit.prevent="submit"  @keydown.enter="submit">
                  <div v-if="stepNumber === 0">
                    <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                      <div class="lg:col-span-3 md:col-span-2 col-span-1">
                        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                          Deposit Return
                        </h4>
                      </div>
                      <Textinput
                          label="Deposit Amount (&pound;)"
                          type="number"
                          placeholder="40"
                          name="depositAmountReturned"
                          v-model="depositAmountReturned"
                          :error="depositAmountReturnedError"
                      />

                      <Select
                          :options="depositBearers"
                          label="Deposit Returner"
                          v-model="depositReturningUser"
                          name="depositReturningUser"
                          :error="depositReturningUserError"
                      />

                      <Textinput
                          label="Deposit Returner Password"
                          type="password"
                          placeholder="Password"
                          name="depositReturningPassword"
                          v-model="depositReturningPassword"
                          :error="depositReturningPasswordError"
                          hasicon/>
                    </div>
                  </div>

                  <div v-if="stepNumber === 1">
                    <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                      <div class="md:col-span-2 col-span-1">
                        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                          Return Accepting Volunteer
                        </h4>
                      </div>

                      <Select
                          :options="activeUsers"
                          label="Return Accepting Volunteer"
                          v-model="returnAcceptingUser"
                          name="returnAcceptingUser"
                          :error="returnAcceptingUserError"
                      />

                      <Textinput
                          label="Password or Pin"
                          type="password"
                          placeholder="Password or Pin"
                          name="returnAcceptingUserPasswordOrPin"
                          v-model="returnAcceptingPasswordOrPin"
                          :error="returnAcceptingPasswordOrPinError"
                          hasicon/>
                    </div>
                  </div>
                  <div v-if="stepNumber === 2">
                    <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                      <div class="lg:col-span-3 md:col-span-2 col-span-1">
                        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                          Final Check
                        </h4>
                        <table class="w-full text-base text-slate-800 dark:text-slate-300 border border-collapse border-slate-500 bg-slate-700">
                          <thead>
                          <th colspan="2" class="border border-slate-500">Return Details</th>
                          </thead>
                          <tr>
                            <td class="border border-slate-500">Return Date</td>
                            <td class="border border-slate-500">{{new Date().toDateString()}}</td>
                          </tr>
                          <tr>
                            <td class="border border-slate-500">Deposit Returned</td>
                            <td class="border border-slate-500">&#163;{{depositAmountReturned}}</td>
                          </tr>
                        </table>
                      </div>
                      <div class="col-span-1">
                        <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Please check all the details!</h5>
                        <Checkbox
                            label="I confirm that this information is correct and the deposit was returned to the lendee!"
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
                    <DashButton
                        @click.prevent="prev()"
                        text="prev"
                        btnClass="btn-dark"
                        v-if="this.stepNumber !== 0"
                    />
                    <DashButton
                        :text="stepNumber !== this.steps.length - 1 ? 'next' : 'submit'"
                        btnClass="btn-dark"
                    />
                  </div>
                </form>
              </div>
            </div>
            <div v-else-if="contract.returnedDate != null">
              <p class="text-slate-600 dark:text-slate-300">Returned on {{new Date(Date.parse(contract.returnedDate)).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}</p>
              <p class="text-slate-600 dark:text-slate-300">Deposit returned: &#163; {{contract.depositAmountReturned}} by {{depositReturnedByUsername}}</p>
              <p class="text-slate-600 dark:text-slate-300">Received by {{returnAcceptedByUsername}}</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
