<script>
import Card from '@/components/Card/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import {ref} from 'vue';

const toast = useToast();

export default {
  name: 'basicSettings',
  components: {DashButton, Textinput, Button, Card},
  setup() {
    const contractTypes = ref([]);
    const expenseTypes = ref([]);

    const newAddressSchema = yup.object().shape({
      number: yup.string().required('Street Number is required'),
      street: yup.string().required('Street Name is required'),
      postcode: yup.string().required('Postcode is required'),
      city: yup.string().required('City is required'),
    });

    const newContractTypeSchema = yup.object().shape({
      newContractTypeId: yup.string().max(20).required(),
    });

    const newExpenseTypeSchema = yup.object().shape({
      newExpenseTypeId: yup.string().max(20).required(),
      newExpenseTypeDescription: yup.string().required(),
    });

    const {handleSubmit: handleUpdateAddressSubmit} = useForm({
      validationSchema: newAddressSchema,
      keepValuesOnUnmount: true,
    });

    const {handleSubmit: handleNewContractTypeSubmit} = useForm({
      validationSchema: newContractTypeSchema,
      keepValuesOnDismount: true,
    });

    const {handleSubmit: handleNewExpenseTypeSubmit} = useForm({
      validationSchema: newExpenseTypeSchema,
      keepValuesOnDismount: true,
    });

    const {value: number, errorMessage: numberError} = useField('number');
    const {value: street, errorMessage: streetError} = useField('street');
    const {value: postcode, errorMessage: postcodeError} = useField('postcode');
    const {value: city, errorMessage: cityError} = useField('city');

    const {value: newContractTypeId, errorMessage: newContractTypeIdError, resetField: resetNewContractTypeId} = useField('newContractTypeId');

    const {value: newExpenseTypeId, errorMessage: newExpenseTypeIdError, resetField: resetNewExpenseTypeId} = useField('newExpenseTypeId');
    const {value: newExpenseTypeDescription, errorMessage: newExpenseTypeDescriptionError, resetField: resetNewExpenseTypeDescription} = useField('newExpenseTypeDescription');

    const submitChangeDetails = handleUpdateAddressSubmit(() => {
      requests.putAddress(
          {
            number: number.value,
            street: street.value,
            postcode: postcode.value,
            city: city.value,
          }).then((response) => {
        toast.success('Address updated', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    const submitNewContractType = handleNewContractTypeSubmit(() => {
      requests.postContractType(newContractTypeId.value).then((response) => {
        console.log(response);
        contractTypes.value.push(response.data);
        resetNewContractTypeId();
        toast.success('Contract Type created', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    const submitNewExpenseType = handleNewExpenseTypeSubmit(() => {
      requests.postNewExpenseType(newExpenseTypeId.value, newExpenseTypeDescription.value).then((response) => {
        expenseTypes.value.push(response.data);
        resetNewExpenseTypeId();
        resetNewExpenseTypeDescription();
        toast.success('Expense Type created', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      number,
      numberError,
      street,
      streetError,
      postcode,
      postcodeError,
      city,
      cityError,
      submitChangeDetails,
      contractTypes,
      newContractTypeId,
      newContractTypeIdError,
      submitNewContractType,
      expenseTypes,
      newExpenseTypeId,
      newExpenseTypeIdError,
      newExpenseTypeDescription,
      newExpenseTypeDescriptionError,
      submitNewExpenseType,
    };
  },
  data() {
    return {
      address: null,
    };
  },
  mounted() {
    requests.getAddress().then((response) => {
      this.address = response.data;
      this.number = this.address.number;
      this.street = this.address.street;
      this.postcode = this.address.postcode;
      this.city = this.address.city;
    });
    requests.getContractTypes().then((response) => {
      this.contractTypes = response.data;
    });
    requests.getExpenseTypes().then((response) => {
      this.expenseTypes = response.data;
    });
  },
  methods: {
    deleteContractType(contractTypeId) {
      requests.deleteContractType(contractTypeId).then((response) => {
        const indexInArray = this.contractTypes.findIndex((t) => (t.id === response.data.id));
        this.contractTypes.splice(indexInArray, 1);
        toast.success('Contract Type deleted', {timeout: 2000});
      });
    },
    deleteExpenseType(expenseTypeId) {
      requests.deleteExpenseType(expenseTypeId).then((response) => {
        const indexInArray = this.expenseTypes.findIndex((t) => (t.id === response.data.id));
        this.expenseTypes.splice(indexInArray, 1);
        toast.success('Expense Type deleted', {timeout: 2000});
      });
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <Card title="Update Address">
        <form @submit.prevent="submitChangeDetails">
          <div class="grid grid-cols-12 gap-5">
            <div class="md:col-span-6 col-span-12">
              <Textinput
                  label="Street Number"
                  type="text"
                  placeholder="21-23"
                  name="number"
                  v-model="number"
                  :error="numberError"
              />
            </div>
            <div class="md:col-span-6 col-span-12">
              <Textinput
                  label="Street Name"
                  type="text"
                  placeholder="High Street"
                  name="street"
                  v-model="street"
                  :error="streetError"
              />
            </div>
            <div class="col-span-6">
              <Textinput
                  label="Post Code"
                  type="text"
                  placeholder="AB24 3EE"
                  name="postcode"
                  v-model="postcode"
                  :error="postcodeError"
              />
            </div>
            <div class="col-span-6">
              <Textinput
                  label="City"
                  type="text"
                  placeholder="Aberdeen"
                  name="city"
                  v-model="city"
                  :error="cityError"
              />
            </div>
            <div class="col-span-12">
              <Button type="submit" class="btn btn-dark block w-full text-center">
                Submit
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
    <div class="col-span-6 row-span-2">
      <Card title="Manage Expense Types">
        <form @submit.prevent="submitNewExpenseType">
          <div class="grid grid-cols-8 gap-2">
            <div class="col-span-2">
              <span class="text-slate-700 dark:text-slate-300 text-xl">Expense Type</span>
            </div>
            <div class="col-span-4">
              <span class="text-slate-700 dark:text-slate-300 text-xl">Description</span>
            </div>
            <div class="col-span-2">
              <span class="text-slate-700 dark:text-slate-300 text-xl">Action</span>
            </div>
            <template v-for="expenseType in expenseTypes" :key="expenseType.id">
              <div class="col-span-2">
                <span class="text-slate-700 dark:text-slate-300">{{expenseType.id}}</span>
              </div>
              <div class="col-span-4">
                <span class="text-slate-700 dark:text-slate-300">{{expenseType.description}}</span>
              </div>
              <div class="col-span-1">
                <DashButton @click="editExpenseType(expenseType.id)" class="btn-sm mx-auto block-btn">Edit</DashButton>
              </div>
              <div class="col-span-1">
                <DashButton @click="deleteExpenseType(expenseType.id)" class="bg-danger-600 btn-sm mx-auto block-btn">Delete</DashButton>
              </div>
            </template>
            <div class="col-span-2">
              <Textinput
                  type="text"
                  placeholder="New Expense Type"
                  name="newExpenseTypeId"
                  v-model="newExpenseTypeId"
                  :error="newExpenseTypeIdError"
              />
            </div>
            <div class="col-span-4">
              <Textinput
                  type="text"
                  placeholder="Description"
                  name="newExpenseTypeDescription"
                  v-model="newExpenseTypeDescription"
                  :error="newExpenseTypeDescriptionError"
              />
            </div>
            <div class="col-span-2">
              <DashButton type="submit" class="btn-sm mx-auto block-btn">
                Add
              </DashButton>
            </div>
          </div>
        </form>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Manage Contract Types">
        <form @submit.prevent="submitNewContractType">
          <div class="grid grid-cols-4 gap-2">
            <div class="col-span-3">
              <span class="text-slate-700 dark:text-slate-300 text-xl">Contract Type</span>
            </div>
            <div class="col-span-1">
              <span class="text-slate-700 dark:text-slate-300 text-xl">Action</span>
            </div>
            <template v-for="contractType in contractTypes" :key="contractType.id">
              <div class="col-span-3">
                <span class="text-slate-700 dark:text-slate-300">{{contractType.id}}</span>
              </div>
              <div class="col-span-1">
                <DashButton @click="deleteContractType(contractType.id)" class="bg-danger-600 btn-sm mx-auto block-btn">Delete</DashButton>
              </div>
            </template>
            <div class="col-span-3">
              <Textinput
                  type="text"
                  placeholder="New Contract Type"
                  name="newContractType"
                  v-model="newContractTypeId"
                  :error="newContractTypeIdError"
              />
            </div>
            <div class="col-span-1">
              <DashButton type="submit" class="btn-sm mx-auto block-btn">
                Add
              </DashButton>
            </div>
          </div>
        </form>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
