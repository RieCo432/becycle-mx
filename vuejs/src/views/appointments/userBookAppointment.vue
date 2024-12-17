<script>
import {computed, ref} from 'vue';
import requests from '@/requests';
import Textinput from '@/components/Textinput/index.vue';
import Button from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import {useRouter} from 'vue-router';
import AppointmentTypeCardSkeleton from '@/components/Skeleton/AppointmentTypeCardSkeleton.vue';
import AppointmentDateCardSkeleton from '@/components/Skeleton/AppointmentDateCardSkeleton.vue';
import Icon from '@/components/Icon';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {debounce} from 'lodash-es';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';

export default {
  name: 'bookAppointment',
  components: {
    ComboboxTextInput,
    DashButton,
    Card,
    Button,
    Textinput,
    AppointmentTypeCardSkeleton,
    AppointmentDateCardSkeleton,
    Icon,
  },
  setup() {
    const steps = [
      {
        id: 1,
        title: 'Client Details',
      },
      {
        id: 2,
        title: 'Type',
      },
      {
        id: 3,
        title: 'Date and Time',
      },
      {
        id: 4,
        title: 'Notes',
      },
    ];

    const toast = useToast();
    const router = useRouter();

    const clientId = ref('');
    const stepNumber = ref(0);
    const appointmentType = ref('');
    const availableSlots = ref(null);
    const appointmentDatetime = ref(new Date());
    const appointmentNotes = ref('');

    const clientSchema = yup.object().shape({
      firstName: yup.string().required('First name is required'),
      lastName: yup.string().required('Last name is required'),
      emailAddress: yup
        .string()
        .email('Email is not valid')
        .required('Email is required'),
      confirmEmailAddress: yup
        .string()
        .email('Email is not valid')
        .required('Confirm Email is required')
        .oneOf([yup.ref('emailAddress')], 'Email Addresses must match'),
    });


    const currentSchema = computed(() => {
      switch (stepNumber.value) {
      case 0:
        return clientSchema;
      default:
        return null;
      }
    });

    useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: emailAddress, errorMessage: emailAddressError} = useField('emailAddress');
    const {value: confirmEmailAddress, errorMessage: confirmEmailAddressError} = useField('confirmEmailAddress');
    const {value: firstName, errorMessage: firstNameError} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError} = useField('lastName');

    const submit = () => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        requests.postAppointment(clientId.value, appointmentType.value, appointmentDatetime.value.toISOString(),
          appointmentNotes.value, true).then((response) => {
          toast.success('Appointment created.', {timeout: 2000});
          router.push(`/clients/${clientId.value}`);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          requests.getAvailableAppointmentSlots(appointmentType.value, true).then((response) => {
            availableSlots.value = response.data;
          });
          stepNumber.value--;
        });
      } else {
        if (stepNumber.value === 0) {
          // Client details processing
          requests.getClientByEmail(emailAddress.value).then((response) => {
            clientId.value = response.data[0]['id'];
            stepNumber.value++;
          }).catch((error) => {
            if (error.response.status === 404) {
              requests.postNewClient({
                firstName: firstName.value,
                lastName: lastName.value,
                emailAddress: emailAddress.value,
              }).then((response) => {
                toast.success('New Client Created!', {timeout: 1000});
                clientId.value = response.data['id'];
                stepNumber.value++;
              });
            }
          });
        } else if (stepNumber.value === 1) {
          stepNumber.value++;
          availableSlots.value = null;
          requests.getAvailableAppointmentSlots(appointmentType.value, true).then((response) => {
            availableSlots.value = response.data;
          });
        } else if (stepNumber.value === 2) {
          stepNumber.value++;
        }
      }
    };

    const prev = () => {
      stepNumber.value--;
    };

    return {
      emailAddress,
      emailAddressError,
      confirmEmailAddress,
      confirmEmailAddressError,
      firstName,
      firstNameError,
      lastName,
      lastNameError,
      clientId,
      appointmentNotes,
      appointmentDatetime,
      appointmentType,

      availableSlots,

      submit,
      steps,
      stepNumber,
      prev,
    };
  },
  data() {
    return {
      emailTyped: '',
      clientSuggestions: [],
      appointmentTypes: null,
    };
  },
  created() {
    requests.getUserMe(); // if this returns 401 the user will get redirected to login page
    this.fetchClientSuggestions = debounce(this.fetchClientSuggestions, 500, {leading: true, trailing: true});
    requests.getAppointmentTypes().then((response) => {
      this.appointmentTypes = response.data;
    });
  },
  methods: {
    fetchClientSuggestions() {
      requests.findClient(
        this.firstName ? this.firstName.toLowerCase() : '',
        this.lastName ? this.lastName.toLowerCase() : '',
        this.emailAddress ? this.emailAddress.toLowerCase() :'')
        .then((response) => {
          this.clientSuggestions = response.data;
        });
    },
    selectClient(event, i) {
      const selectedClient = this.filtered_client_suggestions[i];
      this.clientId = selectedClient.id;
      this.emailAddress = selectedClient.emailAddress;
      this.confirmEmailAddress = selectedClient.emailAddress;
      this.firstName = selectedClient.firstName;
      this.lastName = selectedClient.lastName;
    },
  },
  computed: {
    filtered_client_suggestions() {
      return this.clientSuggestions.filter((client) => (
        (this.firstName && client.firstName.startsWith(this.firstName.toLowerCase())) ||
          (this.lastName && client.lastName.startsWith(this.lastName.toLowerCase())) ||
          (this.emailAddress && client.emailAddress.startsWith(this.emailAddress.toLowerCase()))
      ));
    },
    filteredClientSuggestionsLegible() {
      return this.filtered_client_suggestions.map((client) => (`${client.firstName} ${client.lastName} ${client.emailAddress}`));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Book Appointment">
        <div>
          <div class="flex z-[5] items-center relative justify-center md:mx-8">
            <div
                class="relative z-[1] items-center item flex flex-start flex-1 last:flex-none group"
                v-for="(item, i) in steps"
                :key="i"
            >
              <div
                  :class="`   ${
            stepNumber >= i
              ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500 ' +
                'dark:bg-slate-900 dark:ring-slate-900'
              : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 ' +
                'dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
          }`"
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex
                         flex-col items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
              >
                <span v-if="stepNumber <= i"> {{ i + 1 }}</span>
                <span v-else class="text-3xl">
            <Icon icon="bx:check-double" />
          </span>
              </div>

              <div
                  class="absolute top-1/2 h-[2px] w-full"
                  :class="
            stepNumber >= i
              ? 'bg-slate-900 dark:bg-slate-900'
              : 'bg-[#E0EAFF] dark:bg-slate-700'
          "
              ></div>
              <div
                  class="absolute top-full text-base md:leading-6 mt-3 transition duration-150 md:opacity-100
                         opacity-0 group-hover:opacity-100"
                  :class="
            stepNumber >= i
              ? ' text-slate-900 dark:text-slate-300'
              : 'text-slate-500 dark:text-slate-300 dark:text-opacity-40'
          "
              >
                <span class="w-max">{{ item.title }}</span>
              </div>
            </div>
          </div>

          <div
              class="content-box mt-14 border-t border-slate-100 dark:border-slate-700 -mx-6 px-6 pt-6"
          >
            <form @submit.prevent="submit">
              <div v-if="stepNumber === 0">
                <div class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-2 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Enter the Client's Information
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="emailAddress"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient">
                      <Textinput label="Email" type="email" placeholder="Type your email"
                                 name="emailAddress"
                                 v-model="emailAddress"
                                 :error="emailAddressError"
                                 @input="fetchClientSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <Textinput
                        label="Confirm Email"
                        type="email"
                        placeholder="Confirm your email"
                        name="confirmEmailAddress"
                        v-model="confirmEmailAddress"
                        :error="confirmEmailAddressError"
                    />
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="firstName"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient">
                      <Textinput
                          label="First name"
                          type="text"
                          placeholder="First name"
                          name="firstname"
                          v-model="firstName"
                          :error="firstNameError"
                          @input="fetchClientSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>

                  <div class="col-span-1">
                    <ComboboxTextInput
                        :field-model-value="lastName"
                        :suggestions="filteredClientSuggestionsLegible"
                        :selected-callback="selectClient">
                      <Textinput
                          label="Last name"
                          type="text"
                          placeholder="Last name"
                          name="lastname"
                          v-model="lastName"
                          :error="lastNameError"
                          @input="fetchClientSuggestions"
                      />
                    </ComboboxTextInput>
                  </div>
                </div>
              </div>
              <div v-if="stepNumber === 1">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Select Appointment Type
                    </h4>
                  </div>

                  <template v-if="appointmentTypes == null">
                    <div class="col-span-1 bg-slate" v-for="i in 6" :key="i">
                      <AppointmentTypeCardSkeleton/>
                    </div>
                  </template>

                  <div class="col-span-1 bg-slate" v-for="(type, i) in appointmentTypes" :key="i">
                    <Card :title="type.title" class-name="bg-slate-300 dark:bg-slate-500 border border-slate-300 h-full">
                      <div class="flex flex-col h-full">
                        <div class="flex-1">
                          <p class="text-slate-600 dark:text-slate-300">{{type.description}}</p>
                        </div>
                        <DashButton class="mt-5" @click="() => {appointmentType = type.id}">
                          Select
                        </DashButton>
                      </div>
                    </Card>
                  </div>

                </div>
              </div>

              <div v-if="stepNumber === 2">
                <div class="grid lg:grid-cols-2 grid-cols-1 gap-5">
                  <div class="col-span-full">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Select Date and Time
                    </h4>
                  </div>

                  <!-- TODO: This probably needs a different interface-->

                  <template v-if="availableSlots == null">
                    <div class="col-span-1 bg-slate" v-for="i in 10" :key="i">
                      <AppointmentDateCardSkeleton/>
                    </div>
                  </template>


                  <div class="col-span-1 bg-slate" v-for="(slots, date) in availableSlots" :key="date">
                    <Card :title="new Date(date).toLocaleDateString(undefined, {weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    })" class-name="bg-slate-300 dark:bg-slate-500 border border-slate-300 h-full">
                      <div class="grid xl:grid-cols-6 sm:grid-cols-5 grid-cols-4 gap-3">
                        <div v-for="(slot, j) in slots" :key="j">
                          <DashButton :class="`w-full ${slot.available ? '' : 'bg-warning-500'}`"
                                      @click="() => {appointmentDatetime = (new Date(Date.parse(`${date}T${slot.time}+00:00`)))}">
                            {{ (new Date(Date.parse(`${date}T${slot.time}+00:00`)))
                              .toLocaleTimeString(undefined, { timeZone: 'UTC', hour: "2-digit", minute: "2-digit", hour12: false, }) }}
                          </DashButton>
                        </div>

                      </div>
                    </Card>
                  </div>

                </div>
              </div>
              <div v-if="stepNumber === 3">
                <div class="grid lg:grid-cols-2 grid-cols-1 gap-5">
                  <div class="col-span-full">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Finalise Appointment
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <h5 class="text-base text-slate-800 dark:text-slate-300 mb-3">Please check all the details!</h5>
                    <table class="w-full text-base text-slate-800 dark:text-slate-300 border border-collapse border-slate-500 bg-slate-700">
                      <thead>
                      <th colspan="2" class="border border-slate-500">Appointment Details</th>
                      </thead>
                      <tr>
                        <td class="border border-slate-500">Appointment Type</td>
                        <td class="border border-slate-500">{{appointmentTypes.find((type) => type.id === appointmentType).title}}</td>
                      </tr>
                      <tr>
                        <td class="border border-slate-500">Date and Time</td>
                        <td class="border border-slate-500">
                            {{appointmentDatetime.toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long',
                            year: 'numeric', hour: "2-digit", minute: "2-digit", hour12: false, timeZone: 'UTC'})}}
                        </td>
                      </tr>
                    </table>
                  </div>
                  <div class="col-span-1">

                    <Textinput
                        label="Notes"
                        type="text"
                        placeholder="Any import things to note?"
                        name="appointmentNotes"
                        v-model="appointmentNotes"/>
                  </div>
                </div>
              </div>

              <div
                  class="mt-10"
                  :class="stepNumber > 0 ? 'flex justify-between' : ' text-right'"
              >
                <Button
                    @click.prevent="prev()"
                    text="prev"
                    btnClass="btn-dark"
                    v-if="this.stepNumber !== 0"
                />
                <Button
                    v-if="(stepNumber !== 1) && (stepNumber !== 2)"
                    :text="stepNumber !== this.steps.length - 1 ? 'next' : 'submit'"
                    btnClass="btn-dark"
                />
              </div>
            </form>
          </div>
        </div>

      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
