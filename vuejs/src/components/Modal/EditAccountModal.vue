<script>
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import {ref, toRef} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import VueSelect from '@/components/Select/VueSelect.vue';

import {useToast} from 'vue-toastification';
import Modal from '@/components/Modal/Modal.vue';

const toast = useToast();

export default {
  name: 'EditAccountModal',
  components: {Modal, VueSelect, Button, TextInput},
  setup(props, context) {
    const existingAccounts = toRef(props, 'accounts');
    const users = ref([]);
    const groups = ref([]);

    requests.getUsers().then((response) => {
      response.data.forEach((u) => users.value.push(u));
    });
    requests.getUserGroups().then((response) => {
      response.data.forEach((g) => groups.value.push(g));
    });

    const availableUiFilters = ['deposit', 'expense', 'income', 'transfer', 'return'];
    const accountTypes = ['dividend', 'expense', 'asset', 'liability', 'equity', 'revenue'];

    const updateAccountSchema = yup.object().shape({
      name: yup
        .string()
        .required('Name is required')
        .lowercase()
        .notOneOf(existingAccounts.value.map((a) => a.name).filter((name) => name !== props.account.name), 'This name exists already!')
        .max(60, 'No more than 30 characters'),
      description: yup
        .string()
        .required('Description is required')
        .max(255, 'No more than 255 characters'),
      scheduledClosureDate: yup.date().nullable(),
      showInUis: yup.array().of(yup.object().shape({
        label: yup.string().oneOf(availableUiFilters),
        value: yup.string().oneOf(availableUiFilters),
      })),
    });


    const {handleSubmit: handleUpdateAccountSubmit, resetForm: resetUpdateAccountForm} = useForm({
      validationSchema: updateAccountSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: description, errorMessage: descriptionError} = useField('description');
    const {value: scheduledClosureDate, errorMessage: scheduledClosureDateError} = useField('scheduledClosureDate');
    const {value: showInUis, errorMessage: showInUisError} = useField('showInUis');

    const putUpdateAccount = handleUpdateAccountSubmit(() => {
      requests.putUpdateAccount(
        props.account.id,
        name.value.toLowerCase(),
        description.value.toLowerCase(),
        scheduledClosureDate.value,
        showInUis.value.map((f) => f.value.toLowerCase()))
        .then((response) => {
          toast.success('Account updated!', {timeout: 2000});
          context.emit('accountUpdated', response.data);
        }).finally(() => {
          resetUpdateAccountForm();
          props.closeModal();
        });
    });

    return {
      accountTypes,
      users,
      groups,
      availableUiFilters,
      name,
      nameError,
      description,
      descriptionError,
      scheduledClosureDate,
      scheduledClosureDateError,
      showInUis,
      showInUisError,
      putUpdateAccount,
    };
  },
  emits: ['accountUpdated'],
  props: {
    accounts: {
      type: Array,
      required: true,
    },
    account: {
      type: Object,
      required: true,
    },
    showModal: {
      type: Boolean,
    },
    closeModal: {
      type: Function,
    },
  },
  mounted() {
    this.name = this.account.name;
    this.description = this.account.description;
    this.scheduledClosureDate = this.account.scheduledClosureDate;
    this.showInUis = this.account.showInUis.map((f) => ({label: f, value: f}));
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Details">
    <div class="grid grid-cols-12">
      <div class="col-span-12">
        <form @submit.prevent="putUpdateAccount" class="space-y-4">
          <TextInput
              label="Name"
              type="text"
              placeholder="Deposit Liability Account"
              name="name"
              v-model="name"
              :error="nameError"
              classInput="h-[48px]"
          />
          <TextInput
              label="Description"
              type="text"
              placeholder="This is the main liability account for all deposits"
              name="description"
              v-model="description"
              :error="descriptionError"
              classInput="h-[48px]"
          />
          <div class="col-span-6 content-center">
            <label class="text-slate-700 dark:text-slate-300">Scheduled Closure Date</label>
            <flat-pickr
                class="form-control m-auto"
                name="scheduledClosureDate"
                id="d3"
                placeholder="dd-mm-yyyy"
                v-model="scheduledClosureDate"
                :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            >
            </flat-pickr>
            <ErrorMessage name="scheduledClosureDate" :error="scheduledClosureDateError" class="text-danger-500"/>
          </div>

          <div class="col-span-12" :style="`height: ${35 * availableUiFilters.length}px`">
            <VueSelect
                label="Show in UIs"
                name="showInUis"
                :options="availableUiFilters.map((i) => ({value: i, label: i}))"
                v-model="showInUis"
                :error="showInUisError"
                multiple
            />
          </div>

          <Button type="submit" class="btn btn-dark block w-full text-center">
            Submit
          </Button>
        </form>
      </div>
    </div>
  </Modal>

</template>

<style scoped lang="scss">

</style>
