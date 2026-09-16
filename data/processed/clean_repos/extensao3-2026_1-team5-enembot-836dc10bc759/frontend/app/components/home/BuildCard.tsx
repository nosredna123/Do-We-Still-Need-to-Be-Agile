import type { Build } from '../../lib/types';

type BuildCardProps = {
  item: Build;
  isActive: boolean;
  onSelect: (buildId: Build['id']) => void;
};

export function BuildCard({ item, isActive, onSelect }: BuildCardProps) {
  return (
    <button
      type="button"
      className={`card build-card ${isActive ? 'is-active' : ''}`}
      onClick={() => onSelect(item.id)}
      aria-pressed={isActive}
    >
      {isActive && <span className="active-plate">ATIVO</span>}
      <div className="card-icon" aria-hidden>
        {item.icon}
      </div>
      <h3 className="card-title">{item.title}</h3>
      <p className="card-badge">{item.badge}</p>
      <p className="card-description">{item.description}</p>
    </button>
  );
}
