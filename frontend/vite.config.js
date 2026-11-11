import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const assistant = process.env.ASSISTANT_URL ?? 'http://127.0.0.1:8000'
const classification = process.env.CLASSIFICATION_URL ?? 'http://127.0.0.1:8001'
const analytics = process.env.ANALYTICS_URL ?? 'http://127.0.0.1:8002'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/classification': classification,
      '/chat': assistant,
      '/analytics': analytics,
      '/health/assistant': { target: assistant, rewrite: () => '/health' },
      '/health/classification': { target: classification, rewrite: () => '/health' },
      '/health/analytics': { target: analytics, rewrite: () => '/health' },
    },
  },
})
