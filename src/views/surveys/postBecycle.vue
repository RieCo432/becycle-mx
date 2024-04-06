<script>
import Textinput from '@/components/Textinput/index.vue';
import DashButton from '@/components/Button/index.vue';
import Select from '@/components/Select/index.vue';
import Card from '@/components/Card/index.vue';
import Checkbox from '@/components/Checkbox';
import {computed, ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Icon from '@/components/Icon';
import {useRouter} from 'vue-router';
import {useToast} from 'vue-toastification';

export default {
  name: 'postBecycle',
  components: {Checkbox, Card, DashButton, Textinput, Select, Icon},
  setup() {
    const router = useRouter();
    const toast = useToast();
    const steps = [
      {
        id: 1,
        title: 'Satisfaction',
      },
      {
        id: 2,
        title: 'Returning your bike',
      },
      {
        id: 3,
        title: 'Your Journey',
      },
      {
        id: 4,
        title: 'Suggestions',
      },
    ];

    const stepNumber = ref(0);

    const satisfactionSchema = yup.object().shape({
      serviceSatisfaction: yup.number().integer().min(0).max(5).required(),
    });

    const reasonSchema = yup.object().shape({
      reasonStoppedCycling: yup.boolean(),
      reasonLeavingAberdeen: yup.boolean(),
    });

    const issueAlternativeSchema = yup.object().shape({
      issueSafety: yup.boolean(),
      issueMoney: yup.boolean(),
      issueTime: yup.boolean(),
      issueSweating: yup.boolean(),
      issueComfort: yup.boolean(),
      issueDistance: yup.boolean(),
      issueOther: yup.string(),

      alternativeAnotherBecycle: yup.boolean(),
      alternativeOwnBike: yup.boolean(),
      alternativeShareFriendsFamily: yup.boolean(),
      alternativeOtherRental: yup.boolean(),
    });

    const improvementSchema = yup.object().shape({
      improvementNone: yup.boolean(),
      improvementCyclingPaths: yup.boolean(),
      improvementLights: yup.boolean(),
      improvementSurface: yup.boolean(),
      improvementCleaner: yup.boolean(),
      improvementOther: yup.string(),
    });

    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return satisfactionSchema;
        case 1:
          return reasonSchema;
        case 2:
          return issueAlternativeSchema;
        case 3:
          return improvementSchema;
        default:
          return satisfactionSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: serviceSatisfaction, errorMessage: serviceSatisfactionError} = useField('serviceSatisfaction');

    const {value: reasonStoppedCycling} = useField('reasonStoppedCycling');
    const {value: reasonLeavingAberdeen} = useField('reasonLeavingAberdeen');

    const {value: issueSafety} = useField('issueSafety');
    const {value: issueMoney} = useField('issueMoney');
    const {value: issueTime} = useField('issueTime');
    const {value: issueSweating} = useField('issueSweating');
    const {value: issueComfort} = useField('issueComfort');
    const {value: issueDistance} = useField('issueDistance');
    const {value: issueOther} = useField('issueOther');

    const {value: alternativeAnotherBecycle} = useField('alternativeAnotherBecycle');
    const {value: alternativeOwnBike} = useField('alternativeOwnBike');
    const {value: alternativeShareFriendsFamily} = useField('alternativeShareFriendsFamily');
    const {value: alternativeOtherRental} = useField('alternativeOtherRental');

    const {value: improvementNone} = useField('improvementNone');
    const {value: improvementCyclingPaths} = useField('improvementCyclingPaths');
    const {value: improvementLights} = useField('improvementLights');
    const {value: improvementSurface} = useField('improvementSurface');
    const {value: improvementCleaner} = useField('improvementCleaner');
    const {value: improvementOther} = useField('improvementOther');

    // set defaults
    reasonStoppedCycling.value = false;
    reasonLeavingAberdeen.value = false;

    issueSafety.value = false;
    issueMoney.value = false;
    issueTime.value = false;
    issueSweating.value = false;
    issueComfort.value = false;
    issueDistance.value = false;
    alternativeAnotherBecycle.value = false;
    alternativeOwnBike.value = false;
    alternativeShareFriendsFamily.value = false;
    alternativeOtherRental.value = false;

    improvementNone.value = false;
    improvementCyclingPaths.value = false;
    improvementLights.value = false;
    improvementSurface.value = false;
    improvementCleaner.value = false;

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        requests.postPostBecycleSurvey({
          serviceSatisfaction: serviceSatisfaction.value,
          reasonStoppedCycling: reasonStoppedCycling.value,
          reasonLeavingAberdeen: reasonLeavingAberdeen.value,
          issueSafety: issueSafety.value,
          issueMoney: issueMoney.value,
          issueTime: issueTime.value,
          issueSweating: issueSweating.value,
          issueComfort: issueComfort.value,
          issueDistance: issueDistance.value,
          issueOther: issueOther.value,
          alternativeAnotherBecycle: alternativeAnotherBecycle.value,
          alternativeOwnBike: alternativeOwnBike.value,
          alternativeShareFriendsFamily: alternativeShareFriendsFamily.value,
          alternativeOtherRental: alternativeOtherRental.value,
          improvementNone: improvementNone.value,
          improvementCyclingPaths: improvementCyclingPaths.value,
          improvementLights: improvementLights.value,
          improvementSurface: improvementSurface.value,
          improvementCleaner: improvementCleaner.value,
          improvementOther: improvementOther.value,
        }).then((response) => {
          toast.success('Your response has been recorded.', {timeout: 2000});
          router.push({path: '/home'});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      } else {
        stepNumber.value++;
      }
    });

    const prev = () => {
      stepNumber.value--;
    };

    return {
      steps,
      stepNumber,
      serviceSatisfaction,
      serviceSatisfactionError,
      reasonStoppedCycling,
      reasonLeavingAberdeen,
      issueSafety,
      issueMoney,
      issueTime,
      issueSweating,
      issueComfort,
      issueDistance,
      issueOther,
      improvementNone,
      improvementCyclingPaths,
      improvementLights,
      improvementSurface,
      improvementCleaner,
      improvementOther,
      alternativeAnotherBecycle,
      alternativeOwnBike,
      alternativeShareFriendsFamily,
      alternativeOtherRental,

      prev,
      submit,
    };
  },
};
</script>

<template>
  <div>
    <Card title="Pre-Becycle Survey">
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
        <form @submit.prevent="submit"  @keydown.enter="submit">
          <div v-if="stepNumber === 0">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  On a scale from 0 (do not agree at all) to 5 (agree fully), how much do you agree with the following statement?
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Textinput
                      label="Becycle has helped me get a bike, fix it, and learn about bike maintenance."
                      type="text"
                      placeholder="4"
                      name="serviceSatisfaction"
                      v-model="serviceSatisfaction"
                      :error="serviceSatisfactionError"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 1">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Why are you returning your bike? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I stopped cycling"
                      name="stoppedCycling"
                      v-model="reasonStoppedCycling"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I am leaving Aberdeen"
                      name="reasonLeavingAberdeen"
                      v-model="reasonLeavingAberdeen"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>

          <div v-if="stepNumber === 2 && reasonStoppedCycling">
            <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
              <div class="md:col-span-2 col-span-1">
                <h4  class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What are the reasons why you stopped cycling? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I feel unsafe on the road"
                      name="issueSafety"
                      v-model="issueSafety"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It was expensive"
                      name="issueMoney"
                      v-model="issueMoney"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It takes too long to get places"
                      name="issueTime"
                      v-model="issueTime"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I was arriving sweaty"
                      name="issueSweating"
                      v-model="issueSweating"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It was uncomfortable"
                      name="issueComfort"
                      v-model="issueComfort"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="The places I need to go to are too far"
                      name="issueDistance"
                      v-model="issueDistance"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Other"
                      type="text"
                      placeholder="Any other reasons?"
                      name="issueOther"
                      v-model="issueOther"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 2 && !reasonStoppedCycling">
            <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
              <div class="md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  You have returned your bike. How are you going to continue cycling?
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="Another Rental from Becycle, now or in the future."
                      name="alternativeAnotherBecycle"
                      v-model="alternativeAnotherBecycle"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I have bought or will buy my own bike."
                      name="alternativeOwnBike"
                      v-model="alternativeOwnBike"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I can use a bike from a friend or family."
                      name="alternativeShareFriendsFamily"
                      v-model="alternativeShareFriendsFamily"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I rent a bike from a different service, long or short-term."
                      name="alternativeOtherRental"
                      v-model="alternativeOtherRental"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 3">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 v-if="reasonStoppedCycling" class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Which one of these improvements would change your decision to stop cycling? Tick all that apply.
                </h4>
                <h4 v-else class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Which one of these improvements would you like to see? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="None"
                      name="improvementNone"
                      v-model="improvementNone"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="More cycle paths such as (segregated) cycling lanes"
                      name="improvementCyclingPaths"
                      v-model="improvementCyclingPaths"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Better lighting"
                      name="improvementLights"
                      v-model="improvementLights"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Better surfaces with fewer potholes."
                      name="improvementSurface"
                      v-model="improvementSurface"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Cleaner roads with less glass, sharp metal and slippery leaves."
                      name="improvementCleaner"
                      v-model="improvementCleaner"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Textinput
                      label="Any other improvements you would like to see?"
                      type="text"
                      placeholder="Anything?"
                      name="improvementOther"
                      v-model="improvementOther"
                  />
                </div>
              </div>
            </div>
          </div>
          <div
              class="mt-10"
              :class="stepNumber > 0 ? 'flex justify-between' : ' text-right'"
          >
            <DashButton
                @click.prevent="prev()"
                text="prev"
                btnClass="btn-dark"
                v-if="this.stepNumber !== 0"
            />
            <DashButton
                :text="stepNumber !== this.steps.length - 1 ? 'next' : 'submit'"
                btnClass="btn-dark"
            />
          </div>
        </form>
      </div>
    </Card>
  </div>
</template>

<style scoped lang="scss">

</style>
