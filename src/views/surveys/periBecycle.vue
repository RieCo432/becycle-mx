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
  name: 'periBecycle',
  components: {Checkbox, Card, DashButton, Textinput, Select, Icon},
  setup() {
    const router = useRouter();
    const toast = useToast();
    const steps = [
      {
        id: 1,
        title: 'Road Quality',
      },
      {
        id: 2,
        title: 'Road Users',
      },
      {
        id: 3,
        title: 'Routes',
      },
      {
        id: 3,
        title: 'Accidents',
      },
      {
        id: 3,
        title: 'Harassment',
      },
    ];

    const stepNumber = ref(0);

    const roadsSchema = yup.object().shape({
      roadsGreat: yup.boolean(),
      roadsLight: yup.boolean(),
      roadsPotholes: yup.boolean(),
      roadsRubbish: yup.boolean(),
      roadsParking: yup.boolean(),
      roadsDark: yup.boolean(),
    });

    const usersSchema = yup.object().shape({
      usersSafe: yup.boolean(),
      usersBusesUnsafe: yup.boolean(),
      usersCarsUnsafe: yup.boolean(),
      usersTrucksUnsafe: yup.boolean(),
      usersTaxisUnsafe: yup.boolean(),
      usersCyclistsUnsafe: yup.boolean(),
      usersPedestriansUnsafe: yup.boolean(),
    });

    const routesSchema = yup.object().shape({
      routesRoads: yup.boolean(),
      routesPavements: yup.boolean(),
      routesOffroad: yup.boolean(),
    });

    const accidentsSchema = yup.object().shape({
      accidentsNearMisses: yup.number().integer().min(0).required(),
      accidentsContact: yup.number().integer().min(0).required(),
    });

    const harassmentSchema = yup.object().shape({
      harassmentExperienced: yup.boolean(),
      harassmentSuggestions: yup.string(),
    });

    const currentSchema = computed(() => {
      switch (stepNumber.value) {
        case 0:
          return roadsSchema;
        case 1:
          return usersSchema;
        case 2:
          return routesSchema;
        case 3:
          return accidentsSchema;
        case 4:
          return harassmentSchema;
        default:
          return roadsSchema;
      }
    });

    const {handleSubmit} = useForm({
      validationSchema: currentSchema,
      keepValuesOnUnmount: true,
    });

    const {value: roadsGreat} = useField('roadsGreat');
    const {value: roadsLight} = useField('roadsLight');
    const {value: roadsPotholes} = useField('roadsPotholes');
    const {value: roadsRubbish} = useField('roadsRubbish');
    const {value: roadsParking} = useField('roadsParking');
    const {value: roadsDark} = useField('roadsDark');

    const {value: usersSafe} = useField('usersSafe');
    const {value: usersBusesUnsafe} = useField('usersBusesUnsafe');
    const {value: usersCarsUnsafe} = useField('usersCarsUnsafe');
    const {value: usersTrucksUnsafe} = useField('usersTrucksUnsafe');
    const {value: usersTaxisUnsafe} = useField('usersTaxisUnsafe');
    const {value: usersCyclistsUnsafe} = useField('usersCyclistsUnsafe');
    const {value: usersPedestriansUnsafe} = useField('usersPedestriansUnsafe');

    const {value: routesRoads} = useField('routesRoads');
    const {value: routesPavements} = useField('routesPavements');
    const {value: routesOffroad} = useField('routesOffroad');

    const {value: accidentsNearMisses, errorMessage: accidentsNearMissesError} = useField('accidentsNearMisses');
    const {value: accidentsContact, errorMessage: accidentsContactError} = useField('accidentsContact');

    const {value: harassmentExperienced} = useField('harassmentExperienced');
    const {value: harassmentSuggestions} = useField('harassmentSuggestions');

    // set defaults
    roadsGreat.value = false;
    roadsLight.value = false;
    roadsPotholes.value = false;
    roadsRubbish.value = false;
    roadsParking.value = false;
    roadsDark.value = false;

    usersSafe.value = false;
    usersBusesUnsafe.value = false;
    usersCarsUnsafe.value = false;
    usersTrucksUnsafe.value = false;
    usersTaxisUnsafe.value = false;
    usersCyclistsUnsafe.value = false;
    usersPedestriansUnsafe.value = false;

    routesRoads.value = false;
    routesPavements.value = false;
    routesOffroad.value = false;


    harassmentExperienced.value = false;

    const submit = handleSubmit(() => {
      // next step until last step . if last step then submit form
      const totalSteps = steps.length;
      const isLastStep = stepNumber.value === totalSteps - 1;
      if (isLastStep) {
        stepNumber.value = totalSteps - 1;
        // handle submit
        requests.postPeriBecycleSurvey({
          roadsGreat: roadsGreat.value,
          roadsLight: roadsLight.value,
          roadsPotholes: roadsPotholes.value,
          roadsRubbish: roadsRubbish.value,
          roadsParking: roadsParking.value,
          roadsDark: roadsDark.value,
          usersSafe: usersSafe.value,
          usersBusesUnsafe: usersBusesUnsafe.value,
          usersCarsUnsafe: usersCarsUnsafe.value,
          usersTrucksUnsafe: usersTrucksUnsafe.value,
          usersTaxisUnsafe: usersTaxisUnsafe.value,
          usersCyclistsUnsafe: usersCyclistsUnsafe.value,
          usersPedestriansUnsafe: usersPedestriansUnsafe.value,
          routesRoads: routesRoads.value,
          routesPavements: routesPavements.value,
          routesOffroad: routesOffroad.value,
          accidentsNearMisses: accidentsNearMisses.value,
          accidentsContact: accidentsContact.value,
          harassmentExperienced: harassmentExperienced.value,
          harassmentSuggestions: harassmentSuggestions.value,
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
      roadsGreat,
      roadsLight,
      roadsPotholes,
      roadsRubbish,
      roadsParking,
      roadsDark,
      usersSafe,
      usersBusesUnsafe,
      usersCarsUnsafe,
      usersTrucksUnsafe,
      usersTaxisUnsafe,
      usersCyclistsUnsafe,
      usersPedestriansUnsafe,
      routesRoads,
      routesPavements,
      routesOffroad,
      accidentsNearMisses,
      accidentsNearMissesError,
      accidentsContact,
      accidentsContactError,
      harassmentExperienced,
      harassmentSuggestions,

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
                  How do you feel about the quality of the roads in Aberdeen? Tick all that apply.
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="The road surfaces are great!"
                      name="roadsGreat"
                      v-model="roadsGreat"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="The roads are lit well enough for me to feel safe."
                      name="roadsLight"
                      v-model="roadsLight"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="There are too many potholes."
                      name="roadsPotholes"
                      v-model="roadsPotholes"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="There is a lot of rubbish on the roads, such as glass, metal and leaves, posing a danger."
                      name="roadsRubbish"
                      v-model="roadsRubbish"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="There are too many cars parked on the pavement and/or in cycle lanes."
                      name="roadsParking"
                      v-model="roadsParking"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="The roads are often too dark to cycle safely."
                      name="roadsDark"
                      v-model="roadsDark"
                      activeClass="ring-info-500 bg-info-500"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="stepNumber === 1">
            <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
              <div class="md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Do you feel safe while cycling on the road? If not, what other road users make you feel unsafe?
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I feel safe on the road."
                      name="usersSafe"
                      v-model="usersSafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Buses"
                      name="usersBusesUnsafe"
                      v-model="usersBusesUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Cars"
                      name="usersCarsUnsafe"
                      v-model="usersCarsUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Trucks"
                      name="usersTrucksUnsafe"
                      v-model="usersTrucksUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Taxis"
                      name="usersTaxisUnsafe"
                      v-model="usersTaxisUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Cyclists"
                      name="usersCyclistsUnsafe"
                      v-model="usersCyclistsUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="!usersSafe">
                  <Checkbox
                      label="Pedestrians"
                      name="usersPedestriansUnsafe"
                      v-model="usersPedestriansUnsafe"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 2">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Where do you mostly cycle?
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="On the road, with cars, etc..."
                      name="routesRoads"
                      v-model="routesRoads"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="On the pavement, with pedestrians"
                      name="routesPavements"
                      v-model="routesPavements"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1">
                  <Checkbox
                      label="Off-road, away from cars and pedestrians (e.g. forests)"
                      name="routesOffroad"
                      v-model="routesOffroad"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 3">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Accidents and Near Misses
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Textinput
                      label="Roughly, how many near misses (close to accident, but no contact or injury) have you experienced in the last year?"
                      type="text"
                      placeholder="2"
                      name="accidentsNearMisses"
                      v-model="accidentsNearMisses"
                      :error="accidentsNearMissesError"
                  />
                </div>
                <div class="col-span-1">
                  <Textinput
                      label="Roughly, how many accidents (contact with another road users, regardless of injury) have you experienced in the last year?"
                      type="text"
                      placeholder="2"
                      name="accidentsContact"
                      v-model="accidentsContact"
                      :error="accidentsContactError"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="stepNumber === 4">
            <div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-5">
              <div class="lg:col-span-3 md:col-span-2 col-span-1">
                <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
                  Harassment and discrimination due to your identity, such as gender, race, sexual orientation, disability, etc...
                </h4>
              </div>
              <div class="grid grid-cols-1 gap-5">
                <div class="col-span-1">
                  <Checkbox
                      label="I have been harassed or discriminated against due to my identity."
                      name="harassmentExperienced"
                      v-model="harassmentExperienced"
                      activeClass="ring-info-500 bg-info-500"/>
                </div>
                <div class="col-span-1" v-if="harassmentExperienced">
                  <Textinput
                      label="Would you like to tell us more? You can also include suggestions on how to address this issue."
                      type="text"
                      placeholder="Say as much or as little as you want."
                      name="accidentsContact"
                      v-model="harassmentSuggestions"
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
