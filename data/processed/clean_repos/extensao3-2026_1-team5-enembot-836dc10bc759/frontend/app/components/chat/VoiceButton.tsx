'use client';

import { useState, useRef, useCallback, useEffect, useImperativeHandle, forwardRef } from 'react';

export interface VoiceButtonHandle {
  start: () => void;
  send: () => void;
  cancel: () => void;
  isSupported: boolean;
}

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  onTranscriptChange: (text: string) => void;
  onStateChange: (state: 'idle' | 'recording' | 'processing') => void;
}

export const VoiceButton = forwardRef<VoiceButtonHandle, VoiceButtonProps>(
  ({ onTranscript, onTranscriptChange, onStateChange }, ref) => {
    const [state, setState] = useState<'idle' | 'recording' | 'processing'>('idle');
    const recognitionRef = useRef<SpeechRecognition | null>(null);
    const stateRef = useRef(state);
    const transcriptRef = useRef('');

    useEffect(() => { stateRef.current = state; onStateChange(state); }, [state, onStateChange]);

    const isSupported = typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

    const send = useCallback(() => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      setState('processing');
      setTimeout(() => {
        const finalTranscript = transcriptRef.current;
        if (finalTranscript.trim()) onTranscript(finalTranscript.trim());
        setState('idle');
        transcriptRef.current = '';
        onTranscriptChange('');
      }, 300);
    }, [onTranscript, onTranscriptChange]);

    const cancel = useCallback(() => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }
      setState('idle');
      transcriptRef.current = '';
      onTranscriptChange('');
    }, [onTranscriptChange]);

    const start = useCallback(() => {
      if (!isSupported || stateRef.current === 'recording') return;

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
        transcriptRef.current = text;
        onTranscriptChange(text);
      };

      recognition.onerror = () => cancel();

      recognition.onend = () => {
        if (stateRef.current === 'recording' && transcriptRef.current) {
          send();
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      setState('recording');
      transcriptRef.current = '';
      onTranscriptChange('');
    }, [isSupported, cancel, send]);

    useImperativeHandle(ref, () => ({ start, send, cancel, isSupported }), [start, send, cancel, isSupported]);

    useEffect(() => {
      return () => {
        if (recognitionRef.current) recognitionRef.current.abort();
      };
    }, []);

    return null; // sem UI própria
  }
);

VoiceButton.displayName = 'VoiceButton';