const routes = [
  {
    path: '/',
    name: 'Layout',
    redirect: '/home',
    meta: {
      restrictTo: null,
      hide: true,
      selectNavPath: '/home',
    },
    component: () => import('@/Layout/index.vue'),
    children: [
      {
        path: '/home',
        name: 'home',
        meta: {
          restrictTo: null,
          selectNavPath: '/home',
        },
        component: () => import('@/views/home.vue'),
      },
      {
        path: '/me',
        name: 'Profile',
        meta: {
          restrictTo: ['client', 'user'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/me.vue'),
      },
      {
        path: '/template',
        name: 'template',
        meta: {
          restrictTo: null,
          selectNavPath: '/template',
        },
        component: () => import('@/views/template.vue'),
      },
      {
        path: '/users/login',
        name: 'Volunteer Login',
        meta: {
          restrictTo: null,
          selectNavPath: '/login',
        },
        component: () => import('@/views/login/user.vue'),
      },
      {
        path: '/clients/login',
        name: 'Client Login',
        meta: {
          restrictTo: null,
          selectNavPath: '/login',
        },
        component: () => import('@/views/login/client.vue'),
      },
      {
        path: '/users/me',
        name: 'User',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/user/me.vue'),
      },
      {
        path: '/clients/me',
        name: 'Me',
        meta: {
          restrictTo: ['client'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/client/me.vue'),
      },
      {
        path: '/clients/:clientId',
        name: 'Client',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/clients',
        },
        component: () => import('@/views/client/index.vue'),
      },
      {
        path: '/clients/me/contracts/:contractId',
        name: 'Me',
        meta: {
          restrictTo: ['client'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/contract/clientIndex.vue'),
      },
      {
        path: '/contracts/:contractId',
        name: 'Contract',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/contracts',
        },
        component: () => import('@/views/contract/index.vue'),

      },
      {
        path: '/contracts/new',
        name: 'New Contract',
        meta: {
          restrictTo: ['user'],
          hide: true,
          selectNavPath: '/contracts/new',
        },
        component: () => import('@/views/contract/newContract.vue'),
      },
      {
        path: '/clients',
        name: 'Find Client',
        meta: {
          restrictTo: ['user'],
          hide: true,
          selectNavPath: '/clients',
        },
        component: () => import('@/views/client/findClient.vue'),
      },
      {
        path: '/appointments/book',
        name: 'Book Appointment',
        meta: {
          restrictTo: ['client'],
          selectNavPath: '/appointments/book',
        },
        component: () => import('@/views/appointments/bookAppointment.vue'),
      },
      {
        path: '/appointments',
        name: 'Appointment Calendar',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/appointments',
        },
        component: () => import('@/views/appointments/index.vue'),
      },
      {
        path: '/accounting/deposits',
        name: 'Deposit Book',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/accounting/deposits',
        },
        component: () => import('@/views/accounting/depositBook.vue'),
      },
      {
        path: '/admin/users',
        name: 'User Management',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/admin/users',
        },
        component: () => import('@/views/admin/userRoles.vue'),
      },
      {
        path: '/admin/appointment-types',
        name: 'Appointment Types',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/admin/appointment-types',
        },
        component: () => import('@/views/admin/appointmentTypes.vue'),
      },
      {
        path: '/admin/appointment-settings',
        name: 'Appointment Settings',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/admin/appointment-settings',
        },
        component: () => import('@/views/admin/appointmentSettings.vue'),
      },
      {
        path: '/admin/deposit-exchanges',
        name: 'Deposit Exchanges',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/admin/deposit-exchanges',
        },
        component: () => import('@/views/admin/DepositExchanges.vue'),
      },
      {
        path: '/contracts/find-paper-contract',
        name: 'Find Paper Contract',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/contracts/find-paper-contract',
        },
        component: () => import('@/views/contract/findPaperContract.vue'),
      },
      {
        path: '/statistics/users/leaderboard',
        name: 'Volunteer Leaderboard',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/statistics/users/leaderboard',
        },
        component: () => import('@/views/statistics/userLeaderboard.vue'),
      },
      {
        path: '/statistics/clients/leaderboard',
        name: 'Client Leaderboard',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/statistics/clients/leaderboard',
        },
        component: () => import('@/views/statistics/clientLeaderboard.vue'),
      },
      {
        path: '/statistics/bikes/leaderboard',
        name: 'Bike Leaderboard',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/statistics/bikes/leaderboard',
        },
        component: () => import('@/views/statistics/bikeLeaderboard.vue'),
      },
      {
        path: '/bikes/:bikeId',
        name: 'Bike',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/bikes',
        },
        component: () => import('@/views/bike/index.vue'),
      },
      {
        path: '/bikes',
        name: 'Find Bike',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/bikes',
        },
        component: () => import('@/views/bike/findBike.vue'),
      },
      {
        path: '/statistics/contracts',
        name: 'Contract Charts',
        meta: {
          restrictTo: ['user'],
          selectNavPath: '/statistics/contracts',
        },
        component: () => import('@/views/statistics/contractCharts.vue'),
      },
      {
        path: '/surveys/pre-becycle',
        name: 'Pre-Becycle Survey',
        meta: {
          restrictTo: ['client'],
          selectNavPath: '/surveys/pre-becycle',
        },
        component: () => import('@/views/surveys/preBecycle.vue'),
      },
      {
        path: '/surveys/map',
        name: 'Cycling Suitability Map',
        meta: {
          restrictTo: null,
          selectNavPath: '/surveys/map',
        },
        component: () => import('@/views/surveys/cyclingSuitabilityMap.vue'),
      },
    ],
  },
];

export default routes;
