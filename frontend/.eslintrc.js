module.exports = {
  env: {
    node: true,
  },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:solid/recommended',
  ],
  plugins: ['@typescript-eslint', 'solid'],
  rules: {
    semi: ['error', 'always'],
    'prefer-const': 'error',
    'no-console': ['error', { allow: ['warn', 'error'] }], // Disallow console.log but allow console.warn and console.error
  },
  ignorePatterns: [
    'node_modules/',
    'dist/',
    'build/',
    'coverage/',
    '*.config.js',
    'frontend/.eslint.js',
  ],
  settings: {
    'eslint.workingDirectories': ['src/', 'lib/', 'test/'],
  },
  overrides: [
    {
      files: ['src/**/*.ts', 'src/**/*.tsx'],
      rules: {},
    },
  ],
};
