import axiosClient from '@/plugins/axios';

function getOpeningTimes() {
  axiosClient.get('http://localhost:8000/public/opening-times')
      .then((response) => (console.log(response.data)));
}

export default getOpeningTimes;
