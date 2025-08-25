import os from "node:os"
import { defineConfig } from "vite"
import solidPlugin from "vite-plugin-solid"
import Pages from "vite-plugin-pages"

export default defineConfig({
  plugins: [
    Pages({
      dirs: ["src/pages"],
    }),
    solidPlugin(),
  ],
  server: {
    port: 3000,
    allowedHosts: [
      os.hostname(),
      `${os.hostname()}.local`,
      "pkscope.local",
      "planktoscope.local",
      "home.pkscope",
      "192.168.4.1",
    ],
  },
  build: {
    target: "esnext",
    rollupOptions: {
      external: [/^\/home\/pi\/PlanktoScope\/lib\/.*/],
    },
  },
})
