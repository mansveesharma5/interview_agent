import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {

      '/api': {
        target: 'https://interviewagent-production-ac57.up.railway.app/',
        changeOrigin: true,

        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})