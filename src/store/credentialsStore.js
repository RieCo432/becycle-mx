import {defineStore} from 'pinia';
import requests from '@/requests';

export const useCredentialsStore = defineStore('credentialsStore', {
  state: () => ({
    token: localStorage.getItem('token'),
    tokenType: localStorage.getItem('tokenType'),
    name: localStorage.getItem('name'),
  }),
  actions: {
    login(token, tokenType) {
      this.token = token;
      this.tokenType = tokenType;

      localStorage.setItem('token', this.token);
      localStorage.setItem('tokenType', this.tokenType);

      if (tokenType === 'user') {
        requests.getUserMe().then((response) => (
          this.name = response.data['username']));
      } else if (tokenType === 'client') {
        requests.getClientMe().then((response) => (
          this.name = response.data['firstName'] + ' ' + response.data['lastName']
        ));
      }

      localStorage.setItem('name', this.name);
    },
    logout() {
      this.token = null;
      this.tokenType = null;
      this.name = null;

      localStorage.removeItem('token');
      localStorage.removeItem('tokenType');
      localStorage.removeItem('name');
    },
  },
});
