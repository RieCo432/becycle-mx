import {createRouter, createWebHistory} from 'vue-router';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useToast} from 'vue-toastification';

import routes from './route';
const toast = useToast();

const router = createRouter({
  history: createWebHistory(import.meta.BASE_URL),
  base: import.meta.BASE_URL,
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return {top: 0};
    }
  },
});
router.beforeEach((to, from, next) => {
  const credentialsStore = useCredentialsStore();
  const titleText = to.name;
  const words = titleText.split(' ');
  const wordslength = words.length;
  for (let i = 0; i < wordslength; i++) {
    words[i] = words[i][0].toUpperCase() + words[i].substring(1);
  }

  document.title = 'beCyCle  - ' + words;

  if (to.meta.restrictTo == null) {
    next();
  } else {
    if (to.meta.restrictTo.includes(credentialsStore.getTokenType())) {
      next();
    } else if (to.meta.restrictTo.includes('client')) {
      toast.warning('You need to register/login to access Appointment Booking', {timeout: 4000});
      next({path: '/clients/login', query: {nextUrl: to.path}});
    } else {
      next({path: '/home'});
    }
  }
});

router.afterEach(() => {
  // Remove initial loading
  const appLoading = document.getElementById('loading-bg');
  if (appLoading) {
    appLoading.style.display = 'none';
  }
});

export default router;
