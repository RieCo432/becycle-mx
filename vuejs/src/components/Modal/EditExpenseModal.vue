<script>
import requests from '@/requests';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Select from '@/components/Select/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import Button from '@/components/Button/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Modal from '@/components/Modal/Modal.vue';
import {ref} from 'vue';

const toast = useToast();

export default {
  name: 'editExpenseModal',
  components: {
    Modal,
    Checkbox,
    Button,
    Textinput,
    Textarea,
    Select,
    ErrorMessage,
  },
  setup(props, context) {
    const expenseId = ref('');

    const editExpenseSchemas = yup.object().shape({
      inOrOut: yup.string().oneOf(['in', 'out']),
      type: yup.string(),
      tagId: yup.string(),
      notes: yup.string(),
      amount: yup.number(),
      expenseDate: yup.date(),
      expenseUserId: yup.string(),
      transferred: yup.bool(),
      treasurerUserId: yup.string().nullable(),
      transferDate: yup.date().nullable(),
    });

    const {handleSubmit} = useForm({
      validationSchema: editExpenseSchemas,
      keepValuesOnUnmount: true,
    });

    const {value: inOrOut, errorMessage: inOrOutError, resetField: resetInOrOut} = useField('inOrOut');
    const {value: type, errorMessage: typeError, resetField: resetType} = useField('type');
    const {value: tagId, errorMessage: tagError, resetField: resetTag} = useField('tagId');
    const {value: notes, errorMessage: notesError, resetField: resetNotes} = useField('notes');
    const {value: amount, errorMessage: amountError, resetField: resetAmount} = useField('amount');
    const {value: expenseDate, errorMessage: expenseDateError, resetField: resetExpenseDate} = useField('expenseDate');
    const {value: expenseUserId, errorMessage: expenseUserIdError, resetField: resetExpenseUserId} = useField('expenseUserId');
    const {value: transferred, errorMessage: transferredError, resetField: resetTransferred} = useField('transferred');
    const {value: treasurerUserId, errorMessage: treasurerUserIdError, resetField: resetTreasurerUserId} = useField('treasurerUserId');
    const {value: transferDate, errorMessage: transferDateError, resetField: resetTransferDate} = useField('transferDate');

    const submitPatchExpense = handleSubmit(() => {
      requests.patchExpense(expenseId.value, (inOrOut.value === 'out' ? -1 : 1) * amount.value, type.value, tagId.value, notes.value,
        expenseDate.value, expenseUserId.value, transferred.value, treasurerUserId.value, transferDate.value)
        .then((response) => {
          toast.success('Expense Updated', {timeout: 2000});
          resetInOrOut();
          resetType();
          resetTag();
          resetNotes();
          resetAmount();
          resetExpenseDate();
          resetExpenseUserId();
          resetTransferred();
          resetTreasurerUserId();
          resetTransferDate();
          context.emit('expenseUpdated', response.data);
          props.closeModal();
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          props.closeModal();
        });
    });

    return {
      expenseId,
      inOrOut,
      inOrOutError,
      type,
      typeError,
      tagId,
      tagError,
      notes,
      notesError,
      amount,
      amountError,
      expenseDate,
      expenseDateError,
      expenseUserId,
      expenseUserIdError,
      transferred,
      transferredError,
      treasurerUserId,
      treasurerUserIdError,
      transferDate,
      transferDateError,
      submitPatchExpense,
    };
  },
  data() {
    return {
      expenseTypes: [],
      expenseTags: [],
      expenseUsers: [],
      treasurerUsers: [],
      inOrOutOptions: [
        {
          label: 'OUT of the bank account',
          value: 'out',
        },
        {
          label: 'INTO the bank account',
          value: 'in',
        },
      ],
    };
  },
  created() {
    requests.getExpenseTypes().then((response) => {
      this.expenseTypes = response.data.map((t) => (
        {
          label: `${t.id} --- ${t.description}`,
          value: t.id,
        }
      ));
    });
    requests.getExpenseTags().then((response) => {
      this.expenseTags = response.data.map((t) => (
        {
          label: `${t.id} --- ${t.description}`,
          value: t.id,
        }
      ));
    });
    requests.getUsers().then((response) => {
      this.expenseUsers = response.data.map((t) => (
        {
          label: t.username,
          value: t.id,
        }
      ));
      this.treasurerUsers = response.data.filter((user) => (user.treasurer)).map((t) => (
        {
          label: t.username,
          value: t.id,
        }
      ));
    });
  },
  props: {
    expense: {
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
        this.expenseId = this.expense.id;
        this.inOrOut = this.expense.amount > 0 ? 'in' : 'out';
        this.amount = Math.abs(this.expense.amount);
        this.type = this.expense.type;
        this.tagId = this.expense.tagId;
        this.notes = this.expense.notes;
        this.expenseDate = this.expense.expenseDate;
        this.expenseUserId = this.expense.expenseUser.id;
        this.transferred = this.expense.transferDate !== null;
        if (this.transferred) {
          this.transferDate = this.expense.transferDate;
          this.treasurerUserId = this.expense.treasurerUser.id;
        } else {
          this.transferDate = null;
          this.treasurerUserId = null;
        }
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
    <form @submit.prevent="submitPatchExpense">
      <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
        <div class="col-span-full">
          <h3 class="text-danger-500 dark:text-danger-600">BE CAREFUL! NO VALIDATION IS DONE ON THESE INPUTS</h3>
        </div>
        <div class="col-span-6">
          <Textinput
              label="Amount (&pound;)"
              type="text"
              placeholder="12.34"
              name="amount"
              v-model="amount"
              :error="amountError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="inOrOutOptions"
              label="Is Money going INTO or OUT OF the bank account?"
              v-model="inOrOut"
              name="inOrOut"
              :error="inOrOutError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="expenseTypes"
              label="Type of Expense"
              v-model="type"
              name="type"
              :error="typeError"
          />
        </div>
        <div class="col-span-6">
          <Select
              :options="expenseTags"
              label="Tag/Project"
              v-model="tagId"
              name="tagId"
              :error="tagError"
          />
        </div>
        <div class="col-span-6">
                        <Textarea
                            label="Notes"
                            type="text"
                            placeholder="anything noteworth"
                            name="notes"
                            v-model="notes"
                            :error="notesError"
                        />
        </div>
        <div class="col-span-6 content-center">
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
        <div class="col-span-6">
          <Select
              label="Expense User"
              name="expenseUserId"
              :options="expenseUsers"
              :error="expenseUserIdError"
              v-model="expenseUserId"
          ></Select>
        </div>
        <div class="col-span-6">
          <label class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">Is Transferred</label>
          <Checkbox
              v-model="transferred"
          ></Checkbox>
        </div>
        <div v-if="transferred" class="col-span-6">
          <Select
              label="Transferred By"
              name="treasurerUserId"
              :options="treasurerUsers"
              :error="treasurerUserIdError"
              v-model="treasurerUserId"
          ></Select>
        </div>
        <div v-if="transferred" class="col-span-6">
          <label class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">Transfer Date</label>
          <flat-pickr
              class="form-control m-auto"
              name="transferDate"
              id="d4"
              placeholder="dd-mm-yyyy"
              v-model="transferDate"
              :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
          >
          </flat-pickr>
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
