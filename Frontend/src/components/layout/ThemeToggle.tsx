import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useInvestigation();
  const isLight = theme === 'light';

  return (
    <button
      type="button"
      id="theme-toggle-button"
      onClick={toggleTheme}
      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 cursor-pointer shadow-md group ${
        isLight
          ? 'bg-[#4F46E5] text-white shadow-[0_0_14px_rgba(79,70,229,0.5)] border border-[#C7D2FE] ring-2 ring-[#4F46E5]/40 hover:scale-105'
          : 'bg-[#0D0D11] text-[#FACC15] border border-[#FACC15]/60 shadow-[0_0_14px_rgba(250,204,21,0.45)] ring-2 ring-[#FACC15]/30 hover:scale-105'
      }`}
      title={isLight ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
      aria-label="Toggle light and dark theme"
    >
      {isLight ? (
        <Sun className="w-5 h-5 transition-transform duration-300 group-hover:rotate-45" />
      ) : (
        <Moon className="w-5 h-5 transition-transform duration-300 group-hover:-rotate-12" />
      )}
    </button>
  );
};
