import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // 配置TinyMCE静态资源
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          tinymce: ['tinymce']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['@tinymce/tinymce-vue', 'tinymce']
  },
  server: {
    host: '0.0.0.0',
    port: 5173
  }
}) 