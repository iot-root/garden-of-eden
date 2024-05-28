/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class', '[data-kb-theme="dark"]'],
  content: ['src/pages/**/*.{ts,tsx}', 'src/components/**/*.{ts,tsx}'],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px'
      }
    },
    extend: {
      colors: {
        lightgray: '#F6F6F6',
        textgray: '#94A3B8'
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--kb-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--kb-accordion-content-height)' },
          to: { height: 0 }
        },
        'collapsible-down': {
          from: { height: 0 },
          to: { height: 'var(--kb-collapsible-content-height)' }
        },
        'collapsible-up': {
          from: { height: 'var(--kb-collapsible-content-height)' },
          to: { height: 0 }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'collapsible-down': 'collapsible-down 0.2s ease-out',
        'collapsible-up': 'collapsible-up 0.2s ease-out'
      }
    }
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/container-queries')
  ]
};
