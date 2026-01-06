import React, { createContext, useContext, useState, useEffect } from 'react';

interface ThemeContextType {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const stored = localStorage.getItem('darkMode');
    return stored ? stored === 'dark' : true;
  });

  useEffect(() => {
    // Toggle dark mode class
    document.documentElement.classList.toggle('dark', isDarkMode);
    
    // Update all theme variables
    const theme = {
      '--bg-primary': isDarkMode ? '#111827' : '#ffffff',
      '--bg-secondary': isDarkMode ? '#1f2937' : '#f3f4f6',
      '--bg-tertiary': isDarkMode ? '#374151' : '#e5e7eb',
      '--text-primary': isDarkMode ? '#ffffff' : '#000000',
      '--text-secondary': isDarkMode ? '#9ca3af' : '#1f2937',
      '--text-tertiary': isDarkMode ? '#6b7280' : '#374151',
      '--border-color': isDarkMode ? 'rgba(59, 130, 246, 0.2)' : 'rgba(0, 0, 0, 0.1)',
      '--accent-color': isDarkMode ? '#10b981' : '#047857',
      '--accent-light': isDarkMode ? '#34d399' : '#059669',
      '--accent-dark': isDarkMode ? '#047857' : '#065f46',
      '--shadow-sm': isDarkMode ? '0 1px 2px 0 rgba(0, 0, 0, 0.3)' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      '--shadow-md': isDarkMode ? '0 4px 6px -1px rgba(0, 0, 0, 0.4)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      '--shadow-lg': isDarkMode ? '0 10px 15px -3px rgba(0, 0, 0, 0.5)' : '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
    };

    // Apply all theme variables
    Object.entries(theme).forEach(([property, value]) => {
      document.body.style.setProperty(property, value);
    });

    // Store preference in localStorage
    localStorage.setItem('darkMode', isDarkMode ? 'dark' : 'light');

    // Add/remove transition class for smooth theme changes
    document.body.classList.add('transition-theme');
    const timeout = setTimeout(() => {
      document.body.classList.remove('transition-theme');
    }, 300);

    return () => clearTimeout(timeout);
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
