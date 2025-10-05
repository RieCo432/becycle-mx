import {distance} from 'fastest-levenshtein';
import colourSuggestionSort from '@/util/colourSuggestionSort';

export default {
  filterSort(array, input) {
    return new Promise((resolve) => {
      input = input ? input.toLowerCase() : '';
      array = array.map((item) => item ? item.toLowerCase() : '');
      const result = array
        .filter((item) => (
          distance(input, item) <= 4 ||
              item.includes(input)))
        .sort((a, b) =>
          distance(input, a) -
            distance(input, b) -
            (a.includes(input) ? a.length : 0) +
            (b.includes(input) ? b.length : 0));
      resolve(result);
    });
  },
  filterSortObject(array, input, maxDistance) {
    return new Promise((resolve) => {
      const result = array
        .filter((item) => Object.entries(item).map(([prop, _]) => {
          if (
            prop !== 'id' &&
                Object.prototype.hasOwnProperty.call(item, prop) &&
                Object.prototype.hasOwnProperty.call(input, prop)) {
            if (prop !== 'colours') {
              const itemProp = item[prop].toLowerCase();
              const inputProp = input[prop].toLowerCase();
              return inputProp.length === 0 || (
                distance(inputProp, itemProp) <= maxDistance || itemProp.includes(inputProp)
              );
            };
            return true;
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
            if (prop !== 'colours') {
              const inputProp = input[prop].toLowerCase();
              const aProp = a[prop].toLowerCase();
              const bProp = b[prop].toLowerCase();
              return aProp.length > 0 ?
                distance(inputProp, aProp) -
                      distance(inputProp, bProp) -
                      (aProp.includes(inputProp) ? aProp.length : 0) +
                      (bProp.includes(inputProp) ? bProp.length : 0) :
                0;
            } else {
              return colourSuggestionSort.colourSuggestionSort(a[prop], b[prop], input[prop]);
            }
          } else {
            return 0;
          }
        }).reduce((x, y) => x + y, 0));
      resolve(result);
    });
  },
};
