import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import LyandersonFoto from "../assets/lyanderson.jpeg";
import KayqueFoto from "../assets/kayyque.png";
import LavorFoto from "../assets/lavor.jpeg";
import Ismaael from "../assets/ismael.jpeg";

import Gemini from "../assets/gemini.png";
import Claude from "../assets/claude.png";
import Lovable from "../assets/lovable.jpeg";



gsap.registerPlugin(ScrollTrigger);

const humans = [
  { name: "Lyanderson", role: "QA", initials: "LY", color: "#3a8c64", github: "https://github.com", linkedin: "https://linkedin.com", foto: LyandersonFoto },
  { name: "Kayque", role: "Front-end", initials: "KY", color: "#2d6a4f", github: "https://github.com", linkedin: "https://linkedin.com", foto: KayqueFoto },
  { name: "Ismael", role: "Back-end", initials: "IS", color: "#2d6a4f", github: "https://github.com", linkedin: "https://linkedin.com", foto: Ismaael },
  { name: "Pedro", role: "Engenheiro de IA", initials: "PD", color: "#40916c", github: "https://github.com", linkedin: "https://linkedin.com", foto: LavorFoto },
  { name: "Eduardo", role: "Back-end", initials: "ED", color: "#1b4332", github: "https://github.com", linkedin: "https://linkedin.com", foto: null },
  { name: "Ícaro", role: "Gestor de Projeto", initials: "IC", color: "#1b4332", github: "https://github.com", linkedin: "https://linkedin.com", foto: null },
  { name: "Samuel", role: "Gestor de Projeto", initials: "SM", color: "#52b788", github: "https://github.com", linkedin: "https://linkedin.com", foto: null },
  { name: "Caio Vinícius", role: "Gestor de Projeto", initials: "CV", color: "#3a8c64", github: "https://github.com", linkedin: "https://linkedin.com", foto: null },
];

const ais = [
  { name: "Claude", role: "Consultor Sênior de IA", emoji: "🤖", badge: "Anthropic", joke: "Responde tudo, questiona tudo.", linkedin: "https://linkedin.com/company/anthropic", github: "https://github.com/anthropics", foto: Claude },
  { name: "Gemini", role: "Analista de Dados", emoji: "✨", badge: "Google", joke: "Veio de brinde com o Google One.", linkedin: "https://linkedin.com/company/google", github: "https://github.com/google", foto: Gemini },
  { name: "Lovable", role: "Dev Full-Stack", emoji: "💜", badge: "AI Dev Tool", joke: "Cobra por token. Caro, mas amado.", linkedin: "https://linkedin.com/company/lovable", github: "https://github.com/lovable-dev", foto: Lovable },
];

const GithubIcon = ({ className = "w-4 h-4" }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
  </svg>
);

const LinkedinIcon = ({ className = "w-4 h-4" }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
  </svg>
);

function HumanCard({ member }) {
  const cardRef = useRef(null);
  const onEnter = () => gsap.to(cardRef.current, { y: -10, scale: 1.03, boxShadow: "0 28px 64px rgba(45,106,79,0.18)", duration: 0.35, ease: "power2.out" });
  const onLeave = () => gsap.to(cardRef.current, { y: 0, scale: 1, boxShadow: "0 4px 28px rgba(0,0,0,0.07)", duration: 0.4, ease: "power2.out" });

  return (
    <div
      ref={cardRef}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      className="team-card flex-shrink-0 h-100 w-72 bg-white rounded-3xl p-8 flex flex-col items-center text-center cursor-default select-none"
      style={{ boxShadow: "0 4px 28px rgba(0,0,0,0.07)" }}
    >
      <div
  className="w-28 h-28 rounded-2xl flex items-center justify-center text-white font-bold text-2xl mb-5 relative overflow-hidden"
  style={{ background: `linear-gradient(135deg, ${member.color}, ${member.color}88)` }}
>
  {member.foto ? (
    // Foto real
    <img
      src={member.foto}
      alt={member.name}
      className="absolute inset-0 w-full h-full object-cover"
    />
  ) : (
    // Fallback: SVG de silhueta + iniciais
    <>
      <svg viewBox="0 0 80 80" className="absolute inset-0 w-full h-full opacity-20">
        <circle cx="40" cy="28" r="16" fill="white" />
        <ellipse cx="40" cy="72" rx="26" ry="20" fill="white" />
      </svg>
      <span className="relative z-10 text-2xl font-extrabold tracking-wide">
        {member.initials}
      </span>
    </>
  )}
</div>


      <div className="flex items-center gap-1.5 mb-3">
        <span className="w-2 h-2 rounded-full bg-[#52b788] animate-pulse" />
        <span className="text-[11px] text-[#52b788] font-semibold uppercase tracking-widest">Ativo</span>
      </div>
      <h3 className="font-extrabold text-gray-800 text-xl leading-tight mb-2">{member.name}</h3>
      <span className="text-sm text-gray-400 font-medium px-4 py-1.5 bg-gray-50 rounded-full border border-gray-100 mb-6">{member.role}</span>
      <div className="flex items-center gap-3 mt-auto w-full">
        <a href={member.linkedin} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#0A66C2]/10 text-[#0A66C2] text-xs font-semibold hover:bg-[#0A66C2]/20 transition-colors">
          <LinkedinIcon /> LinkedIn
        </a>
        <a href={member.github} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gray-100 text-gray-600 text-xs font-semibold hover:bg-gray-200 transition-colors">
          <GithubIcon /> GitHub
        </a>
      </div>
    </div>
  );
}

function AiCard({ ai }) {
  const cardRef = useRef(null);
  const onEnter = () => gsap.to(cardRef.current, { y: -10, scale: 1.03, duration: 0.35, ease: "power2.out" });
  const onLeave = () => gsap.to(cardRef.current, { y: 0, scale: 1, duration: 0.4, ease: "power2.out" });

  return (
    <div
      ref={cardRef}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      className="team-card flex-shrink-0 w-72 rounded-3xl p-8 flex flex-col items-center text-center cursor-default select-none relative overflow-hidden"
      style={{ background: "linear-gradient(135deg, #1b4332 0%, #2d6a4f 60%, #40916c 100%)", boxShadow: "0 8px 48px rgba(45,106,79,0.32)" }}
    >
      <div className="absolute -top-8 -right-8 w-36 h-36 rounded-full bg-white/10 blur-2xl pointer-events-none" />
      <div className="absolute -bottom-6 -left-6 w-28 h-28 rounded-full bg-white/5 blur-xl pointer-events-none" />
      <span className="absolute top-4 right-4 text-[10px] font-bold bg-white/15 text-white/80 px-2.5 py-1 rounded-full border border-white/20">{ai.badge}</span>
      
      <div className="w-28 h-28 rounded-2xl bg-white/15 border border-white/20 flex items-center justify-center mb-5 backdrop-blur-sm overflow-hidden">
        {ai.foto ? (
          <img
            src={ai.foto}
            alt={ai.name}
            className="w-full h-full object-contain p-2 rounded-2xl"
          />
        ) : (
          <span className="text-5xl">{ai.emoji}</span>
        )}
      </div>

      <div className="flex items-center gap-1.5 mb-3">
        <span className="w-2 h-2 rounded-full bg-yellow-300 animate-pulse" />
        <span className="text-[11px] text-yellow-300 font-semibold uppercase tracking-widest">IA Membro</span>
      </div>
      <h3 className="font-extrabold text-white text-xl leading-tight mb-2">{ai.name}</h3>
      <span className="text-sm text-white/60 font-medium px-4 py-1.5 bg-white/10 rounded-full border border-white/15 mb-4">{ai.role}</span>
      <p className="text-white/50 text-xs italic leading-snug pt-3 border-t border-white/10 w-full mb-6">"{ai.joke}"</p>
      <div className="flex items-center gap-3 mt-auto w-full">
        <a href={ai.linkedin} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/15 text-white/80 text-xs font-semibold hover:bg-white/25 transition-colors border border-white/20">
          <LinkedinIcon /> LinkedIn
        </a>
        <a href={ai.github} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/10 text-white/70 text-xs font-semibold hover:bg-white/20 transition-colors border border-white/15">
          <GithubIcon /> GitHub
        </a>
      </div>
    </div>
  );
}

export default function Team() {
  const sectionRef = useRef(null);
  const wrapperRef = useRef(null);
  const trackRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);
  const badgeRef = useRef(null);

  useEffect(() => {
    // Animação de entrada do header
    gsap.set([badgeRef.current, titleRef.current, subtitleRef.current], { opacity: 1, y: 0 });
    gsap.from([badgeRef.current, titleRef.current, subtitleRef.current], {
      y: 40,
      opacity: 0,
      duration: 0.9,
      stagger: 0.12,
      ease: "power3.out",
      scrollTrigger: {
        trigger: titleRef.current,
        start: "top 90%",
        toggleActions: "play none none none",
      },
    });

    const mm = gsap.matchMedia();

    mm.add("(min-width: 768px)", () => {
      const track = trackRef.current;
      const wrapper = wrapperRef.current;

      // Distância real até o último card, sem contar padding fantasma
      const getScrollDistance = () => {
        const cards = track.querySelectorAll(".team-card");
        if (!cards.length) return 0;
        const lastCard = cards[cards.length - 1];
        // offsetLeft do card em relação ao track + largura do card + margem direita mínima
        const lastCardEnd = lastCard.offsetLeft + lastCard.offsetWidth + 48;
        return Math.max(0, lastCardEnd - wrapper.offsetWidth);
      };

      gsap.to(track, {
        x: () => -getScrollDistance(),
        ease: "none",
        scrollTrigger: {
          trigger: wrapper,
          start: "top top",
          // end = só o necessário para mover até o último card
          end: () => `+=${getScrollDistance()}`,
          pin: true,
          scrub: 1,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });
    });

    return () => mm.revert();
  }, []);

  return (
    <section ref={sectionRef} className="bg-[#f5f5ec] relative">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ backgroundImage: "radial-gradient(circle, #b7d5c4 1px, transparent 1px)", backgroundSize: "32px 32px" }}
      />

      {/* Header */}
      <div className="px-12 pt-24 pb-8 relative z-10 max-w-3xl mx-auto text-center flex flex-col items-center">
        <span ref={badgeRef} className="inline-flex items-center gap-2 bg-white border border-gray-200 text-gray-500 text-xs px-4 py-1.5 rounded-full shadow-sm mb-5">
          👥 Conheça o time
        </span>
        <h2 ref={titleRef} className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-3 leading-tight">
          As mentes por trás do <span className="text-[#2d6a4f]">RevisAI</span>
        </h2>
        <p ref={subtitleRef} className="text-gray-400 text-lg">
          Humanos (e algumas IAs) trabalhando juntos para te fazer aprender mais.
        </p>
      </div>

      {/* Área de scroll horizontal */}
      <div ref={wrapperRef} className="relative overflow-hidden" style={{ height: "520px" }}>
        {/* Fades nas bordas */}
        <div className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none" style={{ background: "linear-gradient(to right, #f5f5ec, transparent)" }} />
        <div className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none" style={{ background: "linear-gradient(to left, #f5f5ec, transparent)" }} />

        {/* Track — só os cards definem a largura, sem pr extra */}
        <div
          ref={trackRef}
          className="absolute top-1/2 -translate-y-1/2 flex items-center gap-6 pl-12 will-change-transform"
        >
          {humans.map((m) => (
            <HumanCard key={m.name} member={m} />
          ))}

          {/* Divisor */}
          <div className="flex-shrink-0 flex flex-col items-center justify-center px-8 gap-4 h-80">
            <div className="flex-1 w-px bg-gradient-to-b from-transparent via-[#2d6a4f]/30 to-transparent" />
            <span className="text-[11px] font-bold text-[#2d6a4f]/50 uppercase tracking-widest whitespace-nowrap"
              style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}>
              + IAs do time
            </span>
            <div className="flex-1 w-px bg-gradient-to-b from-transparent via-[#2d6a4f]/30 to-transparent" />
          </div>

          {ais.map((ai) => (
            <AiCard key={ai.name} ai={ai} />
          ))}
        </div>
      </div>

      {/* Hint de scroll */}
      <div className="px-12 py-6 flex items-center gap-2 text-gray-300 relative z-10">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-4 h-4">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
        <span className="text-xs font-medium">Role para conhecer o time</span>
      </div>
    </section>
  );
}