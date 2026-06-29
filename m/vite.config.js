import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

// For APK builds: run with BUILD_TARGET=app to use relative base
const isAppBuild = process.env.BUILD_TARGET === 'app'

export default defineConfig({
  plugins: [uni()],
  base: isAppBuild ? './' : '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
