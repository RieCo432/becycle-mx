<script>
import Card from '@/components/Card/index.vue';
import Select from '@/components/Select/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import Switch from '@/components/Switch';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {onBeforeMount, ref} from 'vue';
const toast = useToast();

export default {
  name: 'UpdateLlmSettingsCard',
  components: {
    Switch,
    Button,
    Textarea,
    TextInput,
    Select,
    Card,
  },
  setup() {
    const llmSettingsSchema = yup.object().shape({
      model: yup.string().max(128, 'Model name is too long'),
      systemPrompt: yup.string().nullable(),
      classificationPrompt: yup.string().nullable(),
      customerFreeForm: yup.bool(),
      debounceWindowSeconds: yup.number().integer().min(1, 'Must be at least 1'),
      debounceBatchCap: yup.number().integer().min(1, 'Must be at least 1'),
    });

    const {handleSubmit: handleLlmSettingsSubmit} = useForm({
      validationSchema: llmSettingsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: model, errorMessage: modelError, resetField: resetModelField} = useField('model');
    const {value: systemPrompt, errorMessage: systemPromptError, resetField: resetSystemPromptField} = useField('systemPrompt');
    const {
      value: classificationPrompt,
      errorMessage: classificationPromptError,
      resetField: resetClassificationPromptField,
    } = useField('classificationPrompt');
    const {value: customerFreeForm, resetField: resetCustomerFreeFormField} = useField('customerFreeForm');
    const {
      value: debounceWindowSeconds,
      errorMessage: debounceWindowSecondsError,
      resetField: resetDebounceWindowSecondsField,
    } = useField('debounceWindowSeconds');
    const {
      value: debounceBatchCap,
      errorMessage: debounceBatchCapError,
      resetField: resetDebounceBatchCapField,
    } = useField('debounceBatchCap');

    const modelOptions = ref([
      {
        value: '',
        label: 'No model — assistant disabled',
      },
    ]);

    const setFields = (data) => {
      resetModelField({value: data.model ?? ''});
      resetSystemPromptField({value: data.systemPrompt ?? ''});
      resetClassificationPromptField({value: data.classificationPrompt ?? ''});
      resetCustomerFreeFormField({value: data.customerFreeForm});
      resetDebounceWindowSecondsField({value: data.debounceWindowSeconds.toString()});
      resetDebounceBatchCapField({value: data.debounceBatchCap.toString()});
    };

    const putLlmSettings = handleLlmSettingsSubmit(() => {
      requests.putLlmSettings({
        model: model.value,
        systemPrompt: systemPrompt.value,
        classificationPrompt: classificationPrompt.value,
        customerFreeForm: customerFreeForm.value,
        debounceWindowSeconds: parseInt(debounceWindowSeconds.value),
        debounceBatchCap: parseInt(debounceBatchCap.value),
      }).then((response) => {
        toast.success('LLM Settings updated', {timeout: 2000});
        setFields(response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    onBeforeMount(() => {
      requests.getLlmSettings().then((response) => {
        setFields(response.data);
      });
      requests.getLlmModels().then((response) => {
        modelOptions.value = [
          ...modelOptions.value,
          ...response.data.map((modelName) => ({
            value: modelName,
            label: modelName,
          })),
        ];
      });
    });

    return {
      model,
      modelError,
      systemPrompt,
      systemPromptError,
      classificationPrompt,
      classificationPromptError,
      customerFreeForm,
      debounceWindowSeconds,
      debounceWindowSecondsError,
      debounceBatchCap,
      debounceBatchCapError,
      modelOptions,
      putLlmSettings,
    };
  },
};
</script>

<template>
  <Card title="LLM Settings">
    <div>
      <form @submit.prevent="putLlmSettings">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <Select
                label="Model"
                name="model"
                :options="modelOptions"
                v-model="model"
                :error="modelError"
                :disable-placeholder="true"
                :disabled="!$can('putLlmSettings')"
            />
          </div>
          <div class="col-span-12">
            <Textarea
                label="System Prompt"
                name="systemPrompt"
                v-model="systemPrompt"
                :error="systemPromptError"
                :rows="4"
                :disabled="!$can('putLlmSettings')"
            />
          </div>
          <div class="col-span-12">
            <Textarea
                label="Classification Prompt"
                name="classificationPrompt"
                v-model="classificationPrompt"
                :error="classificationPromptError"
                :rows="4"
                :disabled="!$can('putLlmSettings')"
            />
          </div>
          <div class="col-span-6">
            <TextInput
              label="Debounce Window (seconds)"
              type="number"
              name="debounceWindowSeconds"
              v-model="debounceWindowSeconds"
              :error="debounceWindowSecondsError"
              placeholder="30"
              :disabled="!$can('putLlmSettings')"
            />
          </div>
          <div class="col-span-6">
            <TextInput
              label="Debounce Batch Cap (messages)"
              type="number"
              name="debounceBatchCap"
              v-model="debounceBatchCap"
              :error="debounceBatchCapError"
              placeholder="6"
              :disabled="!$can('putLlmSettings')"
            />
          <div class="col-span-full">
            <label
              class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
              Customer Free-Form
            </label>
            <Switch
              name="customerFreeForm"
              active-class="bg-primary-500"
              v-model="customerFreeForm"
              :disabled="!$can('putLlmSettings')"
            />
          </div>
          </div>
          <div class="col-span-12">
            <Button
              :disabled="!$can('putLlmSettings')"
              type="submit"
              class="btn btn-dark block w-full text-center">
              Submit
            </Button>
          </div>
        </div>
      </form>
    </div>

  </Card>
</template>

<style scoped lang="scss">

</style>
