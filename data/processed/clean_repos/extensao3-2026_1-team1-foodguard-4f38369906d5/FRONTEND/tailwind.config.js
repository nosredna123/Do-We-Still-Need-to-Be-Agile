/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        foodguard: {
          50: '#EDFFF6',
          100: '#DAFFED',
          200: '#BFF3DD',
          300: '#A5E6CC',
          400: '#619D85',
          500: '#008B5B',
          600: '#00784F',
          700: '#006241',
          800: '#005136',
          900: '#00402A',
          950: '#001E14'
        }
      },
      fontFamily: {
        sansita: ['"Sansita"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

