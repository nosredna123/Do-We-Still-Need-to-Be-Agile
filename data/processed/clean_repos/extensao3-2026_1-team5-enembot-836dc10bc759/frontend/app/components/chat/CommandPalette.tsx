'use client';

import { Command } from 'cmdk';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect } from 'react';
import { COMMAND_ACTIONS, type CommandActionDef } from '../../lib/commandActions';
import type { CommandActionId } from '../../lib/llm/llmClient';

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onRun: (id: CommandActionId) => void;
  /** 'chat' filtra comandos chat-only; 'global' mostra so globais */
  scope?: 'chat' | 'global';
};

const GROUPS: Array<CommandActionDef['group']> = ['IA', 'Sessão', 'Navegação', 'Ajustes'];

export function CommandPalette({ open, onOpenChange, onRun, scope = 'chat' }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
      if (e.key === 'Escape' && open) onOpenChange(false);
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onOpenChange]);

  const actions =
    scope === 'global'
      ? COMMAND_ACTIONS.filter((a) => a.context === 'global')
      : COMMAND_ACTIONS;

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            key="cmd-backdrop"
            className="cmd-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => onOpenChange(false)}
          />
          <motion.div
            key="cmd-overlay"
            className="cmd-overlay"
            initial={{ opacity: 0, y: -12, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.22, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Command label="Paleta de comandos" className="cmd" loop>
              <div className="cmd-input-wrap">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.3-4.3" />
                </svg>
                <Command.Input placeholder="Digite um comando ou pergunta para a IA…" className="cmd-input" autoFocus />
                <span className="kbd">Esc</span>
              </div>
              <Command.List className="cmd-list">
                <Command.Empty className="cmd-empty">Nenhum comando encontrado.</Command.Empty>
                {GROUPS.map((group) => {
                  const items = actions.filter((a) => a.group === group);
                  if (items.length === 0) return null;
                  return (
                    <Command.Group key={group} heading={group} className="cmd-group">
                      <div className="cmd-group-label">{group}</div>
                      {items.map((a) => (
                        <Command.Item
                          key={a.id}
                          value={`${a.label} ${a.description}`}
                          className="cmd-item"
                          onSelect={() => {
                            onRun(a.id);
                            onOpenChange(false);
                          }}
                        >
                          <span className="cico" aria-hidden>
                            {a.icon}
                          </span>
                          <span className="ctext">
                            <div className="ctitle">{a.label}</div>
                            <div className="cdesc">{a.description}</div>
                          </span>
                          {a.shortcut && <span className="kbd">{a.shortcut}</span>}
                        </Command.Item>
                      ))}
                    </Command.Group>
                  );
                })}
              </Command.List>
              <div className="cmd-footer">
                <span className="group">
                  <span className="kbd">↵</span> selecionar
                </span>
                <span className="group">
                  <span className="kbd">↑</span> <span className="kbd">↓</span> navegar
                </span>
                <span className="group">
                  <span className="kbd">⌘</span> <span className="kbd">K</span> abrir/fechar
                </span>
              </div>
            </Command>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
