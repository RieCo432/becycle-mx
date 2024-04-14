<script>
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import {ref, toRef} from 'vue';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Textarea from '@/components/Textarea/index.vue';
import Select from '@/components/Select/index.vue';

const toast = useToast();

export default {
  name: 'EditContractDetailsModal',
  components: {ErrorMessage, Select, Textarea, Textinput, Button, Modal},
  setup(props, context) {
    const closeModal = toRef(props, 'closeModal');
    const contract = toRef(props, 'contract');
    const newDetailsSchema = yup.object().shape({
      startDate: yup.date().required('Start Date is required'),
      endDate: yup.date().required('End Date is required'),
      notes: yup.string().nullable(),
      contractType: yup.string().required('Contract Type is required'),
      conditionOfBike: yup.string().required('Condition is required'),
      depositAmountCollected: yup.number().min(0).integer().required('Deposit Amount is required'),
      depositCollectingUserId: yup.string().required('Deposit Collecting Volunteer is required'),
      workingUserId: yup.string().required('Working Volunteer is required'),
      checkingUserId: yup.string().required('Checking Volunteer is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: newDetailsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: startDate, errorMessage: startDateError} = useField('startDate');
    const {value: endDate, errorMessage: endDateError} = useField('endDate');
    const {value: notes, errorMessage: notesError} = useField('notes');
    const {value: contractType, errorMessage: contractTypeError} = useField('contractType');
    const {value: conditionOfBike, errorMessage: conditionOfBikeError} = useField('conditionOfBike');
    const {value: depositAmountCollected, errorMessage: depositAmountCollectedError} = useField('depositAmountCollected');
    const {value: depositCollectingUserId, errorMessage: depositCollectingUserIdError} = useField('depositCollectingUserId');
    const {value: workingUserId, errorMessage: workingUserIdError} = useField('workingUserId');
    const {value: checkingUserId, errorMessage: checkingUserIdError} = useField('checkingUserId');


    const submitChangeDetails = handleSubmit(() => {
      requests.patchContractChangeDetails(contract.value.id, {
        startDate: startDate.value,
        endDate: endDate.value,
        notes: notes.value,
        contractType: contractType.value,
        conditionOfBike: conditionOfBike.value,
        depositAmountCollected: depositAmountCollected.value,
        depositCollectingUserId: depositCollectingUserId.value,
        workingUserId: workingUserId.value,
        checkingUserId: checkingUserId.value,
      }).then((response) => {
        toast.success('Contract Details updated', {timeout: 2000});
        context.emit('contractDetailsUpdated');
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        closeModal.value();
      });
    });

    return {
      startDate,
      startDateError,
      endDate,
      endDateError,
      notes,
      notesError,
      contractType,
      contractTypeError,
      conditionOfBike,
      conditionOfBikeError,
      depositAmountCollected,
      depositAmountCollectedError,
      depositCollectingUserId,
      depositCollectingUserIdError,
      workingUserId,
      workingUserIdError,
      checkingUserId,
      checkingUserIdError,

      submitChangeDetails,
    };
  },
  emits: [
    'contractDetailsUpdated',
  ],
  props: {
    contract: {
      type: Object,
      required: true,
    },
    showModal: {
      type: Boolean,
      required: true,
    },
    closeModal: {
      type: Function,
      required: true,
    },
  },
  data() {
    return {
      allUsers: [],
      contractTypes: [],
      bikeConditions: [],
    };
  },
  mounted() {
    this.startDate = this.contract.startDate;
    this.endDate = this.contract.endDate;
    this.notes = this.contract.notes;
    this.conditionOfBike = this.contract.conditionOfBike;
    this.contractType = this.contract.contractType;
    this.depositAmountCollected = this.contract.depositAmountCollected;
    this.depositCollectingUserId = this.contract.depositCollectingUserId;
    this.workingUserId = this.contract.workingUserId;
    this.checkingUserId = this.contract.checkingUserId;

    requests.getBikeConditions().then((response) => (this.bikeConditions = response.data.map((cond) =>
        ({
          label: cond,
          value: cond,
        }),
    )));
    requests.getContractTypes().then((response) => (this.contractTypes = response.data.map((t) =>
        ({
          label: t,
          value: t,
        }),
    )));
    requests.getUsers().then((response) => (this.allUsers = response.data.map((user) =>
        ({
          label: user.username,
          value: user.id,
        }),
    )));
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Details">
    <form @submit.prevent="submitChangeDetails">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-6">
          <div class="col-span-4 content-center">
            <label class="text-slate-700 dark:text-slate-300">Start Date</label>
            <flat-pickr
                class="form-control m-auto"
                name="startDate"
                id="d3"
                placeholder="dd-mm-yyyy"
                v-model="startDate"
                :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            >
            </flat-pickr>
            <ErrorMessage name="startDate" :error="startDateError" class="text-danger-500"/>
          </div>
        </div>
        <div class="col-span-6">
          <div class="col-span-4 content-center">
            <label class="text-slate-700 dark:text-slate-300">End Date</label>
            <flat-pickr
                class="form-control m-auto"
                name="endDate"
                id="d3"
                placeholder="dd-mm-yyyy"
                v-model="endDate"
                :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            >
            </flat-pickr>
            <ErrorMessage name="endDate" :error="endDateError" class="text-danger-500"/>
          </div>
        </div>
        <div class="col-span-6">
          <Select
              :options="bikeConditions"
              label="Condition"
              v-model="conditionOfBike"
              name="conditionOfBike"
              :error="conditionOfBikeError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="contractTypes"
              label="Contract Type"
              v-model="contractType"
              name="contractType"
              :error="contractTypeError"
          />
        </div>
        <div class="col-span-12">
          <Textarea
              label="Notes"
              type="text"
              placeholder="anything noteworth"
              name="notes"
              v-model="notes"
              :error="notesError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="allUsers"
              label="Working Volunteer"
              v-model="workingUserId"
              name="workingUser"
              :error="workingUserIdError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="allUsers"
              label="Safety Checking User"
              v-model="checkingUserId"
              name="checkingUser"
              :error="checkingUserIdError"
          />
        </div>
        <div class="col-span-6">
          <Textinput
              label="Deposit Amount (&pound;)"
              type="number"
              placeholder="40"
              name="depositAmountCollected"
              v-model="depositAmountCollected"
              :error="depositAmountCollectedError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="allUsers"
              label="Deposit Collector"
              v-model="depositCollectingUserId"
              name="depositCollectingUser"
              :error="depositCollectingUserIdError"
          />
        </div>
        <div class="col-span-12">
          <Button type="submit" class="btn btn-dark block w-full text-center">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
