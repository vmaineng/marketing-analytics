"use client";

import { Sun, Moon, Menu, X } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import { useState } from "react";

export default function Navbar() {
  const NAV_ITEMS = ["Dashboard", "Profile", "Contact"];
  const [menuOpen, setMenuOpen] = useState<boolean>(false);
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="w-full px-4 py-5 flex justify-between items-center sticky">
      <div className="h-5 w-5 text-(--text-secondary)">Logo</div>
      <div className="hidden md:flex items-center gap-8">
        {NAV_ITEMS.map((item) => (
          <div
            key={item}
            className="relative text-sm text-(--text-secondary) hover:text-(--text-primary) transition-colors cursor-pointer"
          >
            {item}
          </div>
        ))}
        <button onClick={toggleTheme}>
          {theme == "dark" ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
      <div className="flex md:hidden items-center gap-4">
        <button
          onClick={toggleTheme}
          className="text--(--text-secondary) hover:text-(--text-primary) transition-colors"
        >
          {theme == "dark" ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="text-(--text-secondary)"
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
      {menuOpen && (
        <div className="absolute top-15 left-0 right-0 bg-background border-b border-(--card-border) px-6 py-4 flex flex-col gap-4 md:hidden">
          {NAV_ITEMS.map((item) => (
            <div
              key={item}
              className="text-sm text-(--text-secondary) hover:text-(--text-primary) transition-colors cursor-pointer"
              onClick={() => setMenuOpen(false)}
            >
              {item}
            </div>
          ))}
        </div>
      )}
    </nav>
  );
}
