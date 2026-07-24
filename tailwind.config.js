/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./static/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#f0f5ff',
          100: '#e0ebff',
          400: '#7b8ff7',
          500: '#4f6ef7',
          600: '#3b54e0',
          700: '#2b3fc7',
        },
      },
    },
  },
}
