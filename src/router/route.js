const routes = [
  {
    path: '/',
    name: 'Layout',
    redirect: '/home',
    meta: {restrictTo: null},
    component: () => import('@/Layout/index.vue'),
    children: [
      {
        path: '/home',
        name: 'home',
        meta: {restrictTo: null},
        component: () => import('@/views/home.vue'),
      },
      {
        path: '/me',
        name: 'Profile',
        meta: {restrictTo: ['client', 'user']},
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
        meta: {restrictTo: null},
        component: () => import('@/views/template.vue'),
      },
      {
        path: '/users/login',
        name: 'Volunteer Login',
        meta: {restrictTo: null},
        component: () => import('@/views/login/user.vue'),
      },
      {
        path: '/clients/login',
        name: 'Client Login',
        meta: {restrictTo: null},
        component: () => import('@/views/login/client.vue'),
      },
      {
        path: '/users/me',
        name: 'User',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/user/me.vue'),
      },
      {
        path: '/clients/me',
        name: 'Me',
        meta: {restrictTo: ['client']},
        component: () => import('@/views/client/me.vue'),
      },
      {
        path: '/clients/:clientId',
        name: 'Client',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/client/index.vue'),
      },
      {
        path: '/clients/me/contracts/:contractId',
        name: 'Me',
        meta: {restrictTo: ['client']},
        component: () => import('@/views/contract/clientIndex.vue'),
      },
      {
        path: '/contracts/:contractId',
        name: 'Contract',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/contract/index.vue'),

      },
      {
        path: '/contracts/new',
        name: 'New Contract',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/contract/newContract.vue'),
      },
      {
        path: '/clients/find',
        name: 'Find Client',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/client/findClient.vue'),
      },
      {
        path: '/appointments/book',
        name: 'Book Appointment',
        meta: {restrictTo: ['client']},
        component: () => import('@/views/appointments/bookAppointment.vue'),
      },
      {
        path: '/appointments',
        name: 'Appointment Calendar',
        meta: {restrictTo: ['user']},
        component: () => import('@/views/appointments/index.vue'),
      },
    ],
  },
];

export default routes;
