import { defineConfig } from "vite";
import path from "path";
import Vue from "@vitejs/plugin-vue";
import ViteImages from "vite-plugin-vue-images";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Vue(),
    ViteImages({
      dirs: ["src/assets/images"],
    }),
  ],
  resolve: {
    extensions: [".mjs", ".js", ".ts", ".jsx", ".tsx", ".json", ".vue", ".css"],
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
