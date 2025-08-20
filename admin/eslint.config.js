import js from "@eslint/js"
import globals from "globals"
import { defineConfig, globalIgnores } from "eslint/config"
import react from "eslint-plugin-react"

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs}"],
    plugins: { js, react },
    extends: ["js/recommended"],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: { ...globals.browser },
    },
    rules: {
      "react/jsx-uses-vars": "error",
      "react/jsx-uses-react": "error",
    },
  },
  globalIgnores(["dist"]),
])
