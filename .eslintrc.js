module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    "plugin:vue/vue3-essential",
    "eslint:recommended",
    "plugin:prettier/recommended",
  ],
  parserOptions: {
    parser: "@babel/eslint-parser",
  },
  rules: {
    "no-console": import.meta.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": import.meta.NODE_ENV === "production" ? "warn" : "off",
    "vue/multi-word-component-names": 0,

    "prettier/prettier": [
      "error",
      {
        endOfLine: "auto",
      },
    ],
  },
};
