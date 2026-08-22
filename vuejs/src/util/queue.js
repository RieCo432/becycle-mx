class Queue extends Array {
    constructor() {
        super();
    }

    enqueue(element) {
        this.push(element);
    }

    dequeue() {
        return this.isEmpty() ? null : this.shift();
    }

    peek() {
        return this.isEmpty() ? null : this[0];
    }

    isEmpty() {
        return this.length === 0;
    }

    size() {
        return this.length;
    }
}

export default Queue;