module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
    'jest/globals': true,
    'cypress/globals': true
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jest/recommended',
    'plugin:cypress/recommended'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    },
    ecmaVersion: 12,
    sourceType: 'module'
  },
  plugins: [
    'react',
    '@typescript-eslint',
    'jest',
    'cypress'
  ],
  settings: {
    react: {
      version: 'detect'
    }
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { 
      'argsIgnorePattern': '^_',
      'varsIgnorePattern': '^_'
    }],
    'react-refresh/only-export-components': 'warn'
  },
  globals: {
    process: 'readonly',
    module: 'readonly',
    require: 'readonly',
    __dirname: 'readonly',
    console: 'readonly',
    global: 'readonly'
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.test.tsx', '**/*.cy.ts', '**/*.cy.tsx', 'setupTests.ts'],
      env: {
        jest: true,
        'cypress/globals': true
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        'no-undef': 'off'
      }
    }
  ]
}; 