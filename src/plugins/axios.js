import axios from "axios";
import store from "../store";
import router from "../router/index.js";

const axiosClient = axios.create({
    baseURL: 'http://dashkit-laravel-api/api/'
})

axiosClient.interceptors.request.use(config => {
    config.headers.Authorization = `Bearer ${store.state.user.token}`
    return config;
})

axiosClient.interceptors.response.use(response => {
    return response;
}, error => {
    if (error.response.status === 401) {
        store.commit('setToken', null)
        router.push({name: 'login'})
    }
    throw error;
})

export default axiosClient;