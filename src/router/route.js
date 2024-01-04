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
    ],
  },
];

export default routes;
