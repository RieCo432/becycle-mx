<script>
import Card from '@/components/card';
import requests from '@/requests';
import DashButton from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import {computed, ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import Textinput from '@/components/Textinput/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import Select from '@/components/Select/index.vue';
import Radio from '@/components/Radio/index.vue';
import Button from '@/components/Button/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import {useRoute, useRouter} from 'vue-router';

const toast = useToast();

export default {
  name: 'viewContract',
  components: {
    ComboboxTextInput,
    Button,
    Radio,
    Select,
    Textarea,
    Checkbox,
    Textinput,
    DashButton,
    Card,
  },

  setup() {
    const route = useRoute();

    const contract = ref({});


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

    const toast = useToast();
    const stepNumber = ref(0);


    const depositReturningSchema = yup.object().shape({
      depositAmountReturned: yup.number().positive().integer().required(' Deposit Amount is required '),
      depositReturningUser: yup.string().required(' Deposit Returner Username is required '),
      depositReturningPassword: yup.string().required(),
    });

    const returnAcceptingUserSchema = yup.object().shape({
      returnAcceptingUser: yup.string().required(' Return Accepting Username is required '),
      returnAcceptingPasswordOrPin: yup.string().required(' Password or Pin is required '),
    });

    const reviewSchema = yup.object().shape({
      everythingCorrect: yup.bool().required('This check is required!'),
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
          return clientSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: depositAmountReturned, errorMessage: depositAmountReturnedError} = useField('depositAmountReturned');
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
        requests.patchReturnContract(route.params.contractId, depositAmountReturned.value,
            depositReturningUser.value, depositReturningPassword.value,
            returnAcceptingUser.value, returnAcceptingPasswordOrPin.value).then(() => {
          toast.success('Contract Returned!', {timeout: 1000});
          requests.getContract(route.params.contractId).then((response) => {
            contract.value = response.data;
          });
        });
      } else {
        if (stepNumber.value === 0) {
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
      contract,
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


  data() {
    return {
      client: {},
      bike: {},
      depositCollectingUser: {},
      workingUser: {},
      checkingUser: {},
      contractId: this.$route.params.contractId,
      depositBearers: [],
      activeUsers: [],
      depositReturnedByUser: {},
      returnAcceptedByUser: {},
    };
  },
  methods: {
    extendContract() {
      requests.patchExtendContract(this.contractId).then(() => {
        toast.success('Contract Extended!', {timeout: 1000});
        requests.getContract(this.contractId).then((response) => {
          this.contract = response.data;
        });
      });
    },
  },
  async created() {
    this.contract = (await requests.getContract(this.$route.params.contractId)).data;
    this.bike = (await requests.getBike(this.contract.bikeId)).data;
    this.client = (await requests.getClient(this.contract.clientId)).data;
    this.depositCollectingUser = (await requests.getUser(this.contract['depositCollectingUserId'])).data;
    this.workingUser = (await requests.getUser(this.contract['workingUserId'])).data;
    this.checkingUser = (await requests.getUser(this.contract['checkingUserId'])).data;
    if (this.contract.returnedDate != null) {
      this.returnAcceptedByUser = (await requests.getUser(this.contract['returnAcceptingUserId'])).data;
      this.depositReturnedByUser = (await requests.getUser(this.contract['depositReturningUserId'])).data;
    };
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
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-4 gap-5">
          <Card title="Lendee">
            <div class="flex flex-col h-full">
              <div class="flex-1">
                <p class="text-slate-600 dark:text-slate-300">{{client.firstName}} {{client.lastName}}</p>
                <p class="text-slate-600 dark:text-slate-300">{{client.emailAddress}}</p>
              </div>
              <DashButton @click="this.$router.push({path: `/clients/${client.id}`})">
                View Client
              </DashButton>
            </div>
          </Card>
        </div>
        <div class="col-span-4 gap-5">
          <Card title="Bike">
            <p class="text-slate-600 dark:text-slate-300">{{bike.make}} {{bike.model}}</p>
            <p class="text-slate-600 dark:text-slate-300">{{bike.colour}} {{bike.decals}}</p>
            <p class="text-slate-600 dark:text-slate-300">{{bike.serialNumber}}</p>

          </Card>
        </div>
        <div class="col-span-4 gap-5">
          <Card title="Contract">
            <div class="flex flex-col h-full">
              <div class="flex-1">
                <p class="text-slate-600 dark:text-slate-300">From: {{contract.startDate}}&emsp; Until: {{contract.endDate}}</p>
                <p class="text-slate-600 dark:text-slate-300">Notes: {{contract.notes}}</p>
                <p class="text-slate-600 dark:text-slate-300">Condition: {{contract.condition}}</p>
                <p class="text-slate-600 dark:text-slate-300">Deposit: &#163;{{contract.depositAmountCollected}} to {{depositCollectingUser.username}}</p>
                <p class="text-slate-600 dark:text-slate-300">Done by: {{workingUser.username}}</p>
                <p class="text-slate-600 dark:text-slate-300">Checked by: {{checkingUser.username}}</p>
              </div>
              <DashButton class="mt-5" @click="extendContract">
                Extend Contract
              </DashButton>
            </div>
          </Card>
        </div>
        <div class="col-span-12 gap-5">
          <Card title="Return">
            <div v-if="contract.returnedDate == null">
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
                      </div>
                      <div class="col-span-1">
                        <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Please check all the details!</h5>
                        <Checkbox
                            label="I confirm this information is correct!"
                            name="everythingCorrect"
                            v-model="everythingCorrect"
                            :error="everythingCorrectError"/>
                        <ErrorMessage name="everythingCorrect" :error="everythingCorrectError"></ErrorMessage>
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
            <div v-else>
              <p class="text-slate-600 dark:text-slate-300">Returned on {{contract.returnedDate}}</p>
              <p class="text-slate-600 dark:text-slate-300">Deposit returned: &#163; {{contract.depositAmountReturned}} by {{depositReturnedByUser.username}}</p>
              <p class="text-slate-600 dark:text-slate-300">Received by {{returnAcceptedByUser.username}}</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
