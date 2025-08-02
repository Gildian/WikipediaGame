import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    css: true,
    coverage: {
      reporter: ['text', 'html', 'clover', 'json'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        '**/*{.,-}test.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        '**/*{.,-}spec.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        '**/vite.config.{js,mjs,cjs,ts,mts,cts}',
        '**/vitest.config.{js,mjs,cjs,ts,mts,cts}',
      ]
    }
  }
})
