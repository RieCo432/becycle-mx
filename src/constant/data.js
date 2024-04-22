export const ProfileMenu = [
  {
    label: 'Profile',
    icon: 'heroicons-outline:user',
    link: '/me',
  },
];

export const topMenu = [
  {
    title: 'Home',
    icon: 'heroicons-outline:home',
    link: '/home',
    show: ['always'],

  },
  {
    title: 'Login',
    icon: 'heroicons-outline:login',
    link: '/app/home',
    ignoreTags: ['clientLoggedIn', 'userLoggedIn'],
    show: ['loggedout'],
    child: [
      {
        childtitle: 'Volunteer Login',
        childlink: '/users/login',
        childicon: 'heroicons-outline:login',
        show: ['loggedout'],
      },
      {
        childtitle: 'Client Register/Login',
        childlink: '/clients/login',
        childicon: 'heroicons-outline:login',
        show: ['loggedout'],
      },
    ],
  },
  {
    title: 'Book Appointment',
    icon: 'heroicons-outline:calendar',
    link: '/appointments/book',
    show: ['client', 'loggedout'],
  },
  {
    title: 'New Contract',
    icon: 'heroicons-outline:document-plus',
    link: '/contracts/new',
    show: ['user'],
  },
  {
    title: 'Find Client',
    icon: 'heroicons-outline:document-magnifying-glass',
    link: '/clients',
    show: ['user'],
  },
  {
    title: 'Find Bike',
    icon: 'heroicons-outline:magnifying-glass',
    link: '/bikes',
    show: ['user'],
  },
  {
    title: 'Deposit Accounting',
    icon: 'heroicons-outline:banknotes',
    link: '/accounting/deposits',
    show: ['user'],
  },
  {
    title: 'Deposit Charts',
    icon: 'heroicons-outline:presentation-chart-line',
    link: '/accounting/deposit-charts',
    show: ['user'],
  },
  {
    title: 'Appointments',
    icon: 'heroicons-outline:calendar',
    link: '/appointments',
    show: ['user'],
  },
  {
    title: 'Submit Deposit Exchange',
    icon: 'heroicons-outline:arrows-right-left',
    link: '/admin/deposit-exchanges',
    show: ['user'],
  },
  {
    title: 'Find Paper Contract',
    icon: 'heroicons-outline:clipboard-document-list',
    link: '/contracts/find-paper-contract',
    show: ['user'],
  },
  {
    title: 'Leaderboards',
    icon: 'heroicons-outline:chart-bar',
    link: '/statistics/',
    show: ['user'],
    child: [
      {
        childtitle: 'Volunteer Leaderboard',
        childicon: 'heroicons-outline:chart-bar',
        childlink: '/statistics/users/leaderboard',
        show: ['user'],
      },
      {
        childtitle: 'Bike Leaderboard',
        childicon: 'heroicons-outline:chart-bar',
        childlink: '/statistics/bikes/leaderboard',
        show: ['user'],
      },
      {
        childtitle: 'Client Leaderboard',
        childicon: 'heroicons-outline:chart-bar',
        childlink: '/statistics/clients/leaderboard',
        show: ['user'],
      },
    ],
  },
  {
    title: 'Contract Charts',
    icon: 'heroicons-outline:presentation-chart-line',
    link: '/statistics/contracts',
    show: ['user'],
  },
  /* {
    title: 'Surveys',
    icon: 'heroicons-outline:chart-bar',
    link: '/surveys/',
    show: ['client'],
    child: [
      {
        childtitle: 'Pre-Becycle Survey',
        childicon: 'heroicons-outline:chart-bar',
        childlink: '/surveys/pre-becycle',
        show: ['client'],
      },
    ],
  },*/
  {
    title: 'Admin',
    icon: 'heroicons-outline:building-library',
    link: '/admin/',
    show: ['user'],
    child: [
      {
        childtitle: 'Basic Settings',
        childicon: 'heroicons-outline:cog-6-tooth',
        childlink: '/admin/basic-settings',
        show: ['user'],
      },
      {
        childtitle: 'User Management',
        childicon: 'heroicons-outline:user',
        childlink: '/admin/users',
        show: ['user'],
      },
      {
        childtitle: 'Appointment Types',
        childicon: 'heroicons-outline:calendar',
        childlink: '/admin/appointment-types',
        show: ['user'],
      },
      {
        childtitle: 'Appointment Settings',
        childicon: 'heroicons-outline:adjustments-horizontal',
        childlink: '/admin/appointment-settings',
        show: ['user'],
      },
      {
        childtitle: 'Duplicate Clients',
        childicon: 'heroicons-outline:users',
        childlink: '/admin/duplicates/clients',
        show: ['user'],
      },
      {
        childtitle: 'Duplicate Bikes',
        childicon: 'heroicons-outline:truck',
        childlink: '/admin/duplicates/bikes',
        show: ['user'],
      },
      {
        childtitle: 'Raw Data Access',
        childicon: 'heroicons-outline:circle-stack',
        childlink: '/admin/raw-data',
        show: ['user'],
      },
    ],
  },
];
