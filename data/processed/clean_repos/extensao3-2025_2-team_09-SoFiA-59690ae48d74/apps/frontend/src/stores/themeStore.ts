import { create } from "zustand";

type Theme = 'light' | 'dark' | 'system';

interface ThemeStore {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeStore>((set) => ({
  theme: 'system',
  setTheme: (theme) => {
    set({ theme })

    const root = document.documentElement

    if (theme === 'light') {
      root.classList.remove('dark')
    } else if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.toggle('dark', prefersDark)
    }

    localStorage.setItem('theme', theme)
  },
}))
