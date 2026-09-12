/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        saathi: {
          // Indian Government / Uniformed Force Institutional Palette
          primary: "#1B4D3E",       // Deep Forest / Military Green
          primaryDark: "#113328",   // Darkest Forest Green
          primaryLight: "#2D6A56",  // Muted Olive / Forest Accent
          primarySubtle: "#EBF3EE", // Very light green tint
          
          secondary: "#365347",     // Muted Olive Green
          secondaryLight: "#DDE7E1",// Light sage border/bg
          
          saffron: "#E65100",       // Indian Saffron / Warm Orange
          saffronLight: "#FFF3E0",  // Saffron highlight tint
          saffronHover: "#BF360C",  // Deep Saffron hover
          
          terracotta: "#C2410C",    // Supporting Terracotta
          terracottaLight: "#FFEDD5",
          
          bg: "#F4F6F4",            // Off-white / Light warm stone
          bgAlt: "#EAEFEA",         // Slightly deeper stone
          card: "#FFFFFF",          // Pure white card surfaces
          cardHeader: "#F8FAF8",    // Subtle card header tint
          border: "#D5DFD8",        // Crisp institutional border
          borderLight: "#E5ECE7",   // Light divider
          
          textDark: "#10231B",      // Deep Forest Charcoal
          textMuted: "#4B6358",     // Muted green-gray
          textSubtle: "#6B857A",    // Subtle label text
          
          // Status Priorities (Standard Welfare Signals)
          green: "#15803D",         // Stable (<30)
          greenBg: "#DCFCE7",
          greenBorder: "#86EFAC",
          
          yellow: "#B45309",        // Low-Moderate (30-54)
          yellowBg: "#FEF3C7",
          yellowBorder: "#FDE68A",
          
          orange: "#C2410C",        // Moderate-High (55-74)
          orangeBg: "#FFEDD5",
          orangeBorder: "#FDBA74",
          
          red: "#B91C1C",           // High Priority (>=75)
          redBg: "#FEE2E2",
          redBorder: "#FCA5A5",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'gov': '0 1px 3px 0 rgba(17, 51, 40, 0.08), 0 1px 2px 0 rgba(17, 51, 40, 0.04)',
        'gov-md': '0 4px 6px -1px rgba(17, 51, 40, 0.1), 0 2px 4px -1px rgba(17, 51, 40, 0.06)',
        'gov-lg': '0 10px 15px -3px rgba(17, 51, 40, 0.1), 0 4px 6px -2px rgba(17, 51, 40, 0.05)',
      }
    },
  },
  plugins: [],
}
