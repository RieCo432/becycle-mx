export default {
  colourSuggestionSort(a, b, selection) {
    {
      const aHex = a.map((c) => c.hex);
      const bHex = b.map((c) => c.hex);
      const selectedHex = selection.map((c) => c.hex);
      const aContainsSelected = aHex.map((c) => selectedHex.includes(c) ? 1 : -0.5);
      const bContainsSelected = bHex.map((c) => selectedHex.includes(c) ? 1 : -0.5);
      const aScore = aContainsSelected.reduce((a, b) => a + b, 0);
      const bScore = bContainsSelected.reduce((a, b) => a + b, 0);
      if (aScore > bScore) return -1;
      if (aScore < bScore) return 1;
      return 0;
    }
  },
};
