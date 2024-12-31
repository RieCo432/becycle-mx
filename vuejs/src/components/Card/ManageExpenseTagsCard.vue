<script>
import Textinput from '@/components/Textinput/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import {ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Checkbox from '@/components/Switch/index.vue';

const toast = useToast();

export default {
  name: 'ManageExpenseTagsCard',
  components: {Checkbox, DashButton, Card, Textinput},
  setup() {
    const expenseTags = ref([]);
    const editExpenseTagId = ref(null);

    const editExpenseTagSchema = yup.object().shape({
      editExpenseTagDescription: yup.string().required(),
      editExpenseTagActive: yup.bool(),
    });

    const {handleSubmit: handleEditExpenseTagSubmit} = useForm({
      validationSchema: editExpenseTagSchema,
      keepValuesOnDismount: true,
    });

    const {value: editExpenseTagDescription, errorMessage: editExpenseTagDescriptionError} = useField('editExpenseTagDescription');
    const {value: editExpenseTagActive} = useField('editExpenseTagActive');

    const submitEditExpenseTag = handleEditExpenseTagSubmit(() => {
      requests.patchExpenseTag(editExpenseTagId.value, editExpenseTagDescription.value, editExpenseTagActive.value).then((response) => {
        const indexInArray = expenseTags.value.findIndex((t) => (t.id === editExpenseTagId.value));
        expenseTags.value.splice(indexInArray, 1, response.data);
        toast.success('Expense Tag updated', {timeout: 2000});
        editExpenseTagId.value = null;
      });
    });

    const newExpenseTagSchema = yup.object().shape({
      newExpenseTagId: yup.string().max(20).required(),
      newExpenseTagDescription: yup.string().required(),
    });

    const {handleSubmit: handleNewExpenseTagSubmit} = useForm({
      validationSchema: newExpenseTagSchema,
      keepValuesOnDismount: true,
    });

    const {value: newExpenseTagId, errorMessage: newExpenseTagIdError, resetField: resetNewExpenseTagId} = useField('newExpenseTagId');
    const {value: newExpenseTagDescription, errorMessage: newExpenseTagDescriptionError,
      resetField: resetNewExpenseTagDescription} = useField('newExpenseTagDescription');

    const submitNewExpenseTag = handleNewExpenseTagSubmit(() => {
      requests.postNewExpenseTag(newExpenseTagId.value, newExpenseTagDescription.value).then((response) => {
        expenseTags.value.push(response.data);
        resetNewExpenseTagId();
        resetNewExpenseTagDescription();
        toast.success('Expense Tag created', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      expenseTags,
      newExpenseTagId,
      newExpenseTagIdError,
      newExpenseTagDescription,
      newExpenseTagDescriptionError,
      submitNewExpenseTag,
      editExpenseTagId,
      editExpenseTagDescription,
      editExpenseTagDescriptionError,
      editExpenseTagActive,
      submitEditExpenseTag,
    };
  },
  mounted() {
    requests.getExpenseTags(true).then((response) => {
      this.expenseTags = response.data;
    });
  },
  methods: {
    /* deleteExpenseType(expenseTypeId) {
      requests.deleteExpenseType(expenseTypeId).then((response) => {
        const indexInArray = this.expenseTypes.findIndex((t) => (t.id === response.data.id));
        this.expenseTypes.splice(indexInArray, 1);
        toast.success('Expense Type deleted', {timeout: 2000});
      });
    }, */
    editExpenseTag(expenseTagId, expenseTagDescription, expenseTagActive) {
      this.editExpenseTagId = expenseTagId;
      this.editExpenseTagDescription = expenseTagDescription;
      this.editExpenseTagActive = expenseTagActive;
    },
  },
};
</script>

<template>
  <Card title="Manage Expense Tags">
    <form @submit.prevent="submitEditExpenseTag">
      <div class="grid grid-cols-10 gap-2">
        <div class="col-span-2">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Expense Tag</span>
        </div>
        <div class="col-span-4">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Description</span>
        </div>
        <div class="col-span-2">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Active</span>
        </div>
        <div class="col-span-2">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Edit</span>
        </div>

        <template v-for="expenseTag in expenseTags" :key="expenseTag.id">
          <div class="col-span-2">
            <span class="text-slate-700 dark:text-slate-300">{{expenseTag.id}}</span>
          </div>
          <div v-if="editExpenseTagId == null || editExpenseTagId !== expenseTag.id" class="col-span-4">
            <span class="text-slate-700 dark:text-slate-300">{{expenseTag.description}}</span>
          </div>
          <div v-if="editExpenseTagId == null || editExpenseTagId !== expenseTag.id" class="col-span-2">
            <Checkbox
              name="editExpenseTagActive"
              disabled
              v-model="expenseTag.active">
            </Checkbox>
          </div>
          <div v-if="editExpenseTagId === expenseTag.id" class="col-span-4">
            <Textinput
                type="text"
                placeholder="New Description"
                name="editExpenseTagDescription"
                v-model="editExpenseTagDescription"
                :error="editExpenseTagDescriptionError"
            />
          </div>
          <div v-if="editExpenseTagId != null && editExpenseTagId === expenseTag.id" class="col-span-2">
            <Checkbox
              name="editExpenseTagActive"
              v-model="editExpenseTagActive">
            </Checkbox>
          </div>
          <div v-if="editExpenseTagId == null" class="col-span-2">
            <DashButton @click="editExpenseTag(expenseTag.id, expenseTag.description, expenseTag.active)" class="btn-sm mx-auto block-btn">Edit</DashButton>
          </div>
          <div v-if="editExpenseTagId != null && editExpenseTagId !== expenseTag.id" class="col-span-2"></div>
          <div v-if="editExpenseTagId != null && editExpenseTagId === expenseTag.id" class="col-span-2">
            <DashButton type="submit" class="btn-sm mx-auto block-btn">Submit</DashButton>
          </div>

        </template>
      </div>
    </form>
    <form @submit.prevent="submitNewExpenseTag">
      <div class="grid grid-cols-8 gap-2 mt-2">
        <div class="col-span-2">
          <Textinput
              type="text"
              placeholder="New Expense Tag"
              name="newExpenseTagId"
              v-model="newExpenseTagId"
              :error="newExpenseTagIdError"
          />
        </div>
        <div class="col-span-4">
          <Textinput
              type="text"
              placeholder="Description"
              name="newExpenseTypeDescription"
              v-model="newExpenseTagDescription"
              :error="newExpenseTagDescriptionError"
          />
        </div>
        <div class="col-span-2">
          <DashButton type="submit" @click="submitNewExpenseTag" class="btn-sm mx-auto block-btn">Add</DashButton>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
