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
    input = input.toLowerCase();
    array = array.map((item) => item.toLowerCase());
    return array
      .filter((item) => (
        this.distance(input, item) <= 4 ||
            item.includes(input)))
      .sort((a, b) => this.distance(input, a) - this.distance(input, b));
  },
  filterSortClientObject(array, input, maxDistance) {
    const client = {
      firstName: input.firstName.toLowerCase(),
      lastName: input.lastName.toLowerCase(),
      emailAddress: input.emailAddress.toLowerCase(),
    };
    const targetArray = array.map((item) => ({
      firstName: item.firstName.toLowerCase(),
      lastName: item.lastName.toLowerCase(),
      emailAddress: item.emailAddress.toLowerCase(),
    }));
    return targetArray
      .filter((item) => (
        (
          client.firstName.length === 0 ?
            (this.distance(client.firstName, item.firstName) <= maxDistance || item.firstName.includes(client.firstName)) :
            true
        ) &&
        (
          client.lastName.length === 0 ?
            (this.distance(client.lastName, item.lastName) <= maxDistance || item.lastName.includes(client.lastName)) :
            true
        ) &&
        (
          client.emailAddress.length === 0 ?
            (this.distance(client.emailAddress, item.emailAddress) <= maxDistance || item.emailAddress.includes(client.emailAddress)) :
            true
        )
      ))
      .sort((a, b) => (
        (
          (client.firstName.length > 0 ?
            this.distance(client.firstName, a.firstName) - this.distance(client.firstName, b.firstName) :
            0
          ) +
            (client.lastName.length > 0 ?
              this.distance(client.lastName, a.lastName) - this.distance(client.lastName, b.lastName) :
              0
            ) +
            (client.emailAddress.length > 0 ?
              this.distance(client.emailAddress, a.emailAddress) - this.distance(client.emailAddress, b.emailAddress) :
              0)
        )
      ));
  },
};
