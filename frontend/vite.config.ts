import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';
// import devtools from 'solid-devtools/vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [
    /* 
    Uncomment the following line to enable solid-devtools.
    For more info see https://github.com/thetarnav/solid-devtools/tree/main/packages/extension#readme
    */
    // devtools(),
    solidPlugin(),
    tsconfigPaths(),
  ],
  server: {
    // If you are trying to access env vars outside your app source code (such as inside vite.config.js), then you have to use loadEnv():
    port: 3000,
  },
  build: {
    target: 'esnext',
  },
});
