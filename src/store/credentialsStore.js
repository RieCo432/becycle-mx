import {defineStore} from 'pinia';

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
    },
    setName(name) {
      this.name = name;
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
    getApiRequestHeader() {
      if (this.token !== null) {
        return {'Authorization': 'Bearer ' + localStorage.getItem('token')};
      } else {
        return {};
      }
    },
    isUserLoggedIn() {
      return this.tokenType === 'user';
    },
    isClientLoggedin() {
      return this.tokenType === 'client';
    },
    isLoggedIn() {
      return this.token !== null;
    },
    getTokenType() {
      return this.isLoggedIn() ? this.tokenType : null;
    },
  },
});
