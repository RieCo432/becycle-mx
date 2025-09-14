<script>
import {ref} from 'vue';
import requests from '@/requests';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import {useRouter} from 'vue-router';
import AppointmentTypeCardSkeleton from '@/components/Skeleton/AppointmentTypeCardSkeleton.vue';
import AppointmentDateCardSkeleton from '@/components/Skeleton/AppointmentDateCardSkeleton.vue';
import Icon from '@/components/Icon';

export default {
  name: 'bookAppointment',
  components: {
    DashButton,
    Card,
    Button,
    TextInput,
    AppointmentTypeCardSkeleton,
    AppointmentDateCardSkeleton,
    Icon,
  },
  setup() {
    const steps = [
      {
        id: 1,
        title: 'Type',
      },
      {
        id: 2,
        title: 'Date and Time',
      },
      {
        id: 3,
        title: 'Notes',
      },
    ];

    const toast = useToast();
    const router = useRouter();

    const stepNumber = ref(0);
    const appointmentType = ref('');
    const availableSlots = ref(null);
    const appointmentDatetime = ref(new Date());
    const appointmentNotes = ref('');


    const submit = () => {
      // next step until last step . if last step then submit form
      if (stepNumber.value === steps.length - 1) {
        // handle submit
        requests.postAppointmentRequest(appointmentType.value, appointmentDatetime.value.toISOString(),
          appointmentNotes.value).then(() => {
          toast.success('Appointment Request submitted! Kindly wait for us to accept or deny your request.', {timeout: 2000});
          router.push('/clients/me');
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          requests.getAvailableAppointmentSlots(appointmentType.value).then((response) => {
            availableSlots.value = response.data;
          });
          stepNumber.value = 1;
        });
      } else {
        if (stepNumber.value === 0) {
          stepNumber.value = 1;
          availableSlots.value = null;
          requests.getAvailableAppointmentSlots(appointmentType.value).then((response) => {
            availableSlots.value = response.data;
          });
        } else if (stepNumber.value === 1) {
          // handle return accepting user
          stepNumber.value = 2;
        }
      }
    };

    const prev = () => {
      stepNumber.value--;
    };

    return {
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
      appointmentTypes: null,
    };
  },
  created() {
    requests.getClientMe(); // if this returns 401 the client will get redirected to login page
    requests.getAppointmentTypes().then((response) => {
      this.appointmentTypes = response.data;
    });
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
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col
                         items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
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

              <div v-if="stepNumber === 1">
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

                  <template v-if="Object.keys(availableSlots).length > 0">
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
                  </template>

                  <template v-else>
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Unfortunately, there are currently no available slots for this appointment type due to high demand.
                      More slots will be added in a few days. Please try again in a few days.
                    </h4>
                  </template>

                </div>
              </div>
              <div v-if="stepNumber === 2">
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
                      <tr class="border border-slate-500">Appointment Details</tr>
                      </thead>
                      <tbody>
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
                      </tbody>
                    </table>
                  </div>
                  <div class="col-span-1">

                    <TextInput
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
                    v-if="stepNumber === this.steps.length - 1"
                    text="submit"
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
