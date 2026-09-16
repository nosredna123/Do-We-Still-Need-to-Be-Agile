'use client';

type Props = {
  onOpenStudyPlan: () => void;
};

export function Inspector({ onOpenStudyPlan }: Props) {
  return (
    <aside className="ws-inspector" aria-label="Painel lateral do chat">
      <div className="insp-block">
        <button className="insp-cta" onClick={onOpenStudyPlan}>
          <span aria-hidden>📅</span>
          Pedir plano à IA (no chat)
        </button>
      </div>
    </aside>
  );
}
