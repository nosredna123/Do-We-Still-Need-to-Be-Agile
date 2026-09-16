export function Footer() {
  return (
    <footer className="landing-footer">
      <div className="container landing-footer-inner">
        <div>
          <span className="brand-lockup" style={{ marginRight: 10 }}>
            <span className="brand-mark" aria-hidden>
              E
            </span>
            <span className="brand-name">ENEMBot</span>
          </span>
          <span>© 2026 — projeto de extensão, UECE</span>
        </div>
        <div style={{ display: 'flex', gap: 20 }}>
          <a href="#features" className="landing-nav-link">
            Recursos
          </a>
          <a href="#faq" className="landing-nav-link">
            FAQ
          </a>
          <a href="https://github.com" className="landing-nav-link" rel="noreferrer">
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
