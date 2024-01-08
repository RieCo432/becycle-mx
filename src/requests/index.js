import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {'Authorization': 'Bearer ' + localStorage.token},
});

export default {
  getOpeningTimes() {
    return axiosClient.get('/public/opening-hours');
  },
  getUserToken(username, password) {
    return axiosClient.post('/users/token', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  getUserMe() {
    return axiosClient.get('/users/me');
  },
};
