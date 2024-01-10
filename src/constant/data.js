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
  },
  /* {
    title: 'App',
    icon: 'heroicons-outline:chip',
    link: '/app/home',
    child: [
      {
        childtitle: 'Projects',
        childlink: 'projects',
        childicon: 'heroicons-outline:document',
      },
    ],
  },*/
  {
    title: 'Login',
    icon: 'heroicons-outline:login',
    link: '/app/home',
    child: [
      {
        childtitle: 'Volunteer Login',
        childlink: '/login/user',
        childicon: 'heroicons-outline:login',
      },
      {
        childtitle: 'Client Login',
        childlink: '/login/client',
        childicon: 'heroicons-outline:login',
      },
    ],
  },
  {
    title: 'Contracts',
    icon: 'heroicons-outline:clipboard-document-list',
    link: '/contracts',
    child: [
      {
        childtitle: 'New Contract',
        childicon: 'heroicons-outline:document-plus',
        childlink: '/contracts/new',
      },
    ],
  },
  // {
  //   title: 'Widgets',
  //   icon: 'heroicons-outline:view-grid-add',
  //   link: 'form-elements',
  //   child: [
  //     {
  //       childtitle: 'Basic',
  //       childlink: 'basic',
  //       childicon: 'heroicons-outline:document-text',
  //     },
  //     {
  //       childtitle: 'Statistic',
  //       childlink: 'statistic',
  //       childicon: 'heroicons-outline:document-text',
  //     },
  //   ],
  // },
  //
  // {
  //   title: 'Extra',
  //   icon: 'heroicons-outline:template',
  //
  //   child: [
  //     {
  //       childtitle: 'Chart js',
  //       childlink: 'chartjs',
  //       childicon: 'heroicons-outline:chart-bar',
  //     },
  //     {
  //       childtitle: 'Map',
  //       childlink: 'map',
  //       childicon: 'heroicons-outline:map',
  //     },
  //   ],
  // },
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
