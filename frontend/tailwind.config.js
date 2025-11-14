/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#2563eb',
        'secondary-blue': '#1e40af',
        'light-blue': '#dbeafe',
        'accent-blue': '#3b82f6',
        'gradient-start': '#1e3a8a',
        'gradient-end': '#3b82f6'
      },
      backgroundImage: {
        'gradient-blue': 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
        'gradient-subtle': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }
    },
  },
  plugins: [],
}