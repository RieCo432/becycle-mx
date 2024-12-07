<script>
import Textinput from '@/components/Textinput/index.vue';
import DashButton from '@/components/Button/index.vue';
import Select from '@/components/Select/index.vue';
import Card from '@/components/Card/index.vue';
import Checkbox from '@/components/Checkbox/index.vue';
import {computed, ref} from 'vue';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Icon from '@/components/Icon';
import {useRouter} from 'vue-router';
import {useToast} from 'vue-toastification';
import surveyInfo from '@/components/SurveyInfo/index.vue';

export default {
  name: 'preBecycle',
  components: {ErrorMessage, Checkbox, Card, DashButton, Textinput, Select, Icon, surveyInfo},
  setup() {
    const router = useRouter();
    const toast = useToast();
    const steps = [
      {
        id: 1,
        title: 'Information and Consent',
      },
      {
        id: 2,
        title: 'Hurdles',
      },
      {
        id: 3,
        title: 'Motivation',
      },
      {
        id: 4,
        title: 'Options Considered',
      },
      {
        id: 5,
        title: 'Training and Experience',
      },
      {
        id: 6,
        title: 'Interest',
      },
    ];

    const stepNumber = ref(0);

    const consentSchema = yup.object().shape({
      consent: yup.boolean().oneOf([true], 'This check is required to take part in the survey.'),
    });

    const hurdleSchema = yup.object().shape({
      hurdleSafety: yup.boolean(),
      hurdleMoney: yup.boolean(),
      hurdleTime: yup.boolean(),
      hurdleSweating: yup.boolean(),
      hurdleComfort: yup.boolean(),
      hurdleDistance: yup.boolean(),
      hurdleOther: yup.string(),
    });

    const motivationSchema = yup.object().shape({
      motivationMoney: yup.boolean(),
      motivationHealth: yup.boolean(),
      motivationEnvironmental: yup.boolean(),
      motivationOther: yup.string(),
    });

    const consideredSchema = yup.object().shape({
      consideredNewOnline: yup.boolean(),
      consideredNewShop: yup.boolean(),
      consideredUsed: yup.boolean(),
      consideredLendingPrivate: yup.boolean(),
      consideredLendingBecycle: yup.boolean(),
      consideredOther: yup.string(),
    });

    const trainingSchema = yup.object().shape({
      trainingExperienceMonths: yup.number().integer().min(0).required(),
      trainingFormal: yup.boolean(),
      trainingConfidence: yup.number().integer().min(0).max(10).required(),
      trainingRules: yup.boolean(),
      trainingDriver: yup.boolean(),
      trainingNone: yup.boolean(),
    });

    const trainingExperienceMonthsOptions = ref([
      {
        label: 'None at all',
        value: 0,
      },
      {
        label: 'Less than 3 months',
        value: 3,
      },
      {
        label: 'Between 3 and 6 months',
        value: 6,
      },
      {
        label: 'Between 6 and 18 months',
        value: 18,
      },
      {
        label: 'Over 18 months',
        value: 24,
      },
    ]);

    const interestMaintenanceDesiredOptions = ref([
      {
        label: 'I do not care',
        value: 0,
      },
      {
        label: 'I want to know enough to keep my bicycle in a good condition',
        value: 1,
      },
      {
        label: 'I want to know basic repairs',
        value: 2,
      },
      {
        label: 'I want to know how to fix everything',
        value: 3,
      },
    ]);

    const interestMaintenanceCurrentOptions = ref([
      {
        label: 'I know nothing',
        value: 0,
      },
      {
        label: 'I know how enough to keep my bicycle in a good condition',
        value: 1,
      },
      {
        label: 'I know how to do basic repairs',
        value: 2,
      },
      {
        label: 'I know how to fix almost anything',
        value: 3,
      },
    ]);

    const interestSchema = yup.object().shape({
      interestMaintenanceCurrent: yup.number().integer().min(0).max(3).required(),
      interestMaintenanceDesired: yup.number().integer().min(0).max(3).required(),
    });

    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return consentSchema;
        case 1:
          return hurdleSchema;
        case 2:
          return motivationSchema;
        case 3:
          return consideredSchema;
        case 4:
          return trainingSchema;
        case 5:
          return interestSchema;
        default:
          return consentSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: consent, errorMessage: consentError} = useField('consent');

    const {value: hurdleSafety} = useField('hurdleSafety');
    const {value: hurdleMoney} = useField('hurdleMoney');
    const {value: hurdleTime} = useField('hurdleTime');
    const {value: hurdleSweating} = useField('hurdleSweating');
    const {value: hurdleComfort} = useField('hurdleComfort');
    const {value: hurdleDistance} = useField('hurdleDistance');
    const {value: hurdleOther} = useField('hurdleOther');

    const {value: motivationMoney} = useField('motivationMoney');
    const {value: motivationHealth} = useField('motivationHealth');
    const {value: motivationEnvironmental} = useField('motivationEnvironmental');
    const {value: motivationOther} = useField('motivationOther');

    const {value: consideredNewOnline} = useField('consideredNewOnline');
    const {value: consideredNewShop} = useField('consideredNewShop');
    const {value: consideredUsed} = useField('consideredUsed');
    const {value: consideredLendingPrivate} = useField('consideredLendingPrivate');
    const {value: consideredLendingBecycle} = useField('consideredLendingBecycle');
    const {value: consideredOther} = useField('consideredOther');

    const {value: trainingExperienceMonths, errorMessage: trainingExperienceMonthsError} = useField('trainingExperienceMonths');
    const {value: trainingFormal} = useField('trainingFormal');
    const {value: trainingConfidence, errorMessage: trainingConfidenceError} = useField('trainingConfidence');
    const {value: trainingRules} = useField('trainingRules');
    const {value: trainingDriver} = useField('trainingDriver');
    const {value: trainingNone} = useField('trainingNone');

    const {value: interestMaintenanceCurrent, errorMessage: interestMaintenanceCurrentError} = useField('interestMaintenanceCurrent');
    const {value: interestMaintenanceDesired, errorMessage: interestMaintenanceDesiredError} = useField('interestMaintenanceDesired');

    // set defaults
    consent.value = false;

    hurdleSafety.value = false;
    hurdleMoney.value = false;
    hurdleTime.value = false;
    hurdleSweating.value = false;
    hurdleComfort.value = false;
    hurdleDistance.value = false;

    motivationMoney.value = false;
    motivationHealth.value = false;
    motivationEnvironmental.value = false;

    consideredNewOnline.value = false;
    consideredNewShop.value = false;
    consideredUsed.value = false;
    consideredLendingPrivate.value = false;
    consideredLendingBecycle.value = false;

    trainingFormal.value = false;
    trainingRules.value = false;
    trainingDriver.value = false;

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        requests.postPreBecycleSurvey({
          hurdleSafety: hurdleSafety.value,
          hurdleMoney: hurdleMoney.value,
          hurdleTime: hurdleTime.value,
          hurdleSweating: hurdleSweating.value,
          hurdleComfort: hurdleComfort.value,
          hurdleDistance: hurdleDistance.value,
          hurdleOther: hurdleOther.value,
          motivationMoney: motivationMoney.value,
          motivationHealth: motivationHealth.value,
          motivationEnvironmental: motivationEnvironmental.value,
          motivationOther: motivationOther.value,
          consideredNewOnline: consideredNewOnline.value,
          consideredNewShop: consideredNewShop.value,
          consideredUsed: consideredUsed.value,
          consideredLendingPrivate: consideredLendingPrivate.value,
          consideredLendingBecycle: consideredLendingBecycle.value,
          consideredOther: consideredOther.value,
          trainingExperienceMonths: trainingExperienceMonths.value,
          trainingFormal: trainingFormal.value,
          trainingConfidence: trainingConfidence.value,
          trainingRules: trainingRules.value,
          trainingDriver: trainingDriver.value,
          interestMaintenanceCurrent: interestMaintenanceCurrent.value,
          interestMaintenanceDesired: interestMaintenanceDesired.value,
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

      hurdleSafety,
      hurdleMoney,
      hurdleTime,
      hurdleSweating,
      hurdleComfort,
      hurdleDistance,
      hurdleOther,

      motivationMoney,
      motivationHealth,
      motivationEnvironmental,
      motivationOther,

      consideredNewOnline,
      consideredNewShop,
      consideredUsed,
      consideredLendingPrivate,
      consideredLendingBecycle,
      consideredOther,

      trainingExperienceMonths,
      trainingExperienceMonthsError,
      trainingExperienceMonthsOptions,
      trainingFormal,
      trainingConfidence,
      trainingConfidenceError,
      trainingRules,
      trainingDriver,
      trainingNone,

      interestMaintenanceCurrentOptions,
      interestMaintenanceDesiredOptions,

      interestMaintenanceCurrent,
      interestMaintenanceCurrentError,
      interestMaintenanceDesired,
      interestMaintenanceDesiredError,

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
                  According to you, what are the biggest hurdles that have prevented, or still prevent you, from cycling? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="Road Safety"
                      name="hurdleSafety"
                      v-model="hurdleSafety"
                      :checked="hurdleSafety"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I don't have money for a bike"
                      name="hurdleMoney"
                      v-model="hurdleMoney"
                      :checked="hurdleMoney"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It takes too long getting from A to B on a bike"
                      name="hurdleTime"
                      v-model="hurdleTime"
                      :checked="hurdleTime"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="The idea of exercising (and potentially sweating) during my daily commute is unappealing to me"
                      name="hurdleSweating"
                      v-model="hurdleSweating"
                      :checked="hurdleSweating"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It is not a comfortable mode of transportation"
                      name="hurdleComfort"
                      v-model="hurdleComfort"
                      :checked="hurdleComfort"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I would like cycle more, but my commute to work, school, grocery stores, or others is too long"
                      name="hurdleDistance"
                      v-model="hurdleDistance"
                      :checked="hurdleDistance"
                      activeClass="ring-info-500 bg-info-500"
                  />
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Other"
                      type="text"
                      placeholder="Other reasons"
                      name="hurdleOther"
                      v-model="hurdleOther"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 2">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What motivated you to get a bike? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="It is a cheap mode of transportation"
                      name="motivationMoney"
                      v-model="motivationMoney"
                      :checked="motivationMoney"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It is a healthy mode of transportation"
                      name="motivationHealth"
                      v-model="motivationHealth"
                      :checked="motivationHealth"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="It is a sustainable mode of transportation"
                      name="motivationEnvironmental"
                      v-model="motivationEnvironmental"
                      :checked="motivationEnvironmental"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Other"
                      type="text"
                      placeholder="Other reasons"
                      name="motivationOther"
                      v-model="motivationOther"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 3">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  When you decided to get a bike, which of the following options did you consider? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I considered buying a new bike online"
                      name="consideredNewOnline"
                      :checked="consideredNewOnline"
                      v-model="consideredNewOnline"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I considered buying a new bike in physical bike shop"
                      name="consideredNewShop"
                      v-model="consideredNewShop"
                      :checked="consideredNewShop"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I considered buying a bike second hand (e.g. Facebook Marketplace, e-Bay, ...)"
                      name="consideredUsed"
                      v-model="consideredUsed"
                      :checked="consideredUsed"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I considered borrowing a bike from friends or family"
                      name="consideredLendingPrivate"
                      v-model="consideredLendingPrivate"
                      :checked="consideredLendingPrivate"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I considered lending a bike from Becycle"
                      name="consideredLendingBecycle"
                      v-model="consideredLendingBecycle"
                      :checked="consideredLendingBecycle"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Other"
                      type="text"
                      placeholder="Other options"
                      name="consideredOther"
                      v-model="consideredOther"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 4">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Training and Experience
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Select
                      label="Roughly, how many MONTHS of cycling experience, particularly on the road, do you have?"
                      :options="trainingExperienceMonthsOptions"
                      name="trainingExperienceMonths"
                      v-model="trainingExperienceMonths"
                      :error="trainingExperienceMonthsError"
                  />
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="On a scale from 0 (not confident at all) to 10 (completely confident), how confident are in your ability to cycle on the roads in Aberdeen?"
                      type="text"
                      placeholder="5"
                      name="trainingConfidence"
                      v-model="trainingConfidence"
                      :error="trainingConfidenceError"
                  />
                </div>
                <div class="col-span-1">
                  <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                    Additional statements about being a cyclist in town. Tick all that apply.
                  </h4>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="I have not received any training on how to behave as a road user, whether as a cyclist or motorist."
                      name="trainingNone"
                      v-model="trainingNone"
                      :checked="trainingNone"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!trainingNone">
                  <Checkbox
                      label="I have received some form of training on how to cycle on the road."
                      name="trainingFormal"
                      v-model="trainingFormal"
                      :checked="trainingFormal"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!trainingNone">
                  <Checkbox
                      label="I know the rules of the highway code and how they apply to me as a cyclist."
                      name="trainingRules"
                      v-model="trainingRules"
                      :checked="trainingRules"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!trainingNone">
                  <Checkbox
                      label="I am a driver (car, motorcycle, van, etc), so I know how to behave as a road user."
                      name="trainingDriver"
                      v-model="trainingDriver"
                      :checked="trainingDriver"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 5">
            <div class="grid grid-cols-1 gap-5">
              <div class="col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Interest in Bicycle Maintenance
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Select
                      :options="interestMaintenanceCurrentOptions"
                      label="How would you describe your level of knowledge on bicycle maintenance?"
                      v-model="interestMaintenanceCurrent"
                      name="interestMaintenance"
                      :error="interestMaintenanceCurrentError"
                  />
                </div>
                <div class="col-span-1">
                  <Select
                      :options="interestMaintenanceDesiredOptions"
                      label="How much would you like to know about bicycle maintenance"
                      v-model="interestMaintenanceDesired"
                      name="interestMaintenance"
                      :error="interestMaintenanceDesiredError"
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
