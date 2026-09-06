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
          title: 'Home',
          restrictTo: null,
          selectNavPath: '/home',
        },
        component: () => import('@/views/home.vue'),
      },
      {
        path: '/privacy-policy',
        name: 'privacyPolicy',
        meta: {
          title: 'Privacy Policy',
          restrictTo: null,
          selectNavPath: '/privacy-policy',
        },
        component: () => import('@/views/privacyPolicy.vue'),
      },
      {
        path: '/me',
        name: 'Profile',
        meta: {
          title: 'Profile',
          restrictTo: ['client', 'user'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/me.vue'),
      },
      {
        path: '/template',
        name: 'template',
        meta: {
          title: 'Template',
          restrictTo: null,
          selectNavPath: '/template',
        },
        component: () => import('@/views/template.vue'),
      },
      {
        path: '/volunteers',
        name: 'Volunteers',
        meta: {
          title: 'Volunteers',
          restrictTo: null,
          selectNavPath: '/volunteers',
        },
        component: () => import('@/views/ourVolunteers.vue'),
      },
      {
        path: '/faq',
        name: 'FAQ',
        meta: {
          title: 'FAQ',
          restrictTo: null,
          selectNavPath: '/faq',
        },
        component: () => import('@/views/Faq.vue'),
      },
      {
        path: '/users/login',
        name: 'Volunteer Login',
        meta: {
          title: 'Volunteer Login',
          restrictTo: null,
          selectNavPath: '/login',
        },
        component: () => import('@/views/login/user.vue'),
      },
      {
        path: '/clients/login',
        name: 'Client Login',
        meta: {
          title: 'Client Login',
          restrictTo: null,
          selectNavPath: '/login',
        },
        component: () => import('@/views/login/client.vue'),
      },
      {
        path: '/users/me',
        name: 'User',
        meta: {
          title: 'User',
          restrictTo: ['user'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/user/me.vue'),
      },
      {
        path: '/clients/me',
        name: 'Me',
        meta: {
          title: 'Me',
          restrictTo: ['client'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/client/me.vue'),
      },
      {
        path: '/clients/:clientId',
        name: 'Client',
        meta: {
          title: 'Client',
          restrictTo: ['user'],
          selectNavPath: '/clients',
        },
        component: () => import('@/views/client/index.vue'),
      },
      {
        path: '/clients/me/contracts/:contractId',
        name: 'Me',
        meta: {
          title: 'Me',
          restrictTo: ['client'],
          selectNavPath: '/me',
        },
        component: () => import('@/views/contract/clientIndex.vue'),
      },
      {
        path: '/contracts/:contractId',
        name: 'Contract',
        meta: {
          title: 'Contract',
          restrictTo: ['user'],
          selectNavPath: '/contracts',
        },
        component: () => import('@/views/contract/index.vue'),

      },
      {
        path: '/contracts/new',
        name: 'New Contract',
        meta: {
          title: 'New Contract',
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
          title: 'Find Client',
          restrictTo: ['user'],
          hide: true,
          selectNavPath: '/clients',
        },
        component: () => import('@/views/client/findClient.vue'),
      },

      {
        path: '/appointments/cancel',
        name: 'Cancel Appointment',
        meta: {
          title: 'Cancel Appointment',
          restrictTo: null,
          selectNavPath: '/home',
        },
        component: () => import('@/views/appointments/cancel.vue'),
      },
      {
        path: '/appointments/reschedule',
        name: 'Reschedule Appointment',
        meta: {
          title: 'Reschedule Appointment',
          restrictTo: null,
          selectNavPath: '/home',
        },
        component: () => import('@/views/appointments/clientBookAppointment.vue'),
      },
      {
        path: '/appointments/book',
        name: 'Book Appointment',
        meta: {
          title: 'Book Appointment',
          restrictTo: ['client'],
          selectNavPath: '/appointments/book',
        },
        component: () => import('@/views/appointments/clientBookAppointment.vue'),
      },
      {
        path: '/appointments/inperson-book',
        name: 'Book Appointment In-Person',
        meta: {
          title: 'Book Appointment In-Person',
          restrictTo: ['user'],
          selectNavPath: '/appointments/inperson-book',
        },
        component: () => import('@/views/appointments/userBookAppointment.vue'),
      },
      {
        path: '/appointments',
        name: 'Appointment Calendar',
        meta: {
          title: 'Appointment Calendar',
          restrictTo: ['user'],
          selectNavPath: '/appointments',
        },
        component: () => import('@/views/appointments/index.vue'),
      },
      {
        path: '/finances/deposits',
        name: 'Deposit Balances',
        meta: {
          title: 'Deposit Balances',
          restrictTo: ['user'],
          selectNavPath: '/finances/deposits',
        },
        component: () => import('@/views/finances/depositBalances.vue'),
      },
      {
        path: '/finances/dashboards',
        name: 'Deposit Dashboards',
        meta: {
          title: 'Dashboards',
          restrictTo: ['user'],
          selectNavPath: '/finances/dashboards',
        },
        component: () => import('@/views/finances/dashboards.vue'),
      },
      {
        path: '/finances/expenses/submit', // TODO: this needs deleted
        name: 'Submit Expense',
        meta: {
          title: 'Submit Expense',
          restrictTo: ['user'],
          selectNavPath: '/finances/expenses/submit',
        },
        component: () => import('@/views/finances/newExpense.vue'),
      },
      {
        path: '/finances/expenses/claim',
        name: 'Claim Expense',
        meta: {
          title: 'Claim Expense',
          restrictTo: ['user'],
          selectNavPath: '/finances/expenses/claim',
        },
        component: () => import('@/views/finances/newExpenseClaim.vue'),
      },
      {
        path: '/finances/expenses/manage', // TODO: this needs deleted
        name: 'Manage Expenses',
        meta: {
          title: 'Manage Expenses',
          restrictTo: ['user'],
          selectNavPath: '/finances/expenses/manage',
        },
        component: () => import('@/views/finances/manageExpenses.vue'),
      },
      {
        path: '/finances/expenses/claims/manage',
        name: 'Manage Expense Claims',
        meta: {
          title: 'Manage Expense Claims',
          restrictTo: ['user'],
          selectNavPath: '/finances/expenses/claims/manage',
        },
        component: () => import('@/views/finances/manageExpenseClaims.vue'),
      },
      {
        path: '/finances/transactions',
        name: 'Transaction History',
        meta: {
          title: 'Transaction History',
          restrictTo: ['user'],
          selectNavPath: '/finances/transactions',
        },
        component: () => import('@/views/finances/transactions.vue'),
      },
      {
        path: '/finances/transactions/record',
        name: 'Record Transaction',
        meta: {
          title: 'Record Transaction',
          restrictTo: ['user'],
          selectNavPath: '/finances/transactions/record',
        },
        component: () => import('@/views/finances/recordTransaction.vue'),
      },
      {
        path: '/finances/sales',
        name: 'Sales History',
        meta: {
          title: 'Sales History',
          restrictTo: ['user'],
          selectNavPath: '/finances/sales',
        },
        component: () => import('@/views/sales/index.vue'),
      },
      {
        path: '/point-of-sale',
        name: 'Point of Sale',
        meta: {
          title: 'Point of Sale',
          restrictTo: ['user'],
          selectNavPath: '/point-of-sale',
        },
        component: () => import('@/views/sales/PointOfSale.vue'),
      },
      {
        path: '/admin/users',
        name: 'User Management',
        meta: {
          title: 'User Management',
          restrictTo: ['user'],
          selectNavPath: '/admin/users',
        },
        component: () => import('@/views/admin/userRoles.vue'),
      },
      {
        path: '/admin/clock-in',
        name: 'Clock-In',
        meta: {
          title: 'Clock-In',
          restrictTo: ['user'],
          selectNavPath: '/admin/clock-in',
        },
        component: () => import('@/views/admin/clockIn.vue'),
      },
      {
        path: '/admin/appointment-types',
        name: 'Appointment Types',
        meta: {
          title: 'Appointment Types',
          restrictTo: ['user'],
          selectNavPath: '/admin/appointment-types',
        },
        component: () => import('@/views/admin/appointmentTypes.vue'),
      },
      {
        path: '/admin/appointment-settings',
        name: 'Appointment Settings',
        meta: {
          title: 'Appointment Settings',
          restrictTo: ['user'],
          selectNavPath: '/admin/appointment-settings',
        },
        component: () => import('@/views/admin/appointmentSettings.vue'),
      },
      {
        path: '/admin/raw-data',
        name: 'Raw Data Access',
        meta: {
          title: 'Raw Data Access',
          restrictTo: ['user'],
          selectNavPath: '/admin/raw-data',
        },
        component: () => import('@/views/admin/rawData.vue'),
      },
      {
        path: '/admin/bug-reports',
        name: 'Bug Reports',
        meta: {
          title: 'Bug Reports',
          restrictTo: ['user'],
          selectNavPath: '/admin/bug-reports',
        },
        component: () => import('@/views/admin/bugReports.vue'),
      },
      {
        path: '/admin/basic-settings',
        name: 'Basic Settings',
        meta: {
          title: 'Basic Settings',
          restrictTo: ['user'],
          selectNavPath: '/admin/basic-settings',
        },
        component: () => import('@/views/admin/basicSettings.vue'),
      },
      {
        path: '/contracts/find-paper-contract',
        name: 'Find Paper Contract',
        meta: {
          title: 'Find Paper Contract',
          restrictTo: ['user'],
          selectNavPath: '/contracts/find-paper-contract',
        },
        component: () => import('@/views/contract/findPaperContract.vue'),
      },
      {
        path: '/statistics/users/leaderboard',
        name: 'Volunteer Leaderboard',
        meta: {
          title: 'Volunteer Leaderboard',
          restrictTo: ['user'],
          selectNavPath: '/statistics/users/leaderboard',
        },
        component: () => import('@/views/statistics/userLeaderboard.vue'),
      },
      {
        path: '/statistics/clients/leaderboard',
        name: 'Client Leaderboard',
        meta: {
          title: 'Client Leaderboard',
          restrictTo: ['user'],
          selectNavPath: '/statistics/clients/leaderboard',
        },
        component: () => import('@/views/statistics/clientLeaderboard.vue'),
      },
      {
        path: '/statistics/bikes/leaderboard',
        name: 'Bike Leaderboard',
        meta: {
          title: 'Bike Leaderboard',
          restrictTo: ['user'],
          selectNavPath: '/statistics/bikes/leaderboard',
        },
        component: () => import('@/views/statistics/bikeLeaderboard.vue'),
      },
      {
        path: '/bikes/:bikeId',
        name: 'Bike',
        meta: {
          title: 'Bike',
          restrictTo: ['user'],
          selectNavPath: '/bikes',
        },
        component: () => import('@/views/bike/index.vue'),
      },
      {
        path: '/bikes',
        name: 'Find Bike',
        meta: {
          title: 'Find Bike',
          restrictTo: ['user'],
          selectNavPath: '/bikes',
        },
        component: () => import('@/views/bike/BikeCatalogue.vue'),
      },
      {
        path: '/statistics/contracts',
        name: 'Contract Charts',
        meta: {
          title: 'Contract Charts',
          restrictTo: ['user'],
          selectNavPath: '/statistics/contracts',
        },
        component: () => import('@/views/statistics/contractCharts.vue'),
      },
      {
        path: '/surveys/map',
        name: 'Cycling Suitability Map',
        meta: {
          title: 'Cycling Suitability Map',
          restrictTo: null,
          selectNavPath: '/surveys/map',
        },
        component: () => import('@/views/surveys/cyclingSuitabilityMap.vue'),
      },
      {
        path: '/admin/duplicates/clients',
        name: 'Manage Potential Duplicate Clients',
        meta: {
          title: 'Manage Potential Duplicate Clients',
          restrictTo: ['user'],
          selectNavPath: '/admin/duplicates/clients',
        },
        component: () => import('@/views/admin/duplicates/clients.vue'),
      },
      {
        path: '/admin/duplicates/bikes',
        name: 'Manage Potential Duplicate Bikes',
        meta: {
          title: 'Manage Potential Duplicate Bikes',
          restrictTo: ['user'],
          selectNavPath: '/admin/duplicates/bikes',
        },
        component: () => import('@/views/admin/duplicates/bikes.vue'),
      },
      {
        path: '/admin/user-groups',
        name: 'Manage User Groups',
        meta: {
          title: 'Manage User Groups',
          restrictTo: ['user'],
          selectNavPath: '/admin/user-groups',
        },
        component: () => import('@/views/admin/userGroups.vue'),
      },
      {
        path: '/admin/accounts',
        name: 'Manage Accounts',
        meta: {
          title: 'Manage Accounts',
          restrictTo: ['user'],
          selectNavPath: '/admin/accounts',
        },
        component: () => import('@/views/admin/accounts.vue'),
      },
      {
        path: '/admin/catalogue',
        name: 'Manage Catalogue',
        meta: {
          title: 'Manage Catalogue',
          restrictTo: ['user'],
          selectNavPath: '/admin/catalogue',
        },
        component: () => import('@/views/admin/catalogue.vue'),
      },
      {
        path: '/crimereports',
        name: 'Find Crime Reports',
        meta: {
          title: 'Find Crime Reports',
          restrictTo: ['user'],
          selectNavPath: '/crimereports',
        },
        component: () => import('@/views/crimereports/find.vue'),
      },
    ],
  },
];

export default routes;
