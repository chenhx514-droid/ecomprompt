/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        accent: '#f59e0b',
        surface: '#1e1b4b',
        card: '#312e81'
      }
    }
  },
  plugins: []
}
