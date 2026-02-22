<script>
import requests from '@/requests';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Select from '@/components/Select/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Modal from '@/components/Modal/Modal.vue';
import {ref} from 'vue';

const toast = useToast();

export default {
  name: 'editExpenseClaimModal',
  components: {
    Modal,
    Button,
    Textarea,
    ErrorMessage,
  },
  setup(props, context) {
    const expenseClaimId = ref('');

    const editExpenseSchemas = yup.object().shape({
      notes: yup.string().required(),
      expenseDate: yup.date().required(),
    });

    const {handleSubmit: handleSubmitEditExpense} = useForm({
      validationSchema: editExpenseSchemas,
      keepValuesOnUnmount: true,
    });
    
    const {value: notes, errorMessage: notesError, resetField: resetNotes} = useField('notes');
    const {value: expenseDate, errorMessage: expenseDateError, resetField: resetExpenseDate} = useField('expenseDate');

    const submitPatchExpense = handleSubmitEditExpense(() => {
      requests.putExpenseClaim(expenseClaimId.value, notes.value, expenseDate.value)
        .then((response) => {
          toast.success('Expense Claim Updated', {timeout: 2000});
          resetNotes();
          resetExpenseDate();
          context.emit('expenseClaimUpdated', response.data);
          props.closeModal();
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          props.closeModal();
        });
    });

    return {
      expenseClaimId,
      notes,
      notesError,
      expenseDate,
      expenseDateError,
      submitUpdateExpenseClaim: submitPatchExpense,
    };
  },
  props: {
    expenseClaim: {
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
  emits: ['expenseUpdated'],
  methods: {
    setFields() {
      {
        this.expenseClaimId = this.expenseClaim.id;
        this.notes = this.expenseClaim.notes;
        this.expenseDate = this.expenseClaim.expenseDate;
      }
    },
  },
  watch: {
    showModal(newValue) {
      if (newValue) {
        this.setFields();
      }
    },
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Expense">
    <form @submit.prevent="submitUpdateExpenseClaim">
      <div class="grid grid-cols-12 gap-5">
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
        <div class="col-span-12 content-center">
          <label class="text-slate-700 dark:text-slate-300">Date of Expense</label>
          <flat-pickr
              class="form-control m-auto"
              name="expenseDate"
              id="d3"
              placeholder="dd-mm-yyyy"
              v-model="expenseDate"
              :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
          >
          </flat-pickr>
          <ErrorMessage name="expenseDate" :error="expenseDateError" class="text-danger-500"/>
        </div>
        <div class="col-span-full">
          <Button type="submit" class="btn block w-full text-center">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
