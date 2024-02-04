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
    showByDefault: true,
    ignoreTags: [],
    showTags: [],
  },
  {
    title: 'Login',
    icon: 'heroicons-outline:login',
    link: '/app/home',
    showByDefault: true,
    ignoreTags: ['clientLoggedIn', 'userLoggedIn'],
    showTags: [],
    child: [
      {
        childtitle: 'Volunteer Login',
        childlink: '/users/login',
        childicon: 'heroicons-outline:login',
        showByDefault: true,
        ignoreTags: [],
        showTags: [],
      },
      {
        childtitle: 'Client Login',
        childlink: '/clients/login',
        childicon: 'heroicons-outline:login',
        showByDefault: true,
        ignoreTags: [],
        showTage: [],
      },
    ],
  },
  {
    title: 'Contracts',
    icon: 'heroicons-outline:clipboard-document-list',
    link: '/contracts',
    showByDefault: false,
    ignoreTags: [],
    showTags: [''],
    child: [
      {
        childtitle: 'New Contract',
        childicon: 'heroicons-outline:document-plus',
        childlink: '/contracts/new',
        ignoreTags: [],
      },
      {
        childtitle: 'Find Contract',
        childicon: 'heroicons-outline:document-magnifying-glass',
        childlink: '/clients/find',
        ignoreTags: [],
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
