export const ProfileMenu = [
  {
    label: 'Profile',
    icon: 'heroicons-outline:user',
    link: '/me',
  },
  {
    label: 'Settings',
    icon: 'heroicons-outline:cog',
    link: '#',
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
        childtitle: 'Client Login',
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
    show: ['client'],
  },
  {
    title: 'Contracts',
    icon: 'heroicons-outline:clipboard-document-list',
    link: '/contracts',
    show: ['user'],
    child: [
      {
        childtitle: 'New Contract',
        childicon: 'heroicons-outline:document-plus',
        childlink: '/contracts/new',
        show: ['user'],
      },
      {
        childtitle: 'Find Contract',
        childicon: 'heroicons-outline:document-magnifying-glass',
        childlink: '/clients/find',
        show: ['user'],
      },
    ],
  },
  {
    title: 'Appointments',
    icon: 'heroicons-outline:calendar',
    link: '/appointments',
    show: ['user'],
  },
];

export const alertType = [
  {
    type: 'dark',
  },
  {
    type: 'primary',
  },
  {
    type: 'secondary',
  },
  {
    type: 'success',
  },
  {
    type: 'info',
  },
  {
    type: 'danger',
  },
  {
    type: 'warning',
  },
];
