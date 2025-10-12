/* eslint new-cap: 0 */

import {defineConfig} from 'vite';
import path from 'path';
import Vue from '@vitejs/plugin-vue';
import ViteImages from 'vite-plugin-vue-images';
import dotenv from 'dotenv';
import mkcert from 'vite-plugin-mkcert';

// https://vitejs.dev/config/
export default defineConfig(() => {
  dotenv.config();
  return {
    css: {
      preprocessorOptions: {
        sass: {
          api: 'modern-compiler',
        },
      },
    },
    server: {https: false}, // set to true for NFC development
    plugins: [
      Vue(),
      ViteImages({
        dirs: ['src/assets/images'],
      }),
      // mkcert(), // this is required for NFC development
    ],
    resolve: {
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue', '.css'],
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  };
});
