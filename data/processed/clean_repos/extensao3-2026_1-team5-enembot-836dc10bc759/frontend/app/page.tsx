'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Builds } from './components/home/Builds';
import { FAQ } from './components/home/FAQ';
import { Features } from './components/home/Features';
import { FinalCTA } from './components/home/FinalCTA';
import { Footer } from './components/home/Footer';
import { Hero } from './components/home/Hero';
import { LandingNav } from './components/home/LandingNav';
import { LogosStrip } from './components/home/LogosStrip';
import { SubjectsShowcase } from './components/home/SubjectsShowcase';
import { Testimonials } from './components/home/Testimonials';
import { Workflow } from './components/home/Workflow';
import { CommandPalette } from './components/chat/CommandPalette';
import { StudyPlanModal } from './components/chat/StudyPlanModal';
import { useTheme } from './components/providers/ThemeProvider';
import type { CommandActionId } from './lib/llm/llmClient';

export default function HomePage() {
  const [cmdOpen, setCmdOpen] = useState(false);
  const [studyPlanOpen, setStudyPlanOpen] = useState(false);
  const { setTheme, theme } = useTheme();
  const router = useRouter();

  async function runCommand(id: CommandActionId) {
    if (id === 'open-study-plan') {
      setStudyPlanOpen(true);
      return;
    }
    if (id === 'toggle-theme') {
      setTheme(theme === 'light' ? 'dark' : 'light');
      return;
    }
    // maioria das acoes IA so faz sentido dentro do chat — empurra o usuario pra la
    router.push('/chat/matematica');
  }

  return (
    <div className="landing">
      <LandingNav onOpenCommand={() => setCmdOpen(true)} />
      <Hero />
      <LogosStrip />
      <Features />
      <Builds />
      <SubjectsShowcase />
      <Workflow />
      <Testimonials />
      <FAQ />
      <FinalCTA />
      <Footer />

      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} onRun={runCommand} scope="global" />
      <StudyPlanModal open={studyPlanOpen} onOpenChange={setStudyPlanOpen} />
    </div>
  );
}
