import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    svelte({
      // Note: we don't need sveltePreprocess here as Vite handles it
    }),
  ],
  css: {
    postcss: './postcss.config.js',
  },
});
