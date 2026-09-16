import { useState, useRef } from "react";
import mammoth from 'mammoth';


interface Props {
  theme: string;
  essayId: number;
  locked: boolean;
  onSubmit: (essayId: number, text: string) => void;
  onNext: () => void;
}

export function EssayCard({ theme, essayId, locked, onSubmit, onNext }: Props) {
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const isLocked = locked || submitted;

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
  
    if (file.name.endsWith('.docx')) {
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      const normalized = result.value
        .replace(/\r\n/g, '\n')
        .replace(/\n\n+/g, '\n')  // múltiplos \n viram um só
        .trim();
      setText(normalized);
    } else {
      // .txt
      const reader = new FileReader();
      reader.onload = (ev) => setText(ev.target?.result as string ?? '');
      reader.readAsText(file);
    }
  }

  function handleSubmit() {
    if (!text.trim()) return;
    onSubmit(essayId, text);
    setSubmitted(true);
  }

  if (isLocked) {
    return (
      <article className="q-card q-card--uniform">
        <header className="q-meta">
          <span className="q-chip accent">Redação</span>
        </header>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text)' }}>
          {theme}
        </p>
      </article>
    );
  }

  return (
    <article className="q-card q-card--uniform">
      <header className="q-meta">
        <span className="q-chip accent">Redação</span>
      </header>
  
      <p className="q-statement">{theme}</p>
  
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Escreva sua redação aqui..."
        rows={10}
        style={{
          width: '100%',
          resize: 'vertical',
          border: '1.5px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '12px 14px',
          fontSize: '0.9rem',
          lineHeight: 1.7,
          color: 'var(--text)',
          background: 'var(--bg)',
          outline: 'none',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          marginBottom: '12px',
        }}
      />
  
      <input
        ref={fileRef}
        type="file"
        accept=".txt,.doc,.docx"
        style={{ display: 'none' }}
        onChange={handleFile}
      />
  
      <button
        type="button"
        onClick={() => fileRef.current?.click()}
        style={{
          alignSelf: 'flex-start',
          background: 'transparent',
          border: '1.5px dashed var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '8px 18px',
          fontSize: '0.85rem',
          fontWeight: 500,
          color: 'var(--text-secondary)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          marginBottom: '12px',
        }}
      >
        📎 Carregar arquivo (.txt, .doc)
      </button>
  
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        paddingTop: '12px',
        borderTop: '1px solid var(--border)',
      }}>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!text.trim()}
          style={{
            background: text.trim() ? 'var(--accent)' : 'var(--bg-soft)',
            color: text.trim() ? '#fff' : 'var(--text-secondary)',
            border: 'none',
            borderRadius: 'var(--radius-lg)',
            padding: '9px 22px',
            fontSize: '0.88rem',
            fontWeight: 600,
            cursor: text.trim() ? 'pointer' : 'not-allowed',
            transition: 'background 0.2s',
          }}
        >
          Enviar redação
        </button>
  
        <button
          type="button"
          onClick={onNext}
          style={{
            background: 'transparent',
            border: '1.5px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            padding: '8px 18px',
            fontSize: '0.85rem',
            fontWeight: 500,
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          Próximo tema →
        </button>
      </div>
    </article>
  );
}