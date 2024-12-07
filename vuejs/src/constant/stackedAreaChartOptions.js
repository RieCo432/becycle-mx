export default {
  chart: {
    type: 'area',
    height: 300,
    stacked: true,
  },
  theme: {
    mode: 'light',
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: 'smooth',
  },
  fill: {
    type: 'gradient',
    gradient: {
      opacityFrom: 0.6,
      opacityTo: 0.8,
    },
  },
  legend: {
    position: 'top',
    horizontalAlign: 'left',
    labels: {
      colors: ['#fffff'],
    },
  },
  tooltip: {
    theme: 'dark',
  },
  xaxis: {
    show: true,
    type: 'datetime',
    labels: {
      style: {
        color: '#ffffff',
      },
    },
    axisTicks: {
      color: '#ffffff',
    },
  },
  yaxis: {
    show: true,
    labels: {
      style: {
        color: '#ffffff',
      },
    },
    axisTicks: {
      color: '#ffffff',
    },
  },
};
