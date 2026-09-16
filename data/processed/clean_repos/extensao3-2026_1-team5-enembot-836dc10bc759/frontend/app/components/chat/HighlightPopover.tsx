'use client';

import { useEffect, useRef, useState } from 'react';
import type { HighlightAction } from '../../lib/llm/llmClient';

type Selection = { text: string; rect: DOMRect };

type Props = {
  containerRef: React.RefObject<HTMLElement | null>;
  onAction: (text: string, action: HighlightAction) => void;
};

/**
 * Escuta selecao de texto dentro do container e abre um popover flutuante
 * com acoes IA (explicar / aprofundar / gerar questao).
 */
export function HighlightPopover({ containerRef, onAction }: Props) {
  const [sel, setSel] = useState<Selection | null>(null);
  const popRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handle() {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        setSel(null);
        return;
      }
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      const text = selection.toString().trim();
      if (text.length < 3) {
        setSel(null);
        return;
      }
      // so ativa se a selecao esta dentro do container
      const container = containerRef.current;
      if (!container) return;
      const anchor = range.commonAncestorContainer;
      if (container.contains(anchor instanceof Element ? anchor : anchor.parentElement)) {
        setSel({ text, rect });
      } else {
        setSel(null);
      }
    }
    document.addEventListener('selectionchange', handle);
    return () => document.removeEventListener('selectionchange', handle);
  }, [containerRef]);

  useEffect(() => {
    function onScroll() {
      setSel(null);
    }
    window.addEventListener('scroll', onScroll, true);
    return () => window.removeEventListener('scroll', onScroll, true);
  }, []);

  if (!sel) return null;

  const style: React.CSSProperties = {
    top: Math.max(8, sel.rect.top - 44),
    left: Math.min(window.innerWidth - 360, Math.max(8, sel.rect.left + sel.rect.width / 2 - 160)),
  };

  const run = (action: HighlightAction) => {
    onAction(sel.text, action);
    setSel(null);
    window.getSelection()?.removeAllRanges();
  };

  return (
    <div ref={popRef} className="highlight-popover" style={style} role="toolbar" aria-label="Ações de IA">
      <button onClick={() => run('explicar')}>
        <span aria-hidden>💬</span> Explicar
      </button>
      <button onClick={() => run('aprofundar')}>
        <span aria-hidden>🔬</span> Aprofundar
      </button>
      <button onClick={() => run('gerar-questao')}>
        <span aria-hidden>✨</span> Gerar questão
      </button>
      <button onClick={() => run('traduzir')}>
        <span aria-hidden>🔤</span> Simplificar
      </button>
    </div>
  );
}
