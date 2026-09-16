import type { ReactNode } from 'react';
import { Inter, Instrument_Serif, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from './components/providers/ThemeProvider';

const sans = Inter({
  subsets: ['latin'],
  variable: '--font-sans-var',
  display: 'swap',
});

const display = Instrument_Serif({
  subsets: ['latin'],
  weight: ['400'],
  style: ['normal', 'italic'],
  variable: '--font-display-var',
  display: 'swap',
});

const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono-var',
  display: 'swap',
});

export const metadata = {
  title: 'ENEMBot — Tutor ENEM adaptativo com IA',
  description:
    'O tutor de IA que se adapta ao seu ritmo. Resolva questões estilo ENEM, receba explicações sob medida e construa um plano de estudo que funciona de verdade.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={`${sans.variable} ${display.variable} ${mono.variable}`}>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
