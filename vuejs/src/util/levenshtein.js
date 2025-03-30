export default {
  distance(string1, string2) {
    if (!string1.length) return string2.length;
    if (!string2.length) return string1.length;
    const arr = [];
    for (let i = 0; i <= string2.length; i++) {
      arr[i] = [i];
      for (let j = 1; j <= string1.length; j++) {
        arr[i][j] = i === 0 ?
          j :
          Math.min(
            arr[i - 1][j] + 1,
            arr[i][j - 1] + 1,
            arr[i - 1][j - 1] + (string1[j - 1] === string2[i - 1] ? 0 : 1),
          );
      }
    }
    return arr[string2.length][string1.length];
  },
  filterSort(array, input) {
    input = input ? input.toLowerCase() : '';
    array = array.map((item) => item ? item.toLowerCase() : '');
    return array
      .filter((item) => (
        this.distance(input, item) <= 4 ||
            item.includes(input)))
      .sort((a, b) => this.distance(input, a) - this.distance(input, b));
  },
  filterSortObject(array, input, maxDistance) {
    return array
      .filter((item) => Object.entries(item).map(([prop, _]) => {
        if (
          prop !== 'id' &&
            Object.prototype.hasOwnProperty.call(item, prop) &&
            Object.prototype.hasOwnProperty.call(input, prop)) {
          const itemProp = item[prop].toLowerCase();
          const inputProp = input[prop].toLowerCase();
          const result = inputProp.length === 0 || (
            this.distance(inputProp, itemProp) <= maxDistance || itemProp.includes(inputProp)
          );
          console.log(itemProp, inputProp, result);
          return result;
        } else {
          return true;
        }
      }).reduce((acc, item) => acc && item), true)
      .sort((a, b) => Object.entries(a).map(([prop, _]) => {
        if (
          prop !== 'id' &&
            Object.prototype.hasOwnProperty.call(a, prop) &&
            Object.prototype.hasOwnProperty.call(b, prop) &&
            Object.prototype.hasOwnProperty.call(input, prop)
        ) {
          console.log(prop);
          const inputProp = input[prop].toLowerCase();
          const aProp = a[prop].toLowerCase();
          const bProp = b[prop].toLowerCase();
          return aProp.length > 0 ?
            this.distance(inputProp, aProp) -
              this.distance(inputProp, bProp) -
              (aProp.includes(inputProp) ? aProp.length : 0) +
              (bProp.includes(inputProp) ? bProp.length : 0) :
            0;
        } else {
          return 0;
        }
      }).reduce((x, y) => x + y, 0));
  },
};
