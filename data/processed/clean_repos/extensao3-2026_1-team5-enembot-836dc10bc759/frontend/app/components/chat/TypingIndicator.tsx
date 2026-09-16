import { motion } from 'framer-motion';

export function TypingIndicator() {
  return (
    <motion.div
      className="msg assistant"
      aria-live="polite"
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="msg-avatar ai" aria-hidden>
        E
      </div>
      <div className="msg-body">
        <div className="msg-header">
          <span className="name">ENEMBot</span>
          <span className="time">digitando…</span>
        </div>
        <div className="typing">
          <span />
          <span />
          <span />
        </div>
      </div>
    </motion.div>
  );
}
