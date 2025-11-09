/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Figma Design System Colors
        background: {
          DEFAULT: '#ffffff',
          dark: 'oklch(0.145 0 0)',
        },
        foreground: {
          DEFAULT: 'oklch(0.145 0 0)',
          dark: 'oklch(0.985 0 0)',
        },
        primary: {
          DEFAULT: '#030213',
          foreground: '#ffffff',
          dark: 'oklch(0.985 0 0)',
          'dark-foreground': 'oklch(0.205 0 0)',
        },
        secondary: {
          DEFAULT: 'oklch(0.95 0.0058 264.53)',
          foreground: '#030213',
          dark: 'oklch(0.269 0 0)',
          'dark-foreground': 'oklch(0.985 0 0)',
        },
        muted: {
          DEFAULT: '#ececf0',
          foreground: '#717182',
          dark: 'oklch(0.269 0 0)',
          'dark-foreground': 'oklch(0.708 0 0)',
        },
        accent: {
          DEFAULT: '#e9ebef',
          foreground: '#030213',
          dark: 'oklch(0.269 0 0)',
          'dark-foreground': 'oklch(0.985 0 0)',
        },
        destructive: {
          DEFAULT: '#d4183d',
          foreground: '#ffffff',
          dark: 'oklch(0.396 0.141 25.723)',
          'dark-foreground': 'oklch(0.637 0.237 25.331)',
        },
        border: {
          DEFAULT: 'rgba(0, 0, 0, 0.1)',
          dark: 'oklch(0.269 0 0)',
        },
        input: {
          DEFAULT: 'transparent',
          background: '#f3f3f5',
          dark: 'oklch(0.269 0 0)',
        },
        card: {
          DEFAULT: '#ffffff',
          foreground: 'oklch(0.145 0 0)',
          dark: 'oklch(0.145 0 0)',
          'dark-foreground': 'oklch(0.985 0 0)',
        },
        ring: {
          DEFAULT: 'oklch(0.708 0 0)',
          dark: 'oklch(0.439 0 0)',
        },
        // Chart colors for data visualization
        chart: {
          1: 'oklch(0.646 0.222 41.116)',
          2: 'oklch(0.6 0.118 184.704)',
          3: 'oklch(0.398 0.07 227.392)',
          4: 'oklch(0.828 0.189 84.429)',
          5: 'oklch(0.769 0.188 70.08)',
        },
      },
      borderRadius: {
        sm: 'calc(0.625rem - 4px)', // ~6px
        md: 'calc(0.625rem - 2px)', // ~8px
        lg: '0.625rem', // 10px
        xl: 'calc(0.625rem + 4px)', // ~14px
      },
      fontSize: {
        base: '16px',
      },
      fontWeight: {
        normal: '400',
        medium: '500',
      },
      lineHeight: {
        base: '1.5',
      },
    },
  },
  plugins: [],
}

