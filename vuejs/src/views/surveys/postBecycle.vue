<script>
import Textinput from '@/components/Textinput/index.vue';
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import Checkbox from '@/components/Checkbox';
import {computed, ref} from 'vue';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Icon from '@/components/Icon';
import {useRouter} from 'vue-router';
import {useToast} from 'vue-toastification';
import SurveyInfo from '@/components/SurveyInfo/index.vue';

export default {
  name: 'postBecycle',
  components: {ErrorMessage, Checkbox, Card, DashButton, Textinput, Icon, SurveyInfo},
  setup() {
    const router = useRouter();
    const toast = useToast();
    const steps = [
      {
        id: 1,
        label: 'Information and Consent',
      },
      {
        id: 2,
        title: 'Satisfaction',
      },
      {
        id: 3,
        title: 'Returning your bike',
      },
      {
        id: 4,
        title: 'Your Journey',
      },
      {
        id: 5,
        title: 'Suggestions',
      },
    ];

    const stepNumber = ref(0);

    const consentSchema = yup.object().shape({
      consent: yup.boolean().oneOf([true], 'This check is required to take part in the survey.'),
    });

    const satisfactionSchema = yup.object().shape({
      serviceSatisfactionGetBike: yup.number().integer().min(0).max(10).required(),
      serviceSatisfactionFixBike: yup.number().integer().min(0).max(10).required(),
      serviceSatisfactionLearn: yup.number().integer().min(0).max(10).required(),
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
        return consentSchema;
      case 1:
        return satisfactionSchema;
      case 2:
        return reasonSchema;
      case 3:
        return issueAlternativeSchema;
      case 4:
        return improvementSchema;
      default:
        return consentSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: consent, errorMessage: consentError} = useField('consent');

    const {value: serviceSatisfactionGetBike, errorMessage: serviceSatisfactionGetBikeError} = useField('serviceSatisfactionGetBike');
    const {value: serviceSatisfactionFixBike, errorMessage: serviceSatisfactionFixBikeError} = useField('serviceSatisfactionFixBike');
    const {value: serviceSatisfactionLearn, errorMessage: serviceSatisfactionLearnError} = useField('serviceSatisfactionLearn');

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
    consent.value = false;
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
          serviceSatisfactionGetBike: serviceSatisfactionGetBike.value,
          serviceSatisfactionFixBike: serviceSatisfactionFixBike.value,
          serviceSatisfactionLearn: serviceSatisfactionLearn.value,
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
      consent,
      consentError,
      serviceSatisfactionGetBike,
      serviceSatisfactionGetBikeError,
      serviceSatisfactionFixBike,
      serviceSatisfactionFixBikeError,
      serviceSatisfactionLearn,
      serviceSatisfactionLearnError,
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
              :class="`transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col ` +
                      `items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium ` +
                      ` ${
                        stepNumber >= i
                          ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500' +
                            'dark:bg-slate-900 dark:ring-slate-900'
                          : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 ' +
                            'dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
                      }`"
              class=""
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
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <survey-info/>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I am taking part voluntarily and I consent to my answers being used in the stated manner."
                      name="consent"
                      v-model="consent"
                      :checked="consent"
                      activeClass="ring-info-500 bg-info-500"
                      :error="consentError"
                  />
                  <ErrorMessage name="consent" :error="consentError" class="text-danger-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 1">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  On a scale from 0 (do not agree at all) to 10 (agree fully), how much do you agree with the following statements?
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Textinput
                      label="Becycle has helped me get a bike."
                      type="text"
                      placeholder="4"
                      name="serviceSatisfactionGetBike"
                      v-model="serviceSatisfactionGetBike"
                      :error="serviceSatisfactionGetBikeError"
                  />
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Becycle has helped me fix a bike."
                      type="text"
                      placeholder="4"
                      name="serviceSatisfactionFixBike"
                      v-model="serviceSatisfactionFixBike"
                      :error="serviceSatisfactionFixBikeError"
                  />
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Becycle has helped me learn about bike maintenance."
                      type="text"
                      placeholder="4"
                      name="serviceSatisfactionLearn"
                      v-model="serviceSatisfactionLearn"
                      :error="serviceSatisfactionLearnError"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 2">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
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
                      :checked="reasonStoppedCycling"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I am leaving Aberdeen"
                      name="reasonLeavingAberdeen"
                      v-model="reasonLeavingAberdeen"
                      :checked="reasonLeavingAberdeen"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>

          <div v-if="stepNumber === 3 && reasonStoppedCycling">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4  class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What are the reasons why you stopped cycling? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I felt unsafe on the road"
                      name="issueSafety"
                      v-model="issueSafety"
                      :checked="issueSafety"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I could not afford to maintain a bike"
                      name="issueMoney"
                      v-model="issueMoney"
                      :checked="issueMoney"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It took too long getting from A to B on a bike"
                      name="issueTime"
                      v-model="issueTime"
                      :checked="issueTime"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="Exercising (and potentially sweating) during my daily commute was unappealing to me"
                      name="issueSweating"
                      v-model="issueSweating"
                      :checked="issueSweating"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It was not a comfortable mode of transportation"
                      name="issueComfort"
                      v-model="issueComfort"
                      :checked="issueComfort"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="My commute to work, school, grocery stores, or others was too long"
                      name="issueDistance"
                      v-model="issueDistance"
                      :checked="issueDistance"
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
          <div v-if="stepNumber === 3 && !reasonStoppedCycling">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
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
                      :checked="alternativeAnotherBecycle"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I have bought or will buy my own bike."
                      name="alternativeOwnBike"
                      v-model="alternativeOwnBike"
                      :checked="alternativeOwnBike"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I can use a bike from a friend or family."
                      name="alternativeShareFriendsFamily"
                      v-model="alternativeShareFriendsFamily"
                      :checked="alternativeShareFriendsFamily"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I rent a bike from a different service, long or short-term."
                      name="alternativeOtherRental"
                      v-model="alternativeOtherRental"
                      :checked="alternativeOtherRental"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 4">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
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
                      :checked="improvementNone"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="More cycle paths such as (segregated) cycling lanes"
                      name="improvementCyclingPaths"
                      v-model="improvementCyclingPaths"
                      :checked="improvementCyclingPaths"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Better lighting"
                      name="improvementLights"
                      v-model="improvementLights"
                      :checked="improvementLights"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Better surfaces with fewer potholes."
                      name="improvementSurface"
                      v-model="improvementSurface"
                      :checked="improvementSurface"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!improvementNone">
                  <Checkbox
                      label="Cleaner roads with less glass, sharp metal and slippery leaves."
                      name="improvementCleaner"
                      v-model="improvementCleaner"
                      :checked="improvementCleaner"
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
