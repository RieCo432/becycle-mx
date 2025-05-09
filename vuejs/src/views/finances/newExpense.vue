<script>
import requests from '@/requests';
import {useDropzone} from 'vue3-dropzone';
import Card from '@/components/Card/index.vue';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Select from '@/components/Select/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';

const toast = useToast();

export default {
  name: 'newExpense',
  components: {
    Button,
    TextInput,
    Textarea,
    Select,
    Card,
    ErrorMessage,
  },
  setup() {
    function onDrop(acceptFiles) {
      files.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        }),
      );
    }

    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: false});

    const newExpenseSchemas = yup.object().shape({
      inOrOut: yup.string().required().oneOf(['in', 'out']),
      type: yup.string().required(),
      tagId: yup.string().required(),
      notes: yup.string().required(),
      amount: yup.number().required(),
      expenseDate: yup.date().nullable(),
      file: yup.array().length(1),
    });

    const {handleSubmit, handleReset: resetExpenseForm} = useForm({
      validationSchema: newExpenseSchemas,
      keepValuesOnUnmount: true,
    });

    const {value: inOrOut, errorMessage: inOrOutError} = useField('inOrOut');
    const {value: type, errorMessage: typeError} = useField('type');
    const {value: tagId, errorMessage: tagError} = useField('tagId');
    const {value: notes, errorMessage: notesError} = useField('notes');
    const {value: amount, errorMessage: amountError} = useField('amount');
    const {value: expenseDate, errorMessage: expenseDateError, setErrors: setExpenseDateErrors} = useField('expenseDate');
    const {value: files, errorMessage: fileError} = useField('file', undefined, {initialValue: []});


    const submitNewExpense = handleSubmit(() => {
      if (!expenseDate.value || !expenseDate.value.length) {
        setExpenseDateErrors('This field is required');
        return;
      }
      requests.postNewExpense((inOrOut.value === 'out' ? -1 : 1) * amount.value,
        type.value, tagId.value, notes.value, expenseDate.value, files.value[0])
        .then(() => {
          toast.success('Expense Submitted', {timeout: 2000});
          resetExpenseForm();
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
        });
    });

    return {
      getRootProps,
      getInputProps,
      ...rest,
      files,
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
      fileError,
      submitNewExpense,
    };
  },
  data() {
    return {
      expenseTypes: [],
      expenseTags: [],
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
  },

};
</script>

<template>
  <div class="grid grid-cols-1">
    <div class="col-span-full">
      <Card title="Submit New Expense">
        <form @submit.prevent="submitNewExpense">
          <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
            <div class="col-span-6">
              <TextInput
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
              <div :class="(expenseDateError ? 'border border-solid border-danger-500 rounded ' : '')">
                <flat-pickr
                    class="form-control m-auto"
                    name="expenseDate"
                    v-model="expenseDate"
                    :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
                >
                </flat-pickr>
              </div>
              <ErrorMessage name="expenseDate" :error="expenseDateError" class="text-danger-500"/>
            </div>
            <div class="col-span-full">
              <div @click="files = []">
                <div
                    v-bind="getRootProps()"
                    :class="'w-full text-center border rounded py-[52px] flex flex-col justify-center items-center '
                    + (files.length === 0 ? 'cursor-pointer' : ' pointer-events-none') + ' '
                    + (fileError ? 'border-danger-500 border-solid' : 'border-secondary-500 border-dashed')
                    "
                >
                  <div v-if="files.length === 0" class="w-full">
                    <input v-bind="getInputProps()" class="hidden" />
                    <img src="@/assets/images/svg/upload.svg" alt="" class="mx-auto mb-4" />
                    <p
                        v-if="isDragActive"
                        class="text-sm text-slate-500 dark:text-slate-300 font-light"
                    >
                      Drop the files here ...
                    </p>
                    <p v-else class="text-sm text-slate-500 dark:text-slate-300 font-light">
                      Drop files here or click to upload.
                    </p>
                  </div>
                  <div class="flex space-x-4">
                    <img
                        v-if="files.length === 1"
                        :src="files[0].preview"
                        class="object-contain block rounded-md"
                        alt="Rceipt photo"
                    />
                  </div>
                </div>
              </div>
              <ErrorMessage name="file" :error="fileError" class="text-danger-500"/>
            </div>
            <div class="col-span-full">
              <Button type="submit" class="btn block w-full text-center">
                Submit
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
