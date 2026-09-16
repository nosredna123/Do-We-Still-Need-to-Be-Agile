type AppHeaderProps = {
  brand: string;
};

export function AppHeader({ brand }: AppHeaderProps) {
  const hasBotSuffix = brand.endsWith('Bot');
  const brandMain = hasBotSuffix ? brand.slice(0, -3) : brand;
  const brandSuffix = hasBotSuffix ? 'Bot' : '';

  return (
    <header className="app-header">
      <div className="container app-header-inner">
        <div className="brand-badge" aria-hidden>
          <span className="brand-dot" />
        </div>
        <strong className="brand-text">
          <span className="brand-main">{brandMain}</span>
          {brandSuffix && <span className="brand-suffix">{brandSuffix}</span>}
        </strong>
      </div>
    </header>
  );
}
