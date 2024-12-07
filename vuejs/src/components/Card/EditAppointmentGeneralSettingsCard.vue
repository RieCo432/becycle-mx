<script>
import Card from '@/components/Card/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';
import Select from '@/components/Select';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Textinput from '@/components/Textinput/index.vue';
import Button from '@/components/Button/index.vue';
import {ref} from 'vue';
const toast = useToast();

export default {
  name: 'EditAppointmentGeneralSettingsCard',
  components: {
    Button,
    Textinput,
    Card,
    VueSelect,
    Select,
  },
  setup() {
    const openingDaysOptions = ref([
      {
        label: 'Monday',
        value: 0,
      },
      {
        label: 'Tuesday',
        value: 1,
      },
      {
        label: 'Wednesday',
        value: 2,
      },
      {
        label: 'Thursday',
        value: 3,
      },
      {
        label: 'Friday',
        value: 4,
      },
      {
        label: 'Saturday',
        value: 5,
      },
      {
        label: 'Sunday',
        value: 6,
      },
    ]);
    const appointmentGeneralSettingsSchema = yup.object().shape({
      openingDays: yup.array().of(yup.object({
        label: yup.string().oneOf(openingDaysOptions.value.map((option) => (option.label))),
        value: yup.number().oneOf(openingDaysOptions.value.map((option) => (option.value))),
      })).max(7),
      minBookAhead: yup.number().integer().min(0, 'Must be at least 0').max(yup.ref('maxBookAhead'), 'Must be less than Max Book Ahead'),
      maxBookAhead: yup.number().integer().min(yup.ref('minBookAhead'), 'Must be more than Min Book Ahead'),
      slotDuration: yup.number().integer().positive(),
    });

    const {handleSubmit: handleAppointmentGeneralSettingsSubmit} = useForm({
      validationSchema: appointmentGeneralSettingsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: openingDays, errorMessage: openingDaysError, resetField: resetOpeningDaysField} = useField('openingDays');
    const {value: minBookAhead, errorMessage: minBookAheadError, resetField: resetMinBookAheadField} = useField('minBookAhead');
    const {value: maxBookAhead, errorMessage: maxBookAheadError, resetField: resetMaxBookAheadField} = useField('maxBookAhead');
    const {value: slotDuration, errorMessage: slotDurationError, resetField: resetSlotDurationField} = useField('slotDuration');

    const setFields = (data) => {
      resetOpeningDaysField({value: openingDaysOptions.value.filter((day) => (data.openingDays.includes(day.value)))});
      resetMinBookAheadField({value: data.minBookAhead.toString()});
      resetMaxBookAheadField({value: data.maxBookAhead.toString()});
      resetSlotDurationField({value: data.slotDuration.toString()});
    };

    requests.getAppointmentGeneralSettings().then((response) => {
      setFields(response.data);
    });

    const patchAppointmentGeneralSettings = handleAppointmentGeneralSettingsSubmit(() => {
      console.log('Update');
      requests.patchAppointmentGeneralSettings({
        openingDays: openingDays.value.map((option) => (option.value)),
        minBookAhead: parseInt(minBookAhead.value),
        maxBookAhead: parseInt(maxBookAhead.value),
        slotDuration: parseInt(slotDuration.value),
      }).then((response) => {
        toast.success('Appointment General Settings updated', {timeout: 2000});
        setFields(response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      openingDaysOptions,
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
            <Textinput
                label="Minimum Booking Ahead"
                type="text"
                placeholder="2"
                name="minBookAhead"
                v-model="minBookAhead"
                :error="minBookAheadError"
            />
          </div>
          <div class="col-span-6">
            <Textinput
                label="Maximum Booking Ahead"
                type="text"
                placeholder="60"
                name="maxBookAhead"
                v-model="maxBookAhead"
                :error="maxBookAheadError"
            />
          </div>
          <div class="col-span-12">
            <Textinput
                label="Slot Duration"
                type="text"
                placeholder="15"
                name="slotDuration"
                v-model="slotDuration"
                :error="slotDurationError"
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
