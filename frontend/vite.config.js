import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Стандартный порт Vite
    proxy: {
      // Проксируем запросы с /api на наш Flask-сервер
      '/api': {
        target: 'http://localhost:5000', // Адрес вашего Flask-сервера
        changeOrigin: true, // Необходимо для виртуальных хостов
        // rewrite: (path) => path.replace(/^\/api/, '') // Если нужно убрать /api из пути
      }
    }
  }
})