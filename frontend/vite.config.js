import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Importante: Permite conexiones desde fuera del contenedor
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true // Necesario para hot-reload en Docker
    }
  }
})
