import vue from 'eslint-plugin-vue';
import globals from 'globals';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import js from '@eslint/js';
import {FlatCompat} from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [...compat.extends('google', 'plugin:vue/vue3-essential'), {
  plugins: {
    vue,
  },

  languageOptions: {
    globals: {
      ...globals.browser,
    },

    ecmaVersion: 'latest',
    sourceType: 'module',
  },

  rules: {
    'linebreak-style': ['off', 'unix'],
    'indent': ['error', 2],
    'require-jsdoc': 'off',
    'valid-jsdoc': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/multi-word-component-names': 'off',
    'max-len': ['error', {
      code: 140,
    }],
  },
}, {
  files: ['**/.eslintrc.{js,cjs}'],

  languageOptions: {
    globals: {
      ...globals.node,
    },

    ecmaVersion: 5,
    sourceType: 'commonjs',
  },
}];
