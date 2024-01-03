export default {
  data() {
    return {
      window: {
        width: 0,
        height: 0,
      },
    };
  },
  methods: {
    handleResize() {
      this.window.width = window.innerWidth;
    },
  },
  created() {
    window.addEventListener("resize", this.handleResize);
    this.handleResize();
  },
  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  },
};
