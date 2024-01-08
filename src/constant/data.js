export const menuItems = [
  {
    isHeader: true,
    title: 'menu',
  },
  {
    title: 'Dashboard',
    icon: 'heroicons-outline:home',
    link: 'home',
  },
];
// menuseetins

export const ProfileMenu = [
  {
    label: 'Profile',
    icon: 'heroicons-outline:user',
    link: '/user/me',
  },
  {
    label: 'Settings',
    icon: 'heroicons-outline:cog',
    link: '#',
  },
  {
    label: 'Logout',
    icon: 'heroicons-outline:login',
    link: '/',
  },
];

export const topMenu = [
  {
    isHeader: true,
    title: 'DASHBOARD',
  },
  {
    title: 'Home',
    icon: 'heroicons-outline:home',
    link: '/app/home',
  },
  {
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
  },
  {
    title: 'Pages',
    icon: 'heroicons-outline:view-boards',
    link: '/app/home',
    megamenu: [
      {
        megamenutitle: 'Authentication',
        megamenuicon: 'heroicons-outline:user',
        singleMegamenu: [
          {
            m_childtitle: 'User Login',
            m_childlink: '/login/user',
          },
          {
            m_childtitle: 'Signin Two',
            m_childlink: '/login2',
          },
        ],
      },

      {
        megamenutitle: 'Components',
        megamenuicon: 'heroicons-outline:user',
        singleMegamenu: [
          {
            m_childtitle: 'colors',
            m_childlink: 'colors',
          },
        ],
      },
      {
        megamenutitle: 'Forms',
        megamenuicon: 'heroicons-outline:user',
        singleMegamenu: [
          {
            m_childtitle: 'Radio button',
            m_childlink: 'radio-button',
          },
          {
            m_childtitle: 'Switch',
            m_childlink: 'switch',
          },
        ],
      },
      {
        megamenutitle: 'Utility',
        megamenuicon: 'heroicons-outline:user',
        singleMegamenu: [
          {
            m_childtitle: 'Coming Soon',
            m_childlink: '/coming-soon',
          },
          {
            m_childtitle: 'Under Maintanance page',
            m_childlink: '/under-construction',
          },
        ],
      },
    ],
  },

  {
    isHeader: true,
    title: 'PAGES',
  },
  {
    title: 'Widgets',
    icon: 'heroicons-outline:view-grid-add',
    link: 'form-elements',
    child: [
      {
        childtitle: 'Basic',
        childlink: 'basic',
        childicon: 'heroicons-outline:document-text',
      },
      {
        childtitle: 'Statistic',
        childlink: 'statistic',
        childicon: 'heroicons-outline:document-text',
      },
    ],
  },

  {
    title: 'Extra',
    icon: 'heroicons-outline:template',

    child: [
      {
        childtitle: 'Chart js',
        childlink: 'chartjs',
        childicon: 'heroicons-outline:chart-bar',
      },
      {
        childtitle: 'Map',
        childlink: 'map',
        childicon: 'heroicons-outline:map',
      },
    ],
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
