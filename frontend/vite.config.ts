import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue(), vueJsx(), vueDevTools()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    // Escucha en todas las interfaces para soportar subdominios (demo.localhost, admin.localhost)
    host: true,
    allowedHosts: [
      'admin.techhive-ec.com',
    ],
    proxy: {
      '/api': {
        target: 'http://techhive_backend:8000',
        changeOrigin: false,
        ws: true,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            // Reenvía el host real del browser, reemplazando el puerto de Vite con el de Django
            const incomingHost = req.headers['host'] || 'techhive_frontend:5173'
            const backendHost = incomingHost.replace(/:\d+$/, ':8000')
            proxyReq.setHeader('Host', backendHost)
          })
        },
      },
    },
  },
})
