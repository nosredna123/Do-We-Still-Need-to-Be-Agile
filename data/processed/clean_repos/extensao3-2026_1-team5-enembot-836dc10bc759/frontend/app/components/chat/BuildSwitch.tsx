'use client';

import { BUILDS } from '../../lib/catalog';
import type { BuildId } from '../../lib/types';

type Props = {
  value?: BuildId;
  onChange: (b: BuildId) => void;
};

export function BuildSwitch({ value, onChange }: Props) {
  return (
    <div className="pill-row" role="tablist" aria-label="Build ativa">
      {BUILDS.map((b) => (
        <button
          key={b.id}
          role="tab"
          aria-selected={b.id === value}
          onClick={() => onChange(b.id)}
          className={`pill ${b.id === value ? 'is-active' : ''}`}
          title={b.description}
        >
          <span aria-hidden>{b.icon}</span>
          {b.title}
        </button>
      ))}
    </div>
  );
}
