import js from "@eslint/js"
import globals from "globals"
import { defineConfig } from "eslint/config"
import nodePlugin from "eslint-plugin-n"

export default defineConfig([
  nodePlugin.configs["flat/recommended-script"],
  {
    files: ["**/*.{js,mjs,cjs}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: { sourceType: "module", globals: { ...globals.node } },
    ignores: ["dist"],
    rules: {
      "n/no-top-level-await": "error",
      "n/no-unsupported-features/node-builtins": [
        "error",
        { allowExperimental: true },
      ],
    },
  },
])
