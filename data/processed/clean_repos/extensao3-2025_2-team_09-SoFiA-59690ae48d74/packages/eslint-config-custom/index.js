module.exports = {
  extends: [
    "eslint:recommended",
    "turbo",
    "next",
    "plugin:@typescript-eslint/recommended",
    "prettier",
  ],
  plugins: [
    "@typescript-eslint",
    "prettier",
  ],
  rules: {
    "@next/next/no-html-link-for-pages": "off",
    "prettier/prettier": "error",
    "arrow-body-style": "off",
    "prefer-arrow-callback": "off",
  },
  parserOptions: {
    babelOptions: {
      presets: [require.resolve("next/babel")],
    },
  },
};
