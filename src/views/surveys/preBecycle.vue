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
  name: 'preBecycle',
  components: {Checkbox, Card, DashButton, Textinput, Select, Icon},
  setup() {
    const router = useRouter();
    const toast = useToast();
    const steps = [
      {
        id: 1,
        title: 'Hurdles',
      },
      {
        id: 2,
        title: 'Motivation',
      },
      {
        id: 3,
        title: 'Options Considered',
      },
      {
        id: 3,
        title: 'Training',
      },
      {
        id: 3,
        title: 'Interest',
      },
    ];

    const stepNumber = ref(0);

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
    });

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
          return hurdleSchema;
        case 1:
          return motivationSchema;
        case 2:
          return consideredSchema;
        case 3:
          return trainingSchema;
        case 4:
          return interestSchema;
        default:
          return hurdleSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

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

    const {value: interestMaintenanceCurrent, errorMessage: interestMaintenanceCurrentError} = useField('interestMaintenanceCurrent');
    const {value: interestMaintenanceDesired, errorMessage: interestMaintenanceDesiredError} = useField('interestMaintenanceDesired');

    // set defaults
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
      trainingFormal,
      trainingConfidence,
      trainingConfidenceError,
      trainingRules,
      trainingDriver,

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
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What are the biggest hurdles that prevented you from cycling? Tick all that apply.
                </h4>
              </div>
              <Checkbox
                  label="Road Safety"
                  name="hurdleSafety"
                  v-model="hurdleSafety"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="I don't have money for a bike"
                  name="hurdleMoney"
                  v-model="hurdleMoney"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="It takes too much time"
                  name="hurdleTime"
                  v-model="hurdleTime"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="I don't want to arrive sweaty"
                  name="hurdleSweating"
                  v-model="hurdleSweating"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="It's not comfortable"
                  name="hurdleComfort"
                  v-model="hurdleComfort"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="It's too far"
                  name="hurdleDistance"
                  v-model="hurdleDistance"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Textinput
                  label="Other"
                  type="text"
                  placeholder="Other reasons"
                  name="hurdleOther"
                  v-model="hurdleOther"
              />

            </div>
          </div>

          <div v-if="stepNumber === 1">
            <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
              <div class="md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What were your motivations for getting a bike? Tick all that apply.
                </h4>
              </div>
              <Checkbox
                  label="It's a cheap means of transportation"
                  name="motivationMoney"
                  v-model="motivationMoney"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="It's a healthy means of transportation"
                  name="motivationHealth"
                  v-model="motivationHealth"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="It's a sustainable means of transportation"
                  name="motivationEnvironmental"
                  v-model="motivationEnvironmental"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Textinput
                  label="Other"
                  type="text"
                  placeholder="Other reasons"
                  name="motivationOther"
                  v-model="motivationOther"
              />

            </div>
          </div>
          <div v-if="stepNumber === 2">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  What options did you consider for getting a bike? Tick all that apply.
                </h4>
              </div>
              <Checkbox
                  label="Buying new online"
                  name="consideredNewOnline"
                  v-model="consideredNewOnline"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="Buying new from  a shop"
                  name="consideredNewShop"
                  v-model="consideredNewShop"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="Buying Used (e.g. Facebook Marketplace, e-Bay, ...)"
                  name="consideredUsed"
                  v-model="consideredUsed"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="Lending from a friend, or family"
                  name="consideredLendingPrivate"
                  v-model="consideredLendingPrivate"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="Lending from Becycle"
                  name="consideredLendingBecycle"
                  v-model="consideredLendingBecycle"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Textinput
                  label="Other"
                  type="text"
                  placeholder="Other options"
                  name="consideredOther"
                  v-model="consideredOther"
              />
            </div>
          </div>
          <div v-if="stepNumber === 3">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Training and Experience
                </h4>
              </div>
              <Textinput
                  label="Roughly, how many MONTHS of cycling experience, particularly on the road, do you have?"
                  type="text"
                  placeholder="6"
                  name="trainingExperienceMonths"
                  v-model="trainingExperienceMonths"
                  :error="trainingExperienceMonthsError"
              />
              <Textinput
                  label="On a scale from 0 (not confident at all) to 10 (completely confident) are you about your ability to cycle on the road in Aberdeen?"
                  type="text"
                  placeholder="5"
                  name="trainingConfidence"
                  v-model="trainingConfidence"
                  :error="trainingConfidenceError"
              />
              <Checkbox
                  label="I have received some form of training for cycling on the road"
                  name="trainingFormal"
                  v-model="trainingFormal"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="I know the rules of the highway code and how they apply to me as a cyclist"
                  name="trainingRules"
                  v-model="trainingRules"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>
              <Checkbox
                  label="I am a driver (car, motorcycle, van, etc...)"
                  name="trainingDriver"
                  v-model="trainingDriver"
                  activeClass="ring-info-500 bg-info-500"
              ></Checkbox>

            </div>
          </div>
          <div v-if="stepNumber === 4">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Interest in Bicycle Maintenance
                </h4>
              </div>
              <Select
                  :options="interestMaintenanceCurrentOptions"
                  label="How would you describe your level knowledge of bicycle maintenance?"
                  v-model="interestMaintenanceCurrent"
                  name="interestMaintenance"
                  :error="interestMaintenanceCurrentError"
              />
              <Select
                  :options="interestMaintenanceDesiredOptions"
                  label="How much would you like to know about bicycle maintenance"
                  v-model="interestMaintenanceDesired"
                  name="interestMaintenance"
                  :error="interestMaintenanceDesiredError"
              />
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