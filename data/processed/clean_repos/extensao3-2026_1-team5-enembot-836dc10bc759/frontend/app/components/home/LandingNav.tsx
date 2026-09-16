'use client';

import Link from 'next/link';
import { useTheme } from '../providers/ThemeProvider';

export function LandingNav({ onOpenCommand }: { onOpenCommand: () => void }) {
  const { theme, toggle } = useTheme();

  return (
    <header className="landing-nav">
      <div className="container landing-nav-inner">
        <Link href="/" className="brand-lockup" aria-label="ENEMBot">
          <span className="brand-mark" aria-hidden>
            E
          </span>
          <span className="brand-name">ENEMBot</span>
        </Link>

        <nav className="landing-nav-links" aria-label="Navegação">
          <a href="#features" className="landing-nav-link">
            Recursos
          </a>
          <a href="#builds" className="landing-nav-link">
            Builds
          </a>
          <a href="#workflow" className="landing-nav-link">
            Como funciona
          </a>
          <a href="#faq" className="landing-nav-link">
            FAQ
          </a>
        </nav>

        <div className="landing-nav-actions">
          <button
            className="btn btn-ghost"
            onClick={onOpenCommand}
            aria-label="Abrir paleta de comandos"
            title="Paleta (⌘K)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <span className="kbd">⌘K</span>
          </button>
          <button className="btn btn-ghost" onClick={toggle} aria-label="Alternar tema">
            {theme === 'dark' ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
              </svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
          <Link href="/chat/matematica" className="btn btn-primary">
            Ir ao chat →
          </Link>
        </div>
      </div>
    </header>
  );
}
