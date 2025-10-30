import { NavLink } from 'react-router-dom';
import PlayerSwitcher from './PlayerSwitcher';

const links = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/inventory', label: 'Inventory' },
  { to: '/shop', label: 'Shop' },
];

function SunIcon(props) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...props}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.364-7.364-1.414 1.414M8.05 17.95l-1.414 1.414m0-13.656L8.05 8.05m9.9 9.9 1.414 1.414" />
    </svg>
  );
}

function MoonIcon(props) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...props}>
      <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 1 0 9.79 9.79z" />
    </svg>
  );
}

function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark';

  const handleClick = () => {
    if (typeof onToggle === 'function') {
      onToggle();
    }
  };

  return (
    <button
      type="button"
      className="top-nav__theme-toggle"
      onClick={handleClick}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      {isDark ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}

function TopNav({ theme = 'light', onToggleTheme }) {
  return (
    <header className="top-nav">
      <div className="top-nav__brand">Ultimate App</div>
      <div className="top-nav__actions">
        <nav className="top-nav__links">
          {links.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end}>
              {label}
            </NavLink>
          ))}
        </nav>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        <PlayerSwitcher />
      </div>
    </header>
  );
}

export default TopNav;
