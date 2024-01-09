const routes = [
  {
    path: '/',
    name: 'Layout',
    redirect: '/home',
    component: () => import('@/Layout/index.vue'),
    children: [
      {
        path: '/home',
        name: 'home',
        component: () => import('@/views/home.vue'),
      },
      {
        path: '/me',
        name: 'Profile',
        component: () => {
          if (localStorage.getItem('tokenType') === 'user') {
            return import('@/views/user/me.vue');
          } else if (localStorage.getItem('tokenType') === 'client') {
            return import('@/views/client/me.vue');
          } else {
            return import('@/views/home.vue');
          }
        },
      },
      {
        path: '/template',
        name: 'template',
        component: () => import('@/views/template.vue'),
      },
      {
        path: '/login/user',
        name: 'Volunteer Login',
        component: () => import('@/views/login/user.vue'),
      },
      {
        path: '/login/client',
        name: 'Client Login',
        component: () => import('@/views/login/client.vue'),
      },
      {
        path: '/user/me',
        name: 'Me',
        component: () => import('@/views/user/me.vue'),
      },
      {
        path: '/client/me',
        name: 'Me',
        component: () => import('@/views/client/me.vue'),
      },
    ],
  },
];

export default routes;
