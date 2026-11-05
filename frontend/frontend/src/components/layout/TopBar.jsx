import { Menu, Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext.jsx';
import { useHealth } from '../../hooks/useHealth.js';

const DOT = {
  online: ['bg-emerald-500', 'API connected'],
  offline: ['bg-red-500', 'API offline'],
  checking: ['bg-slate-400', 'Checking API...'],
};

export default function TopBar({ onMenu }) {
  const { dark, toggle } = useTheme();
  const health = useHealth();
  const [dot, label] = DOT[health];

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
      <button onClick={onMenu} className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden" aria-label="Open menu">
        <Menu className="h-5 w-5" />
      </button>
      <div className="hidden lg:block" />
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
          <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
          {label}
        </span>
        <button onClick={toggle} className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Toggle theme">
          {dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
      </div>
    </header>
  );
}
