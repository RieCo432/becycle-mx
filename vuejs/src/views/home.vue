<template>
    <div class="grid grid-cols-12 gap-5">
        <div class="lg:col-span-6 col-span-12">
            <Card title="Welcome to BECYCLE">
                <div class="grid grid-cols-12 h-full gap-5">
                  <div class="col-span-12">
                    <p class="text-base text-slate-700 dark:text-slate-300">
                        This is the official website for BECYCLE Workshop SCIO,
                        the community bicycle library and workshop in Aberdeen.</p><br>
                    <p class="text-base text-slate-700 dark:text-slate-300" v-if="!loadingAddress">
                        We are located at:<br>
                        {{ address.number }} {{ address.street }}<br>
                        {{ address.postcode }}, {{ address.city }}
                    </p>
                    <p class="text-base text-slate-700 dark:text-slate-300 animate-pulse" v-else>
                      We are located at:<br>
                      Loading...<br>
                      Loading...
                    </p>
                    <br>
                    <span class="text-base text-slate-700 dark:text-slate-300">You can donate to our cause via PayPal:</span><br>
                      <div id="donate-button-container">
                        <div id="donate-button"></div>
                      </div>
                    <p class="text-base text-slate-700 dark:text-slate-300">You can contact us directly on social media:<br>
                      <a href="https://facebook.com/beCyCleWorkshop/">
                          <img src="/src/assets/images/social/Facebook_Logo_Primary.png"
                               class="w-[32px] h-[32px] m-[16px] inline" alt="Facebook"/></a>
                      <a href="https://instagram.com/becycleworkshop/">
                          <img src="/src/assets/images/social/Instagram_Glyph_Gradient.png"
                               class="w-[32px] h-[32px] m-[16px] inline" alt="Instagram"/></a>
                    </p>
                  </div>
                  <div v-if="isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToBookAppointment" class="mt-auto">Book Appointment</DashButton>
                  </div>
                  <div v-if="isNotUser && isNotClient" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToClientLogin" class="mt-auto">Client Register/Login</DashButton>
                  </div>
                  <div v-if="!isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToNewContract" class="mt-auto">New Contract</DashButton>
                  </div>
                  <div v-if="!isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToFindClient" class="mt-auto">Find Client</DashButton>
                  </div>
                </div>

            </Card>
        </div>
        <div class="lg:col-span-6 col-span-12">
            <Card title="Opening Days and Times">
              <div class="grid grid-cols-12 gap-5">
                <div class="col-span-12">
                  <Calendar
                      v-if="!loadingClosedDays && !loadingOpenDays"
                      expanded
                      :is-dark="themeSettingsStore.isDark"
                      :columns="numCalendarColumns"
                      :step="1"
                      :attributes="calendarAttributes"
                      :first-day-of-week="2"
                      :min-date="new Date()"/>
                  <div v-else class="rounded-md h-64 animate-pulse items-center bg-[#C4C4C4] dark:bg-slate-500 mx-auto"></div>
                </div>
                <div class="col-span-12">
                  <vue-good-table
                      v-if="!loadingOpeningTimes"
                      :columns="columns"
                      :rows="openingTimes"
                      style-class="vgt-table"
                      :sort-options="{
                    enabled: false
                  }"/>
                  <div v-else>
                    <TableSkeleton num-columns="3" count="2"></TableSkeleton>
                  </div>
                </div>
              </div>
            </Card>
        </div>
    </div>
</template>

<script>
import requests from '@/requests';
import Card from '@/components/Card';
import DashButton from '@/components/Button/index.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useThemeSettingsStore} from '@/store/themeSettings';
import {Calendar} from 'v-calendar';
import 'v-calendar/style.css';
import {useScreens} from 'vue-screen-utils';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';

const credentialsStore = useCredentialsStore();
const themeSettingsStore = useThemeSettingsStore();
const {mapCurrent} = useScreens({
  xs: '0px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  xxl: '1536px',
});

export default {
  components: {
    TableSkeleton,
    DashButton,
    Card,
    Calendar,
  },
  data() {
    return {
      loadingOpeningTimes: true,
      loadingClosedDays: true,
      loadingOpenDays: true,
      loadingAddress: true,
      openingTimes: null,
      address: null,
      themeSettingsStore: themeSettingsStore,
      calendarAttributes: [],
      numCalendarColumns: mapCurrent({xs: 1, sm: 2, md: 2, lg: 1, xxl: 2}, 1),
      columns: [
        {
          label: 'Day',
          field: 'day',
        },
        {
          label: 'Open',
          field: 'open',
        },
        {
          label: 'Close',
          field: 'close',
        },
      ],
    };
  },
  computed: {
    isNotUser() {
      return credentialsStore.getTokenType() !== 'user';
    },
    isNotClient() {
      return credentialsStore.getTokenType() !== 'client';
    },
  },
  methods: {
    goToBookAppointment() {
      this.$router.push({path: '/appointments/book'});
    },
    goToClientLogin() {
      this.$router.push({path: '/clients/login'});
    },
    goToNewContract() {
      this.$router.push({path: '/contracts/new'});
    },
    goToFindClient() {
      this.$router.push({path: '/clients'});
    },
  },
  mounted() {
    requests.getOpeningTimes().then((response) => {
      this.openingTimes = response.data;
      this.loadingOpeningTimes = false;
    });
    requests.getUpcomingClosures().then((response) => {
      const closedDays = response.data.filter((closure) => closure.type === 'day')
        .map((closure) => (new Date(Date.parse(closure.item.date))));
      const closedPeriods = response.data.filter((closure) => closure.type === 'period')
        .map((closure) => (
          [
            new Date(Date.parse(closure.item.date)),
            new Date(Date.parse(closure.item.untilDate)),
          ]));
      this.calendarAttributes.push({
        key: 'closedDays',
        dates: closedDays,
        highlight: {
          color: 'red',
          fillMode: 'light',
        },
      });
      this.calendarAttributes.push({
        key: 'closedPeriods',
        dates: closedPeriods,
        highlight: {
          color: 'red',
          fillMode: 'light',
        },
      });
      this.loadingClosedDays = false;
    });
    requests.getUpcomingOpenDates().then((response) => {
      response.data.forEach((openDay) => {
        this.calendarAttributes.push({
          key: 'openDays' + openDay,
          dates: new Date(Date.parse(openDay)),
          highlight: {
            color: 'green',
            fillMode: 'light',
          },
        });
      });
      this.loadingOpenDays = false;
    });
    requests.getAddress().then((response) => {
      this.address = response.data;
      this.loadingAddress = false;
    });
    function loadAsync(url, callback) {
      const s = document.createElement('script');
      s.setAttribute('src', url); s.onload = callback;
      document.head.insertBefore(s, document.head.firstElementChild);
    }
    loadAsync('https://www.paypalobjects.com/donate/sdk/donate-sdk.js', function() {
      // eslint-disable-next-line new-cap
      PayPal.Donation.Button({
        env: 'production',
        hosted_button_id: '5XHLXRAKWQEEN',
        image: {
          src: 'https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif',
          alt: 'Donate with PayPal button',
          title: 'PayPal - The safer, easier way to pay online!',
        },
      }).render('#donate-button');
    });
    loadAsync('https://app.termly.io/resource-blocker/cfac8041-9e2d-4f64-9c8b-1ba418ea07a1?autoBlock=on');
  },
};

</script>
<style lang=""></style>
