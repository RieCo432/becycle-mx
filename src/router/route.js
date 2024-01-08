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
        path: '/user/me',
        name: 'Me',
        component: () => import ('@/views/user/me.vue'),
      },
    ],
  },
];

export default routes;
