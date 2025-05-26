<script>
import Card from '@/components/Card/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import Switch from '@/components/Switch';
import {onBeforeMount} from 'vue';
const toast = useToast();

export default {
  name: 'EditAppointmentGeneralSettingsCard',
  components: {
    Switch,
    Button,
    TextInput,
    Card,
    VueSelect,
  },
  emits: ['openingDaysUpdated'],
  props: {
    openingDaysOptions: {
      type: Array,
      required: true,
    },
  },
  setup(props, context) {
    const appointmentGeneralSettingsSchema = yup.object().shape({
      openingDays: yup.array().of(yup.object({
        label: yup.string().oneOf(props.openingDaysOptions.map((option) => (option.label))),
        value: yup.number().oneOf(props.openingDaysOptions.map((option) => (option.value))),
      })).max(7),
      minBookAhead: yup.number().integer().min(0, 'Must be at least 0').max(yup.ref('maxBookAhead'), 'Must be less than Max Book Ahead'),
      maxBookAhead: yup.number().integer().min(yup.ref('minBookAhead'), 'Must be more than Min Book Ahead'),
      slotDuration: yup.number().integer().positive(),
      gradualAvailability: yup.bool(),
    });

    const {handleSubmit: handleAppointmentGeneralSettingsSubmit} = useForm({
      validationSchema: appointmentGeneralSettingsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: openingDays, errorMessage: openingDaysError, resetField: resetOpeningDaysField} = useField('openingDays');
    const {value: minBookAhead, errorMessage: minBookAheadError, resetField: resetMinBookAheadField} = useField('minBookAhead');
    const {value: maxBookAhead, errorMessage: maxBookAheadError, resetField: resetMaxBookAheadField} = useField('maxBookAhead');
    const {value: slotDuration, errorMessage: slotDurationError, resetField: resetSlotDurationField} = useField('slotDuration');
    const {value: gradualAvailability, resetField: resetGradualAvailabilityField} = useField('gradualAvailability');

    const setFields = (data) => {
      resetOpeningDaysField({value: props.openingDaysOptions.filter((day) => (data.openingDays.includes(day.value)))});
      resetMinBookAheadField({value: data.minBookAhead.toString()});
      resetMaxBookAheadField({value: data.maxBookAhead.toString()});
      resetSlotDurationField({value: data.slotDuration.toString()});
      resetGradualAvailabilityField({value: data.gradualAvailability});
    };

    const patchAppointmentGeneralSettings = handleAppointmentGeneralSettingsSubmit(() => {
      requests.patchAppointmentGeneralSettings({
        openingDays: openingDays.value.map((option) => (option.value)),
        minBookAhead: parseInt(minBookAhead.value),
        maxBookAhead: parseInt(maxBookAhead.value),
        slotDuration: parseInt(slotDuration.value),
        gradualAvailability: gradualAvailability.value,
      }).then((response) => {
        toast.success('Appointment General Settings updated', {timeout: 2000});
        setFields(response.data);
        context.emit('openingDaysUpdated', response.data.openingDays);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    onBeforeMount(() => {
      requests.getAppointmentGeneralSettings().then((response) => {
        setFields(response.data);
      });
    });

    return {
      openingDays,
      openingDaysError,
      resetOpeningDaysField,
      minBookAhead,
      minBookAheadError,
      resetMinBookAheadField,
      maxBookAhead,
      maxBookAheadError,
      resetMaxBookAheadField,
      slotDuration,
      slotDurationError,
      resetSlotDurationField,
      gradualAvailability,
      resetGradualAvailabilityField,
      patchAppointmentGeneralSettings,
    };
  },
};
</script>

<template>
  <Card title="Appointment General Settings">
    <div>
      <form @submit.prevent="patchAppointmentGeneralSettings">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <VueSelect
                label="Opening Days"
                name="openingDays"
                :options="openingDaysOptions"
                v-model="openingDays"
                :error="openingDaysError"
                multiple
            />
          </div>
          <div class="col-span-6">
            <TextInput
                label="Minimum Booking Ahead"
                type="text"
                placeholder="2"
                name="minBookAhead"
                v-model="minBookAhead"
                :error="minBookAheadError"
            />
          </div>
          <div class="col-span-6">
            <TextInput
                label="Maximum Booking Ahead"
                type="text"
                placeholder="60"
                name="maxBookAhead"
                v-model="maxBookAhead"
                :error="maxBookAheadError"
            />
          </div>
          <div class="col-span-6">
            <TextInput
                label="Slot Duration"
                type="text"
                placeholder="15"
                name="slotDuration"
                v-model="slotDuration"
                :error="slotDurationError"
            />
          </div>
          <div class="col-span-6">
            <label
              class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
              Gradual Availability
            </label>
            <Switch
              name="gradualAvailability"
              active-class="bg-primary-500"
              v-model="gradualAvailability"
            />
          </div>
          <div class="col-span-12">
            <Button type="submit" class="btn btn-dark block w-full text-center">
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
