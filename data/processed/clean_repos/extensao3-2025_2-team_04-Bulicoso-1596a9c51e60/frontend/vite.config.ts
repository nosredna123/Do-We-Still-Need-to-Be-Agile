import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: 'motion/react', replacement: 'framer-motion' },
      // Map imports like `figma:asset/xxxxx.png` -> ./ParteParaIntegrar/.../assets/xxxxx.png
      { find: /^figma:asset\/(.*)/, replacement: fileURLToPath(new URL('./ParteParaIntegrar/HomeLoguin/HomeAndPage/src/assets/$1', import.meta.url)) }
    ]
  }
})
