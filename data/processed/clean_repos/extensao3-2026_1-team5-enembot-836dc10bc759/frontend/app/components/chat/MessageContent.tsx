'use client';

import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { type ReactNode } from 'react';

type Props = {
  content: string;
};

/**
 * Parser simples para <callout>...</callout> (nosso custom tag) — como o
 * react-markdown nao suporta HTML por padrao sem plugin, a gente transforma
 * manualmente no source ANTES de enviar ao markdown. Callouts viram blocos
 * marcados com ":::callout" (fake block) que detectamos depois.
 */
function preprocess(src: string): Array<{ kind: 'md' | 'callout'; variant?: 'info' | 'warn' | 'danger'; text: string }> {
  const blocks: Array<{ kind: 'md' | 'callout'; variant?: 'info' | 'warn' | 'danger'; text: string }> = [];
  const regex = /<callout(?:\s+type="(info|warn|danger)")?>([\s\S]*?)<\/callout>/g;
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = regex.exec(src)) !== null) {
    if (m.index > last) blocks.push({ kind: 'md', text: src.slice(last, m.index) });
    blocks.push({ kind: 'callout', variant: (m[1] as 'info' | 'warn' | 'danger') || 'info', text: m[2].trim() });
    last = m.index + m[0].length;
  }
  if (last < src.length) blocks.push({ kind: 'md', text: src.slice(last) });
  return blocks.length ? blocks : [{ kind: 'md', text: src }];
}

const components: Components = {
  // permite sublinhado/quebra sem exagerar
  hr: () => <hr style={{ border: 0, borderTop: '1px solid var(--border)', margin: '16px 0' }} />,
};

function Callout({ variant, children }: { variant?: 'info' | 'warn' | 'danger'; children: ReactNode }) {
  const cls = variant === 'warn' ? 'callout warn' : variant === 'danger' ? 'callout danger' : 'callout';
  const icon = variant === 'warn' ? '⚠️' : variant === 'danger' ? '🛑' : '💡';
  return (
    <div className={cls}>
      <span className="cico" aria-hidden>
        {icon}
      </span>
      <div>{children}</div>
    </div>
  );
}

export function MessageContent({ content }: Props) {
  const blocks = preprocess(content);
  return (
    <>
      {blocks.map((b, i) => {
        if (b.kind === 'callout') {
          return (
            <Callout key={i} variant={b.variant}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[[rehypeKatex, { strict: false }]]}
              >
                {b.text}
              </ReactMarkdown>
            </Callout>
          );
        }
        return (
          <ReactMarkdown
            key={i}
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[[rehypeKatex, { strict: false }]]}
            components={components}
          >
            {b.text}
          </ReactMarkdown>
        );
      })}
    </>
  );
}
