import { useEffect, useState, type ReactNode } from 'react'
import { ThemeContext } from './ThemeContextBase'

export type Theme = 'dark' | 'light'

const THEME_KEY = 'cna-theme'

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem(THEME_KEY)
    return stored === 'light' ? 'light' : 'dark'
  })

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  function toggleTheme() {
    setTheme((currentTheme) => currentTheme === 'dark' ? 'light' : 'dark')
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}
