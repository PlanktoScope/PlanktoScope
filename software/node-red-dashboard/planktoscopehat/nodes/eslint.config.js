import js from "@eslint/js"
import globals from "globals"
import { defineConfig } from "eslint/config"
import html from "eslint-plugin-html"

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,html}"],
    plugins: { js },
    extends: ["js/recommended"],
  },
  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: { globals: { ...globals.node } },
  },
  {
    files: ["**/*.html"],
    plugins: { html },
    languageOptions: { globals: { ...globals.browser, RED: true } },
  },
])
