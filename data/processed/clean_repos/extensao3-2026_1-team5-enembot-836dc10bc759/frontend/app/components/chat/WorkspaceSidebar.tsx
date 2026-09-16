'use client';

import Link from 'next/link';
import { useMemo } from 'react';
import { SUBJECTS } from '../../lib/catalog';
import type { ChatSchema } from '../../lib/backendTypes';
import type { SubjectId } from '../../lib/types';
import { habilidadeNome, subjectToHabilidadeId } from '../../lib/subjectHabilidade';
import { useTheme } from '../providers/ThemeProvider';

type Props = {
  activeSubjectId: SubjectId;
  onOpenCommand: () => void;
  chats: ChatSchema[];
  selectedChatId: number | null;
  onSelectChat: (chatId: number) => void;
  onCreateChat: () => void;
  onRequestDeleteChat: (chatId: number) => void;
  collapsed?: boolean;
};

function formatChatLabel(chat: ChatSchema) {
  const date = new Date(chat.atualizado_em || chat.criado_em);
  if (Number.isNaN(date.getTime())) return `#${chat.id}`;
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function WorkspaceSidebar({
  activeSubjectId,
  onOpenCommand,
  chats,
  selectedChatId,
  onSelectChat,
  onCreateChat,
  onRequestDeleteChat,
  collapsed = false,
}: Props) {
  const { theme, toggle } = useTheme();
  const activeHabilidade = subjectToHabilidadeId(activeSubjectId);

  const activeChats = useMemo(
    () =>
      chats
        .filter((c) => c.habilidade === activeHabilidade)
        .sort((a, b) => {
          const timeA = Date.parse(a.atualizado_em || a.criado_em);
          const timeB = Date.parse(b.atualizado_em || b.criado_em);
          if (timeA !== timeB) return timeB - timeA;
          return b.id - a.id;
        }),
    [chats, activeHabilidade],
  );

  return (
    <aside className={`ws-sidebar ${collapsed ? 'is-collapsed' : ''}`} aria-label="Navegação da workspace">
      <div className="ws-sidebar-header">
        <Link href="/" className="brand-lockup" aria-label="ENEMBot home">
          <span className="brand-mark" aria-hidden>
            E
          </span>
          <span className="brand-name">ENEMBot</span>
        </Link>
      </div>

      <button className="ws-sidebar-search" onClick={onOpenCommand} aria-label="Abrir paleta de comandos">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <span>Buscar ou digitar comando</span>
        <span className="hint">
          <span className="kbd">⌘</span>
          <span className="kbd">K</span>
        </span>
      </button>

      <nav className="ws-nav">
        <div className="ws-nav-label">Matérias</div>
        {SUBJECTS.map((s) => (
          <Link
            key={s.id}
            href={`/chat/${s.id}`}
            className={`ws-nav-item ${s.id === activeSubjectId ? 'is-active' : ''}`}
            title={collapsed ? s.title : undefined}
          >
            <span className="emoji" aria-hidden>
              {s.icon}
            </span>
            <span>{s.title}</span>
          </Link>
        ))}
      </nav>

      <div className="ws-nav-label" style={{ padding: '14px 14px 4px' }}>
        Históricos · {habilidadeNome(activeHabilidade)}
      </div>
      <div className="ws-sessions" style={{ gap: 10 }}>
        <button type="button" className="btn btn-ghost btn-sm" onClick={onCreateChat}>
          Nova conversa
        </button>

        {activeChats.length > 0 ? (
          <>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Selecionar histórico</span>
              <select
                className="input"
                value={selectedChatId ? String(selectedChatId) : ''}
                onChange={(e) => onSelectChat(Number(e.target.value))}
              >
                {activeChats.map((chat) => (
                  <option key={chat.id} value={chat.id}>
                    {chat.chat_name} · {formatChatLabel(chat)}
                  </option>
                ))}
              </select>
            </label>

            <div className="ws-session-list">
              {activeChats.map((chat) => (
                <div
                  key={chat.id}
                  className={`ws-session ${chat.id === selectedChatId ? 'is-active' : ''}`}
                  role="button"
                  tabIndex={0}
                  onClick={() => onSelectChat(chat.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectChat(chat.id);
                    }
                  }}
                >
                  <div className="title">{chat.chat_name || `Conversa #${chat.id}`}</div>
                  <div className="meta">
                    <span className="time">{formatChatLabel(chat)}</span>
                  </div>
                  <div className="actions">
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectChat(chat.id);
                      }}
                    >
                      Abrir
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={async (e) => {
                        e.stopPropagation();
                        onRequestDeleteChat(chat.id);
                      }}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="ws-session" style={{ opacity: 0.8 }}>
            <div className="title">Nenhum histórico ainda</div>
            <div className="meta">
              <span>Crie a primeira conversa dessa matéria</span>
            </div>
          </div>
        )}
      </div>

      <div className="ws-sidebar-footer">
        <div style={{ flex: 1 }}>
          <div style={{ color: 'var(--text-primary)', fontWeight: 500, fontSize: '0.84rem' }}>
            Ferramentas
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
            Tema e atalhos do workspace
          </div>
        </div>
        <button className="icon-btn" onClick={toggle} aria-label="Alternar tema" title="Alternar tema (⌘⇧L)">
          {theme === 'dark' ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <circle cx="12" cy="12" r="5" />
              <path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>
      </div>
    </aside>
  );
}
