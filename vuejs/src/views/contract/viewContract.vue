<script>
import TextInput from '@/components/TextInput/index.vue';
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import {computed, ref, toRef} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useCredentialsStore} from '@/store/credentialsStore';
import ContractClientCardSkeleton from '@/components/Skeleton/ContractClientCardSkeleton.vue';
import ContractBikeCardSkeleton from '@/components/Skeleton/ContractBikeCardSkeleton.vue';
import ContractCardSkeleton from '@/components/Skeleton/ContractCardSkeleton.vue';
import Icon from '@/components/Icon';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import nfc from '@/nfc';
import {useToast} from 'vue-toastification';
import SubmitCrimeReportCard from '@/components/Card/SubmitCrimeReportCard.vue';
import Tooltip from '@/components/Tooltip/index.vue';

const toast = useToast();

export default {
  name: 'viewContract',
  components: {
    Tooltip,
    SubmitCrimeReportCard,
    ComboboxTextInput,
    Card,
    DashButton,
    TextInput,
    ContractClientCardSkeleton,
    ContractBikeCardSkeleton,
    ContractCardSkeleton,
    Icon,
  },
  setup(props, context) {
    const credentialsStore = useCredentialsStore();
    const contractData = toRef(props, 'contract');
    const depositAmountCollected = computed(() => {
      return Math.abs(
        contractData.value.depositCollectedTransactionHeader ?
          contractData.value.depositCollectedTransactionHeader
            .transactionLines
            .find((l) => l.account.type === 'liability' ).amount :
          0,
      );
    });
    const patchContractReturn = toRef(props, 'patchContractReturn');
    const isInWriteMode = ref(false);
    const userSelectionOptionsStatic = ref(true);

    const depositLiabilityAccounts = toRef(props, 'depositLiabilityAccounts');
    const depositAssetAccounts = toRef(props, 'depositAssetAccounts');
    const depositRevenueAccounts = toRef(props, 'depositRevenueAccounts');

    const steps = [
      {
        id: 1,
        title: 'Accepting Volunteer',
      },
      {
        id: 2,
        title: 'Deposit Return',
      },
    ];

    const stepNumber = ref(0);

    const depositReturningSchema = yup.object().shape({
      depositAmountReturned: yup.number().min(0, 'Must be positive').integer()
        .required(' Deposit Amount is required '),
      depositReturnedLiabilityAccount: yup.object().shape({
        id: yup.string().uuid().required(' The deposit liability account id is required '),
        name: yup.string().required(' The deposit liability account name is required '),
      }).required(' The deposit liability account is required '),
      depositReturnedAssetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The deposit asset account id is required '),
        name: yup.string().required(' The deposit asset account name is required '),
      }).required(' The deposit asset account is required '),
      depositReturnedRevenueAccount: yup.object().shape({
        id: yup.string().uuid().required(' The deposit asset account id is required '),
        name: yup.string().required(' The deposit asset account name is required '),
      }).required(' The deposit asset account is required '),
      depositReturningPassword: yup.string().required(),
    });

    const returnAcceptingUserSchema = yup.object().shape({
      returnAcceptingUser: yup.string().required(' Return Accepting Username is required '),
      returnAcceptingPasswordOrPin: yup.string().required(' Password or Pin is required '),
    });


    const currentSchema = computed(() => {
      switch (stepNumber.value) {
      case 0:
        return returnAcceptingUserSchema;
      case 1:
        return depositReturningSchema;
      default:
        return depositReturningSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: depositAmountReturned, errorMessage: depositAmountReturnedError,
      setErrors: depositAmountReturnedSetErrors} = useField('depositAmountReturned');
    const {
      value: depositReturnedLiabilityAccount,
      errorMessage: depositReturnedLiabilityAccountError,
    } = useField('depositReturnedLiabilityAccount');
    const {value: depositReturnedAssetAccount, errorMessage: depositReturnedAssetAccountError} = useField('depositReturnedAssetAccount');
    const {
      value: depositReturnedRevenueAccount,
      errorMessage: depositReturnedRevenueAccountError,
    } = useField('depositReturnedRevenueAccount');
    const {value: depositReturningPassword, errorMessage: depositReturningPasswordError,
      setErrors: depositReturningPasswordSetErrors} = useField('depositReturningPassword');

    const depositSettledTransactionHeader = ref({});

    depositReturnedLiabilityAccount.value = {name: null, id: null};
    depositReturnedAssetAccount.value = {name: null, id: null};
    depositReturnedRevenueAccount.value = {name: null, id: null};

    const {value: returnAcceptingUser, errorMessage: returnAcceptingUserError} = useField('returnAcceptingUser');
    const {value: returnAcceptingPasswordOrPin, errorMessage: returnAcceptingPasswordOrPinError,
      setErrors: returnAcceptingPasswordOrPinSetErrors} = useField('returnAcceptingPasswordOrPin');

    returnAcceptingUser.value = '';

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      if (stepNumber.value === 0) {
        // handle return accepting user
        requests.checkUserPasswordOrPin(returnAcceptingUser.value, returnAcceptingPasswordOrPin.value).then((response) => {
          if (response.data) {
            stepNumber.value = 1;
          } else {
            returnAcceptingPasswordOrPinSetErrors('Wrong Password or Pin!');
          }
        });
      } else if (stepNumber.value === 1) {
        if (depositAmountReturned.value * 100 > depositAmountCollected.value) {
          depositAmountReturnedSetErrors('Must not be larger than the deposit collected!');
          return;
        }

        const depositReturnedTransactionDraft = {
          transactionHeader: {
            event: 'deposit_returned',
          },
          transactionLines: [
            {amount: depositAmountCollected.value, accountId: depositReturnedLiabilityAccount.value.id},
            {amount: - depositAmountReturned.value * 100, accountId: depositReturnedAssetAccount.value.id},
            depositAmountReturned.value * 100 < depositAmountCollected.value ?
              {amount: -(depositAmountCollected.value - depositAmountReturned.value * 100),
                accountId: depositReturnedRevenueAccount.value.id} :
              undefined,
          ],
          attemptAutoPost: false,
        };

        requests.createTransaction(depositReturnedTransactionDraft).then((response) => {
          if (response.data) {
            depositSettledTransactionHeader.value = response.data;
            toast.success('Deposit Settled Successfully!');

            patchContractReturn.value(
              depositSettledTransactionHeader.value.id,
              depositReturnedAssetAccount.value.ownerUser.username,
              depositReturningPassword.value,
              returnAcceptingUser.value, returnAcceptingPasswordOrPin.value);
          } else {
            depositReturningPasswordSetErrors('Wrong Password!');
            toast.error(response.data.detail.description, {timeout: 1000});
          }
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 1000});
        });
      }
    });

    const prev = () => {
      stepNumber.value--;
    };

    return {
      isInWriteMode,
      contractData,
      depositAmountCollected,
      credentialsStore,
      depositAmountReturned,
      depositAmountReturnedError,
      depositReturnedLiabilityAccount,
      depositReturnedLiabilityAccountError,
      depositReturnedAssetAccount,
      depositReturnedAssetAccountError,
      depositReturnedRevenueAccount,
      depositReturnedRevenueAccountError,
      depositReturningPassword,
      depositReturningPasswordError,

      returnAcceptingUser,
      returnAcceptingUserError,
      returnAcceptingPasswordOrPin,
      returnAcceptingPasswordOrPinError,
      
      userSelectionOptionsStatic,

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
    userSortingFunction(user1, user2) {
      if (user1.toLowerCase() > user2.toLowerCase()) return 1;
      if (user1.toLowerCase() < user2.toLowerCase()) return -1;
      return 0;
    },
    selectDepositReturnedLiabilityAccount(event, i) {
      if (i !== -1) {
        this.depositReturnedLiabilityAccount = this.filtered_deposit_returned_liability_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectDepositReturnedAssetAccount(event, i) {
      if (i !== -1) {
        this.depositReturnedAssetAccount = this.filtered_deposit_returned_asset_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectDepositReturnedRevenueAccount(event, i) {
      if (i !== -1) {
        this.depositReturnedRevenueAccount = this.filtered_deposit_returned_revenue_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectReturnAcceptingUser(event, i) {
      if (i !== -1) {
        this.returnAcceptingUser = this.filtered_return_accepting_user_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },
    writeBikeDetailsToNfcTag() {
      this.isInWriteMode = true;
      nfc.writeBikeDetailsToNfcTag(this.bike)
        .then((tagSerialNumber) => {
          toast.success('Details written.');
          const bikeCopy = this.bike;
          bikeCopy.rfidTagSerialNumber = tagSerialNumber;
          requests.patchBikeChangeDetails(this.bike.id, bikeCopy)
            .then(() => {
              toast.success('RFID Tag Serial Number recorded.', {timeout: 1000});
            })
            .catch((error) => {
              toast.error(error.response.data.detail.description, {timeout: 1000});
            });
        })
        .catch((error) => {
          toast.error(error.message, {timeout: 1000});
        })
        .finally(() => {
          this.isInWriteMode = false;
        });
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
    returnAcceptedByUsername: {
      type: String,
      required: false,
    },
    depositLiabilityAccounts: {
      type: Array,
      required: false,
      default: () => [],
    },
    depositAssetAccounts: {
      type: Array,
      required: false,
      default: () => [],
    },
    depositRevenueAccounts: {
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
    isUserAdmin: {
      type: Boolean,
      default: false,
    },
    openEditClientDetailsModal: {
      type: Function,
      required: true,
    },
    goToBike: {
      type: Function,
      default: () => {},
    },
    openEditBikeDetailsModal: {
      type: Function,
      default: () => {},
    },
    openEditContractDetailsModal: {
      type: Function,
      default: () => {},
    },
    patchCloseCrimeReport: {
      type: Function,
      default: () => {},
    },
  },
  computed: {
    filtered_deposit_returned_liability_account_suggestions() {
      return this.depositLiabilityAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.depositReturnedLiabilityAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_deposit_returned_asset_account_suggestions() {
      return this.depositAssetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.depositReturnedAssetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_deposit_returned_revenue_account_suggestions() {
      return this.depositRevenueAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.depositReturnedRevenueAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_return_accepting_user_suggestions() {
      return this.activeUsers
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith(this.returnAcceptingUser.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },
  emits: ['crimeReportAdded'],
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
              <div class="grid grid-cols-12 h-full gap-5">
                <div class="col-span-12" >
                  <p class="text-slate-600 dark:text-slate-300">{{client.firstName}} {{client.lastName}}</p>
                  <p class="text-slate-600 dark:text-slate-300">{{client.emailAddress}}</p>
                </div>
                <div class="col-span-6 mt-auto">
                  <DashButton class="w-full" @click="goToClient">
                    View Client
                  </DashButton>
                </div>
                <div class="col-span-6 mt-auto">
                  <DashButton class="w-full" @click="openEditClientDetailsModal">
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
              <div class="grid grid-cols-12 h-full gap-5">
                <div class="col-span-12 col-start-1">
                  <p class="text-slate-600 dark:text-slate-300">{{bike.make}} {{bike.model}}</p>
                  <p class="text-slate-600 dark:text-slate-300">{{bike.colour}} {{bike.decals}}</p>
                  <p class="text-slate-600 dark:text-slate-300">{{bike.serialNumber}}</p>
                </div>
                <div class="col-span-12 col-start-1">
                  <div class="h-10 rounded-full overflow-hidden">
                    <div :class="`w-full h-full rounded-full overflow-hidden grid grid-cols-${bike.colours.length}`">
                      <template
                          v-for="c in bike.colours"
                          :key="c.name"
                      >
                        <Tooltip placement="top" arrow theme="dark" btn-class="col-span-1" :btn-style="{backgroundColor: c.hex}">
                          <template #button>
                            <div class="w-full h-full"></div>
                          </template>
                          <span>{{ c.name }} ({{ c.hex }})</span>
                        </Tooltip>
                      </template>
                    </div>
                  </div>
                </div>
                <div v-if="isUser" class="col-span-6 col-start-1 mt-auto">
                  <DashButton class="w-full" @click="goToBike">
                    View Bike
                  </DashButton>
                </div>
                <div v-if="isUser" class="col-span-6 mt-auto">
                  <DashButton class="w-full" @click="openEditBikeDetailsModal">
                    Edit Details
                  </DashButton>
                </div>
<!--                <div v-if="isUser" class="col-span-4 mt-auto">-->
<!--                  <DashButton class="w-full" @click="writeBikeDetailsToNfcTag">-->
<!--                    Write To NFC-->
<!--                  </DashButton>-->
<!--                </div>-->
              </div>
            </template>
          </Card>
        </div>
        <div class="col-span-12 lg:col-span-4 gap-5">
          <Card title="Contract">
            <template #header v-if="isUserAdmin && !loadingContract">
              <div  class="col-span-6 mt-auto">
                <DashButton class="w-full btn-sm bg-danger-600" @click="openEditContractDetailsModal">
                  Edit Details
                </DashButton>
              </div>
            </template>
            <template v-if="loadingContract">
              <ContractCardSkeleton v-if="loadingContract"></ContractCardSkeleton>
            </template>
            <template v-else>
              <div class="flex flex-col h-full">
                <div class="flex-1">
                  <p class="text-slate-600 dark:text-slate-300">
                      From: {{new Date(Date.parse(contract.startDate))
                      .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}
                  </p>
                  <p class="text-slate-600 dark:text-slate-300">
                      Until: {{new Date(Date.parse(contract.endDate))
                      .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}
                  </p>
                  <p class="text-slate-600 dark:text-slate-300">Notes: {{contract.notes}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Contract Type: {{contract.contractType}}</p>
                  <p class="text-slate-600 dark:text-slate-300">Condition: {{contract.conditionOfBike}}</p>
                  <p class="text-slate-600 dark:text-slate-300 w-100">
                      Deposit:
                    <table class="border-collapse border dark:border-slate-400 min-w-full">
                      <tr class=" dark:bg-slate-700">
                        <th class="border dark:border-slate-500">Account</th>
                        <th class="border dark:border-slate-500">Credit</th>
                        <th class="border dark:border-slate-500">Debit</th>
                      </tr>
                      <tr v-for="line in contract.depositCollectedTransactionHeader.transactionLines" :key="line.id">
                        <td class="border dark:border-slate-500">{{line.account.name}}</td>
                        <td class="border dark:border-slate-500">{{ line.amount < 0 ? `&#163; ${(-line.amount / 100).toFixed(2)}` : '' }}</td>
                        <td class="border dark:border-slate-500">{{ line.amount > 0 ? `&#163; ${(line.amount / 100).toFixed(2)}` : '' }}</td>
                      </tr>
                    </table>

                  </p>
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
        <div class="col-span-12 gap-5" v-if="
        !loadingContract &&
        (((contract.returnedDate == null) && isUser) || (contract.returnedDate != null)) &&
        contract.crimeReports.filter((report) => (report.closedOn === null)).length === 0">
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
                <form @submit.prevent="submit"  @keydown.enter="submit">
                  <div v-if="stepNumber === 0">
                    <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                      <div class="md:col-span-2 col-span-1">
                        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                          Return Accepting Volunteer
                        </h4>
                      </div>

                      <ComboboxTextInput
                          :field-model-value="returnAcceptingUser"
                          :suggestions="filtered_return_accepting_user_suggestions"
                          :selected-callback="selectReturnAcceptingUser"
                          :allow-new="false"
                          :open-by-default="false"
                          label="Return Accepting Volunteer"
                          type="text"
                          placeholder="workshop"
                          name="returnAcceptingUser"
                          v-model="returnAcceptingUser"
                          :error="returnAcceptingUserError"
                          @input="() => {}"
                      />

                      <TextInput
                          label="Password or Pin"
                          type="password"
                          placeholder="Password or Pin"
                          name="returnAcceptingUserPasswordOrPin"
                          v-model="returnAcceptingPasswordOrPin"
                          :error="returnAcceptingPasswordOrPinError"
                          hasicon/>
                    </div>
                  </div>
                  <div v-if="stepNumber === 1">
                    <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                      <div class="lg:col-span-3 md:col-span-2 col-span-1">
                        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                          Deposit Return
                        </h4>
                      </div>
                      <TextInput
                          label="Deposit Amount (&pound;)"
                          type="number"
                          placeholder="40"
                          name="depositAmountReturned"
                          v-model="depositAmountReturned"
                          :error="depositAmountReturnedError"
                      />

                      <ComboboxTextInput
                        :field-model-value="depositReturnedLiabilityAccount.name"
                        :suggestions="filtered_deposit_returned_liability_account_suggestions.map(makeAccountLegible)"
                        :selected-callback="selectDepositReturnedLiabilityAccount"
                        :allow-new="false"
                        :open-by-default="userSelectionOptionsStatic"
                        label="Liability Account"
                        type="text"
                        placeholder="workshop"
                        name="depositReturnedLiabilityAccount"
                        v-model="depositReturnedLiabilityAccount.name"
                        :error="depositReturnedLiabilityAccountError"
                        @change="() => {}"
                      />

                      <ComboboxTextInput
                        :field-model-value="depositReturnedAssetAccount.name"
                        :suggestions="filtered_deposit_returned_asset_account_suggestions.map(makeAccountLegible)"
                        :selected-callback="selectDepositReturnedAssetAccount"
                        :allow-new="false"
                        :open-by-default="userSelectionOptionsStatic"
                        label="Asset Account"
                        type="text"
                        placeholder="workshop"
                        name="depositReturnedAssetAccount"
                        v-model="depositReturnedAssetAccount.name"
                        :error="depositReturnedAssetAccountError"
                        @change="() => {}"
                      />

                      <ComboboxTextInput v-if="depositAmountReturned ?? 100000000 < depositAmountCollected"
                        :field-model-value="depositReturnedRevenueAccount.name"
                        :suggestions="filtered_deposit_returned_revenue_account_suggestions.map(makeAccountLegible)"
                        :selected-callback="selectDepositReturnedRevenueAccount"
                        :allow-new="false"
                        :open-by-default="userSelectionOptionsStatic"
                        label="Revenue Account"
                        type="text"
                        placeholder="workshop"
                        name="depositReturnedRevenueAccount"
                        v-model="depositReturnedRevenueAccount.name"
                        :error="depositReturnedRevenueAccountError"
                        @change="() => {}"
                      />

                      <TextInput
                          label="Deposit Returner Password"
                          type="password"
                          placeholder="Password"
                          name="depositReturningPassword"
                          v-model="depositReturningPassword"
                          :error="depositReturningPasswordError"
                          hasicon/>
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
              <p class="text-slate-600 dark:text-slate-300">
                  Returned on {{new Date(Date.parse(contract.returnedDate))
                  .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}
              </p>
              <p class="text-slate-600 dark:text-slate-300 w-100">
                Deposit Settlement:
                <table class="border-collapse border dark:border-slate-400 min-w-full">
                  <tr class=" dark:bg-slate-700">
                    <th class="border dark:border-slate-500">Account</th>
                    <th class="border dark:border-slate-500">Credit</th>
                    <th class="border dark:border-slate-500">Debit</th>
                  </tr>
                  <tr v-for="line in contract.depositSettledTransactionHeader.transactionLines" :key="line.id">
                    <td class="border dark:border-slate-500">{{line.account.name}}</td>
                    <td class="border dark:border-slate-500">{{ line.amount < 0 ? `&#163; ${(-line.amount / 100).toFixed(2)}` : '' }}</td>
                    <td class="border dark:border-slate-500">{{ line.amount > 0 ? `&#163; ${(line.amount / 100).toFixed(2)}` : '' }}</td>
                  </tr>
                </table>

              </p>
              <p class="text-slate-600 dark:text-slate-300">Received by {{returnAcceptedByUsername}}</p>
            </div>
          </Card>
        </div>
        <template v-if="!loadingContract">
          <template v-if="
          isUser &&
          contractData.returnedDate == null &&
          contractData.crimeReports.filter((report) => (report.closedOn === null)).length === 0">
            <div class="col-span-12 lg:col-span-4 gap-5">
              <SubmitCrimeReportCard
              :contract-id="contract.id"
              @crime-report-added="(report) => $emit('crimeReportAdded', report)"/>
            </div>
          </template>
          <div
              v-for="crimeReport in contract.crimeReports.toSorted((report) => (report.createdOn)).reverse()"
              :key="crimeReport.id"
              class="col-span-12 lg:col-span-4 gap-5" >
            <Card
                :key="crimeReport.id"
                  title="Crime Report">
              <div class="flex flex-col h-full">
                <div class="flex-1">
                  <p class="text-slate-600 dark:text-slate-300">
                    Created: {{new Date(Date.parse(crimeReport.createdOn))
                      .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}
                  </p>
                  <p class="text-slate-600 dark:text-slate-300">
                    Crime Number: {{crimeReport.crimeNumber}}
                  </p>
                  <p
                      v-if="crimeReport.closedOn !== null"
                      class="text-slate-600 dark:text-slate-300">
                    Closed: {{new Date(Date.parse(crimeReport.closedOn))
                      .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}}
                  </p>
                </div>
                <DashButton
                    v-if="isUser && crimeReport.closedOn === null"
                    class="mt-5"
                    @click="() => patchCloseCrimeReport(crimeReport.id)">
                  Close Crime Report
                </DashButton>
              </div>

            </Card>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
