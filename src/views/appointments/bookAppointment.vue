<script>
import {ref} from 'vue';
import requests from '@/requests';
import Textinput from '@/components/Textinput/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Select from '@/components/Select/index.vue';
import Button from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import {useRouter} from 'vue-router';
import AppointmentTypeCardSkeleton from '@/components/Skeleton/AppointmentTypeCardSkeleton.vue';

export default {
  name: 'bookAppointment',
  components: {
    DashButton,
    Card,
    Button,
    Select,
    Checkbox,
    Textinput,
    AppointmentTypeCardSkeleton,
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
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        requests.postAppointmentRequest(appointmentType.value, appointmentDatetime.value.toISOString(), appointmentNotes.value).then((response) => {
          toast.success('Appointment Request submitted! Kindly wait for us to accept or deny your request.', {timeout: 2000});
          router.push('/clients/me');
        });
      } else {
        if (stepNumber.value === 0) {
          stepNumber.value++;
          requests.getAvailableAppointmentSlots(appointmentType.value).then((response) => {
            availableSlots.value = response.data;
          });
        } else if (stepNumber.value === 1) {
          // handle return accepting user
          stepNumber.value++;
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
              ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500 dark:bg-slate-900 dark:ring-slate-900'
              : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
          }`"
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
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
                  class="absolute top-full text-base md:leading-6 mt-3 transition duration-150 md:opacity-100 opacity-0 group-hover:opacity-100"
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
                    <Card :title="type.title" class-name="dark:bg-slate-600">
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
                <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Select Date and Time
                    </h4>
                  </div>

                  <!-- TODO: This needs loading indicator and probably a different interface-->

                  <div class="col-span-1 bg-slate" v-for="(times, date) in availableSlots" :key="date">
                    <Card :title="date" class-name="dark:bg-slate-600">
                      <div class="grid grid-cols-4">
                        <div v-for="(time, j) in times" :key="j">
                          <DashButton class="mt-3" @click="() => {appointmentDatetime = new Date(Date.parse(`${date}T${time}+00:00`))}">
                            {{ time }}
                          </DashButton>
                        </div>

                      </div>
                    </Card>
                  </div>

                </div>
              </div>
              <div v-if="stepNumber === 2">
                <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
                  <div class="lg:col-span-3 md:col-span-2 col-span-1">
                    <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                      Notes
                    </h4>
                  </div>
                  <div class="col-span-1">
                    <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Please check all the details!</h5>
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