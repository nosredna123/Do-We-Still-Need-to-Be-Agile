import { Header } from "../components/Header";
import { Hero } from "../components/Hero";
import { FeatureCard } from "../components/FeatureCard";
import { ToolsList } from "../components/ToolsList";
import { TeamStrip } from "../components/TeamStrip";
import { Footer } from "../components/Footer";
import { motion } from "motion/react";

interface HomePageProps {
  onNavigate?: (page: 'home' | 'login') => void;
}

export default function HomePage({ onNavigate }: HomePageProps) {
  const scrollToSection = (section: string) => {
    const element = document.getElementById(section);
    if (element) {
      const yOffset = -100; // Offset for fixed header
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  return (
    <div className="bg-white relative size-full" data-name="Home Page">
      <Header onNavigate={onNavigate} onScrollTo={scrollToSection} />

      <div id="hero">
        <Hero onCTAClick={() => onNavigate?.('login')} />
      </div>

      {/* Decorative elements */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        className="absolute border-2 border-slate-200 border-solid left-[1553px] size-[113.862px] top-[1127px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute border-2 border-slate-200 border-solid left-[1639px] size-[113.862px] top-[1207px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute border-2 border-slate-200 border-solid left-[1753px] size-[113.862px] top-[1013px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
        className="absolute border-2 border-slate-200 border-solid left-[120px] size-[151.816px] top-[1105px]"
        data-name="Container"
      />

      {/* Features Section */}
      <div id="features" className="absolute bg-[#0f172b] h-[400px] left-0 overflow-clip top-[627px] w-[1920px]" data-name="Section">
        <div className="absolute h-[400px] left-0 opacity-10 top-0 w-[1528px]" data-name="Container">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
            className="absolute border-2 border-solid border-white left-[25.12px] size-[189.77px] top-[25.12px]"
            data-name="Container"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
            className="absolute border-2 border-solid border-white left-[25.12px] size-[189.77px] top-[25.12px]"
            data-name="Container"
          />
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
            className="absolute border-2 border-solid border-white left-[1348.09px] size-[151.816px] top-[220.09px]"
            data-name="Container"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
            className="absolute border-2 border-solid border-white left-[362.12px] size-[135.765px] top-[180.12px]"
            data-name="Container"
          />
        </div>
        <div className="absolute gap-[24px] grid grid-cols-[repeat(3,_minmax(0px,_1fr))] grid-rows-[repeat(1,_minmax(0px,_1fr))] h-[240px] left-[384px] top-[76px] w-[1152px]" data-name="Container">
          <FeatureCard
            icon="purpose"
            title="Propósito"
            description="Facilitar o acesso à informação de saúde para idosos, oferecendo suporte personalizado e orientações confiáveis de forma simples e acessível."
            index={0}
          />
          <FeatureCard
            icon="focus"
            title="Foco"
            description="Saúde preventiva, lembretes de medicamentos, consultas médicas e orientações sobre bem-estar específicas para a terceira idade."
            index={1}
          />
          <FeatureCard
            icon="usage"
            title="Modo de usar"
            description="Faça perguntas naturalmente, como em uma conversa. O chatbot entende e responde de forma clara, com letras grandes e interface amigável."
            index={2}
          />
        </div>
      </div>

      <ToolsList />

      <TeamStrip />

      <Footer />
    </div>
  );
}