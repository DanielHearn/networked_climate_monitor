module.exports = {
  root: true,
  env: {
    browser: true
  },
  extends: ['plugin:vue/essential', '@vue/prettier', 'prettier/standard'],
  plugins: ['prettier'],
  rules: {
    indent: 0,
    'no-tabs': 0,
    'eol-last': 'off',
    'no-console': 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 2 : 0,
    'no-process-env': 'off',
    semi: ['error', 'never'],
    quotes: ['error', 'single'],
    'prettier/prettier': [
      'warn',
      {
        singleQuote: true,
        semi: false,
        trailingComma: 'none'
      }
    ]
  },
  parserOptions: {
    parser: 'babel-eslint',
    sourceType: 'module'
  },
  overrides: [
    {
      files: [
        '**/__tests__/*.{j,t}s?(x)',
        '**/tests/unit/**/*.spec.{j,t}s?(x)'
      ],
      env: {
        jest: true
      }
    }
  ]
}
