'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

type State = 'idle' | 'recording' | 'processing';

/**
 * VoiceButton - WhatsApp-style 2026 UX
 *
 * Tap to start → Tap to send (auto-lock)
 * Cancel button appears during recording
 * Simple, no swipe gestures for desktop
 */
export function VoiceButton({ onTranscript, disabled = false }: VoiceButtonProps) {
  const [state, setState] = useState<State>('idle');
  const [duration, setDuration] = useState(0);
  const [transcript, setTranscript] = useState('');

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stateRef = useRef<State>('idle');
  const transcriptRef = useRef('');

  // Keep refs in sync
  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    transcriptRef.current = transcript;
  }, [transcript]);

  // Check support
  const isSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  // Format duration as mm:ss
  const formatDuration = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  // Send transcript
  const send = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);

    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }

    setState('processing');

    // Small delay for final transcript
    setTimeout(() => {
      const finalTranscript = transcriptRef.current;
      if (finalTranscript.trim()) {
        onTranscript(finalTranscript.trim());
      }
      setState('idle');
      setTranscript('');
      setDuration(0);
    }, 300);
  }, [onTranscript]);

  // Cancel recording
  const cancel = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);

    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }

    setState('idle');
    setTranscript('');
    setDuration(0);
  }, []);

  // Start recording
  const start = useCallback(() => {
    if (disabled || !isSupported || stateRef.current === 'recording') return;

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) return;
    const recognition = new SpeechRecognitionAPI();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'pt-BR';

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let text = '';
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript;
      }
      setTranscript(text);
    };

    recognition.onerror = () => {
      cancel();
    };

    recognition.onend = () => {
      // Only process if we were recording (not cancelled)
      if (stateRef.current === 'recording' && transcriptRef.current) {
        send();
      }
    };

    recognitionRef.current = recognition;
    recognition.start();

    setState('recording');
    setDuration(0);
    setTranscript('');

    // Duration timer
    timerRef.current = setInterval(() => {
      setDuration(d => d + 1);
    }, 1000);
  }, [disabled, isSupported, cancel, send]);

  // Handle main button click
  const handleClick = () => {
    if (state === 'idle') {
      start();
    } else if (state === 'recording') {
      send();
    }
  };

  // Cleanup
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (recognitionRef.current) recognitionRef.current.abort();
    };
  }, []);

  if (!isSupported) return null;

  return (
    <div className="voice-btn-wrap">
      <AnimatePresence mode="wait">
        {state === 'recording' && (
          <motion.div
            className="voice-recording-bar"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            {/* Cancel button */}
            <button
              type="button"
              className="voice-cancel"
              onClick={cancel}
              aria-label="Cancelar"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>

            {/* Waveform indicator */}
            <div className="voice-wave">
              {[...Array(5)].map((_, i) => (
                <motion.span
                  key={i}
                  animate={{
                    scaleY: [1, 1.5 + Math.random(), 1],
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 0.4,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>

            {/* Duration */}
            <span className="voice-duration">{formatDuration(duration)}</span>

            {/* Live transcript preview */}
            {transcript && (
              <span className="voice-preview">
                {transcript.length > 30 ? '...' + transcript.slice(-30) : transcript}
              </span>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main mic button */}
      <motion.button
        type="button"
        className={`voice-btn ${state}`}
        onClick={handleClick}
        disabled={disabled || state === 'processing'}
        whileTap={{ scale: 0.92 }}
        animate={{
          backgroundColor: state === 'recording' ? '#ef4444' : 'var(--accent)',
        }}
        aria-label={state === 'idle' ? 'Gravar mensagem de voz' : 'Enviar mensagem'}
      >
        <AnimatePresence mode="wait">
          {state === 'idle' && (
            <motion.svg
              key="mic"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" x2="12" y1="19" y2="22" />
            </motion.svg>
          )}
          {state === 'recording' && (
            <motion.svg
              key="send"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="currentColor"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </motion.svg>
          )}
          {state === 'processing' && (
            <motion.div
              key="spinner"
              className="voice-spinner"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
            />
          )}
        </AnimatePresence>
      </motion.button>

      <style jsx>{`
        .voice-btn-wrap {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .voice-recording-bar {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 12px;
          background: var(--bg-soft);
          border-radius: 20px;
          border: 1px solid var(--border);
        }

        .voice-cancel {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          border: none;
          background: var(--bg);
          color: var(--text-muted);
          display: grid;
          place-items: center;
          cursor: pointer;
          transition: all 0.15s;
        }
        .voice-cancel:hover {
          background: #fee2e2;
          color: #ef4444;
        }

        .voice-wave {
          display: flex;
          align-items: center;
          gap: 2px;
          height: 20px;
        }
        .voice-wave span {
          width: 3px;
          height: 8px;
          background: #ef4444;
          border-radius: 2px;
        }

        .voice-duration {
          font-size: 13px;
          font-weight: 500;
          color: #ef4444;
          font-variant-numeric: tabular-nums;
          min-width: 36px;
        }

        .voice-preview {
          font-size: 12px;
          color: var(--text-muted);
          max-width: 150px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .voice-btn {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: none;
          background: var(--accent);
          color: white;
          display: grid;
          place-items: center;
          cursor: pointer;
          transition: box-shadow 0.2s;
        }
        .voice-btn:hover:not(:disabled) {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .voice-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .voice-btn.recording {
          box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2);
        }

        .voice-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid transparent;
          border-top-color: white;
          border-radius: 50%;
        }
      `}</style>
    </div>
  );
}
