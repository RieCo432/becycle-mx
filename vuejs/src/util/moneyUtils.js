export default {
  moneyFormatter: (val) => (`\u00A3 ${(val / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`),
}