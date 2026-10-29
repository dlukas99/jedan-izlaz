import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages poslužuje stranicu na /jedan-izlaz/; lokalni razvoj (npm run dev) na /.
export default defineConfig(({ command, isPreview }) => ({
  plugins: [react()],
  base: command === 'build' || isPreview ? '/jedan-izlaz/' : '/',
}))
