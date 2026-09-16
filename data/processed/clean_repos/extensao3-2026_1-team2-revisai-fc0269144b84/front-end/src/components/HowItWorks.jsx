import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const cards = [
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-[#2d6a4f]" stroke="currentColor" strokeWidth={1.8}>
        <rect x="3" y="4" width="18" height="18" rx="2" />
        <path d="M16 2v4M8 2v4M3 10h18" />
      </svg>
    ),
    title: "Semanas 1, 2 e 3",
    description:
      "Estude novos conteúdos nos dias úteis. No sábado e domingo, revise com flashcards da semana.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-[#2d6a4f]" stroke="currentColor" strokeWidth={1.8}>
        <path d="M12 2a7 7 0 0 1 7 7c0 3-2 5.5-4.5 6.5V17h-5v-1.5C7 14.5 5 12 5 9a7 7 0 0 1 7-7z" />
        <path d="M9.5 21h5M12 17v4" />
      </svg>
    ),
    title: "Semana 4",
    description:
      "Revisão geral de todo o mês. Reforce tudo que foi estudado nas semanas anteriores.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-[#2d6a4f]" stroke="currentColor" strokeWidth={1.8}>
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <circle cx="9" cy="9" r="1.5" fill="currentColor" />
        <circle cx="15" cy="9" r="1.5" fill="currentColor" />
        <path d="M8 15s1.5 2 4 2 4-2 4-2" />
      </svg>
    ),
    title: "IA que gera cards",
    description:
      "Converse com o RevisAI e gere flashcards personalizados em 3 níveis de dificuldade.",
  },
];

export default function HowItWorks() {
  const sectionRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);
  const cardsRef = useRef([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Title reveal
      gsap.from(titleRef.current, {
        y: 60,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: titleRef.current,
          start: "top 85%",
        },
      });

      // Subtitle reveal
      gsap.from(subtitleRef.current, {
        y: 30,
        opacity: 0,
        duration: 0.9,
        delay: 0.15,
        ease: "power3.out",
        scrollTrigger: {
          trigger: subtitleRef.current,
          start: "top 85%",
        },
      });

      // Cards stagger with parallax feel
      gsap.from(cardsRef.current, {
        y: 80,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        stagger: 0.18,
        scrollTrigger: {
          trigger: cardsRef.current[0],
          start: "top 88%",
        },
      });

      // Subtle continuous parallax on cards while scrolling
      cardsRef.current.forEach((card, i) => {
        gsap.to(card, {
          y: -20 * (i + 1),
          ease: "none",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top bottom",
            end: "bottom top",
            scrub: 1.5,
          },
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="bg-[#f5f5ec] py-28 px-6 overflow-hidden"
    >
      <div className="max-w-5xl mx-auto text-center">
        <h2
          ref={titleRef}
          className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4"
        >
          Como funciona?
        </h2>
        <p
          ref={subtitleRef}
          className="text-gray-500 text-lg mb-16"
        >
          Um ciclo de 4 semanas pensado para maximizar a retenção do conteúdo.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {cards.map((card, i) => (
            <div
              key={i}
              ref={(el) => (cardsRef.current[i] = el)}
              className="bg-white rounded-2xl p-8 text-left shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-300"
            >
              <div className="w-12 h-12 bg-[#e8f5ee] rounded-xl flex items-center justify-center mb-5">
                {card.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                {card.title}
              </h3>
              <p className="text-gray-500 text-sm leading-relaxed">
                {card.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}