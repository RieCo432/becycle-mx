<script>
import Textinput from '@/components/Textinput/index.vue';
import Button from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import {ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'ManageExpenseTypesCard',
  components: {DashButton, Card, Button, Textinput},
  setup() {
    const expenseTypes = ref([]);
    const editExpenseTypeId = ref(null);

    const editExpenseTypeSchema = yup.object().shape({
      editExpenseTypeDescription: yup.string().required(),
    });

    const {handleSubmit: handleEditExpenseTypeSubmit} = useForm({
      validationSchema: editExpenseTypeSchema,
      keepValuesOnDismount: true,
    });

    const {value: editExpenseTypeDescription, errorMessage: editExpenseTypeDescriptionError} = useField('editExpenseTypeDescription');

    const submitEditExpenseType = handleEditExpenseTypeSubmit(() => {
      requests.patchExpenseType(editExpenseTypeId.value, editExpenseTypeDescription.value).then((response) => {
        const indexInArray = expenseTypes.value.findIndex((t) => (t.id === editExpenseTypeId.value));
        expenseTypes.value.splice(indexInArray, 1, response.data);
        toast.success('Expense Type updated', {timeout: 2000});
        editExpenseTypeId.value = null;
      });
    });

    const newExpenseTypeSchema = yup.object().shape({
      newExpenseTypeId: yup.string().max(20).required(),
      newExpenseTypeDescription: yup.string().required(),
    });

    const {handleSubmit: handleNewExpenseTypeSubmit} = useForm({
      validationSchema: newExpenseTypeSchema,
      keepValuesOnDismount: true,
    });

    const {value: newExpenseTypeId, errorMessage: newExpenseTypeIdError, resetField: resetNewExpenseTypeId} = useField('newExpenseTypeId');
    const {value: newExpenseTypeDescription, errorMessage: newExpenseTypeDescriptionError, resetField: resetNewExpenseTypeDescription} = useField('newExpenseTypeDescription');

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
      expenseTypes,
      newExpenseTypeId,
      newExpenseTypeIdError,
      newExpenseTypeDescription,
      newExpenseTypeDescriptionError,
      submitNewExpenseType,
      editExpenseTypeId,
      editExpenseTypeDescription,
      editExpenseTypeDescriptionError,
      submitEditExpenseType,
    };
  },
  mounted() {
    requests.getExpenseTypes().then((response) => {
      this.expenseTypes = response.data;
    });
  },
  methods: {
    deleteExpenseType(expenseTypeId) {
      requests.deleteExpenseType(expenseTypeId).then((response) => {
        const indexInArray = this.expenseTypes.findIndex((t) => (t.id === response.data.id));
        this.expenseTypes.splice(indexInArray, 1);
        toast.success('Expense Type deleted', {timeout: 2000});
      });
    },
    editExpenseType(expenseTypeId, expenseTypeDescription) {
      this.editExpenseTypeId = expenseTypeId;
      this.editExpenseTypeDescription = expenseTypeDescription;
    },
  },
};
</script>

<template>
  <Card title="Manage Expense Types">
    <form @submit.prevent="submitEditExpenseType">
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
          <div v-if="editExpenseTypeId == null || editExpenseTypeId !== expenseType.id" class="col-span-4">
            <span class="text-slate-700 dark:text-slate-300">{{expenseType.description}}</span>
          </div>
          <div v-if="editExpenseTypeId === expenseType.id" class="col-span-4">
            <Textinput
                type="text"
                placeholder="New Description"
                name="editExpenseTypeDescription"
                v-model="editExpenseTypeDescription"
                :error="editExpenseTypeDescriptionError"
            />
          </div>
          <div v-if="editExpenseTypeId == null" class="col-span-1">
            <DashButton @click="editExpenseType(expenseType.id, expenseType.description)" class="btn-sm mx-auto block-btn">Edit</DashButton>
          </div>
          <div v-if="editExpenseTypeId != null && editExpenseTypeId === expenseType.id" class="col-span-1">
            <DashButton type="submit" class="btn-sm mx-auto block-btn">Submit</DashButton>
          </div>
          <div class="col-span-1">
            <DashButton @click="deleteExpenseType(expenseType.id)" class="bg-danger-600 btn-sm mx-auto block-btn">Delete</DashButton>
          </div>
        </template>
      </div>
    </form>
    <form @submit.prevent="submitNewExpenseType">
      <div class="grid grid-cols-8 gap-2 mt-2">
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
          <DashButton type="submit" @click="submitNewExpenseType" class="btn-sm mx-auto block-btn">Add</DashButton>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
