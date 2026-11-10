import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/classification': 'http://127.0.0.1:8001',
      '/chat': 'http://127.0.0.1:8000',
      '/analytics': 'http://127.0.0.1:8002',
      '/health/assistant': { target: 'http://127.0.0.1:8000', rewrite: () => '/health' },
      '/health/classification': { target: 'http://127.0.0.1:8001', rewrite: () => '/health' },
      '/health/analytics': { target: 'http://127.0.0.1:8002', rewrite: () => '/health' },
    },
  },
})
