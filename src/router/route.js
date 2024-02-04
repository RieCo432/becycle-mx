// import {useCredentialsStore} from '@/store/credentialsStore';

// function checkUserLoggedIn(to) {
//   const router = useRouter();
//   const credentialsStore = useCredentialsStore();
//   if (credentialsStore.isUserLoggedIn()) {
//     return true;
//   } else {
//     router.push('/login/user');
//   }
// }

const routes = [
  {
    path: '/',
    name: 'Layout',
    redirect: '/home',
    restrictTo: null,
    component: () => import('@/Layout/index.vue'),
    children: [
      {
        path: '/home',
        name: 'home',
        restrictTo: null,
        component: () => import('@/views/home.vue'),
      },
      {
        path: '/me',
        name: 'Profile',
        restrictTo: ['client', 'user'],
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
        restrictTo: null,
        component: () => import('@/views/template.vue'),
      },
      {
        path: '/users/login',
        name: 'Volunteer Login',
        restrictTo: null,
        component: () => import('@/views/login/user.vue'),
      },
      {
        path: '/clients/login',
        name: 'Client Login',
        restrictTo: null,
        component: () => import('@/views/login/client.vue'),
      },
      {
        path: '/users/me',
        name: 'User',
        restrictTo: ['user'],
        component: () => import('@/views/user/me.vue'),
      },
      {
        path: '/clients/:clientId',
        name: 'Client',
        restrictTo: ['user'],
        component: () => import('@/views/client/clientView.vue'),
      },
      {
        path: '/clients/me',
        name: 'Me',
        restrictTo: ['user'],
        component: () => import('@/views/client/me.vue'),
      },
      {
        path: '/contracts/:contractId',
        name: 'Contract',
        restrictTo: ['user'],
        component: () => import('@/views/contract/viewContract.vue'),
        children: [

        ],
      },
      {
        path: '/contracts/new',
        name: 'New Contract',
        restrictTo: ['user'],
        component: () => import('@/views/contract/newContract.vue'),
      },
      {
        path: '/clients/find',
        name: 'Find Client',
        restrictTo: ['user'],
        component: () => import('@/views/client/findClient.vue'),
      },
    ],
  },
];

export default routes;
