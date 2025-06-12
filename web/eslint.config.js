import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';
import eslintPluginPrettier from 'eslint-plugin-prettier';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),

  {
    plugins: {
      prettier: eslintPluginPrettier,
    },
    rules: {
      // Prettier
      'prettier/prettier': 'warn',

      // Disable React hooks exhaustive deps warnings
      'react-hooks/exhaustive-deps': 'off',

      // Disable Next.js img element warnings
      '@next/next/no-img-element': 'off',

      // Disable TypeScript unused variables errors
      '@typescript-eslint/no-unused-vars': 'off',

      // Disable TypeScript explicit any warnings
      '@typescript-eslint/no-explicit-any': 'off',

      // Disable TypeScript ban-ts-comment errors
      '@typescript-eslint/ban-ts-comment': 'off',

      // Disable JSX a11y alt-text warnings
      'jsx-a11y/alt-text': 'off',

      // Disable React hooks exhaustive deps warnings
      'react-hooks/exhaustive-deps': 'off',
      'react/no-unescaped-entities': 'off',
    },
  },
];
